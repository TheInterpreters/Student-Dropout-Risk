"""Local what-if mode for the research interface: re-predict an edited validation student.

Started by `python scripts/launch_interface.py --what-if`. It serves the interface page on
http://127.0.0.1:<port>/ and answers POST /api/predict with a new prediction from the frozen final
model (hash-checked against artifacts/final_test.lock). Nothing is retrained, nothing is written to
disk, and the test split is never read.

Rules:
- Only saved validation students can be edited; the practice case and study cases are refused.
- Only first-semester results and fee/debt/scholarship status can change. Demographic and family
  fields are fixed so the tool cannot be used to ask "what if this student were a different gender,
  age or nationality".
- Values must be consistent (passed <= enrolled and <= evaluations, grade 0 when nothing passed)
  and inside the range seen in the train/validation data. Invalid input is rejected, never adjusted.
- Rank is recomputed against the other 543 frozen validation scores, which stay fixed.
- Results carry no stability audit or recourse check and are model responses, not advice.
"""
from __future__ import annotations

import json
import math
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import sys
import threading

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "forms"))

UNIT_FIELDS = ("curricular_units_1st_sem_enrolled", "curricular_units_1st_sem_evaluations",
               "curricular_units_1st_sem_approved", "curricular_units_1st_sem_without_evaluations")
GRADE_FIELD = "curricular_units_1st_sem_grade"
BINARY_FIELDS = ("tuition_fees_up_to_date", "debtor", "scholarship_holder")
EDITABLE = UNIT_FIELDS + (GRADE_FIELD,) + BINARY_FIELDS
MAX_BODY = 4096


def validate_edits(edits, bounds):
    """Return cleaned numeric edits or raise ValueError with a readable reason."""
    if not isinstance(edits, dict) or set(edits) != set(EDITABLE):
        raise ValueError("send exactly these fields: " + ", ".join(EDITABLE))
    clean = {}
    for field in UNIT_FIELDS:
        value = edits[field]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value != int(value):
            raise ValueError(f"{field} must be a whole number")
        low, high = bounds[field]
        if not low <= value <= high:
            raise ValueError(f"{field} must be between {low:g} and {high:g} (range in the development data)")
        clean[field] = int(value)
    grade = edits[GRADE_FIELD]
    if isinstance(grade, bool) or not isinstance(grade, (int, float)) or not math.isfinite(grade):
        raise ValueError("grade must be a number")
    for field in BINARY_FIELDS:
        if edits[field] not in (0, 1) or isinstance(edits[field], bool):
            raise ValueError(f"{field} must be 0 or 1")
        clean[field] = int(edits[field])
    enrolled, evaluations, approved, missing = (clean[f] for f in UNIT_FIELDS)
    if approved > enrolled:
        raise ValueError("units passed cannot exceed units enrolled")
    if approved > evaluations:
        raise ValueError("units passed cannot exceed evaluations taken")
    if missing > enrolled:
        raise ValueError("units with no evaluation cannot exceed units enrolled")
    if approved == 0 and grade != 0:
        raise ValueError("average grade must be 0 when no units were passed (dataset convention)")
    low, high = bounds[GRADE_FIELD]
    if approved > 0 and not low <= grade <= high:
        raise ValueError(f"average grade of passed units must be between {low:g} and {high:g} "
                         "(range in the development data)")
    clean[GRADE_FIELD] = float(grade)
    return clean


def development_bounds(*frames):
    """Allowed ranges: what the train and validation splits contain (never the test split)."""
    import pandas as pd
    data = pd.concat(frames)
    bounds = {f: (float(data[f].min()), float(data[f].max())) for f in UNIT_FIELDS}
    passed = data.loc[data["curricular_units_1st_sem_approved"] > 0, GRADE_FIELD]
    bounds[GRADE_FIELD] = (float(passed.min()), float(passed.max()))
    return bounds


def cohort_rank(probability, own_position, cohort, positions):
    """Rank among the cohort with this student's score replaced; ties by validation position."""
    rank = 1
    for other, position in zip(cohort, positions):
        if position == own_position:
            continue
        if other > probability or (other == probability and position < own_position):
            rank += 1
    return rank


class WhatIfEngine:
    """Holds the frozen model, validation frame and frozen cohort scores."""

    def __init__(self, refused_ids, n_flag):
        import numpy as np
        from scripts.build_demo_card import load_bundle
        from src.evaluation import development_frames, load_protocol
        from src.modeling import prepare_tfm_frame
        self.np = np
        self.bundle, self.lock = load_bundle()  # raises unless the hash matches the lock
        self.train, self.validation, self.columns = development_frames("validation")
        if list(self.columns) != self.bundle["columns"]:
            raise ValueError("validation features do not match the saved model")
        self.model = self.bundle["model"]
        self.protocol = load_protocol()
        self.prepare = prepare_tfm_frame
        print("What-if: scoring the validation cohort with the frozen model (about 20 s)...")
        frame = prepare_tfm_frame(self.validation, self.columns)
        self.cohort = self.model.predict_proba(frame)[:, 1]
        self.cached = self._enable_context_cache(frame)
        self.positions = list(range(len(self.validation)))
        self.n_flag = n_flag
        self.refused = set(refused_ids)
        self.bounds = development_bounds(self.train, self.validation)
        self.lock_obj = threading.Lock()
        self.background = None

    def _enable_context_cache(self, frame):
        """Speed up later predictions about 100x with TabICL's own key-value cache.

        TabICL has no weights trained on this dataset: every prediction re-reads all training
        students as context, which takes about 9 s on CPU even for one student. The cache stores
        that context once, in memory only (the saved model file is not changed). It is used only
        if it reproduces the frozen cohort: scores within 1e-4 and an identical ranking.
        """
        np = self.np
        try:
            self.model.cache_mode_ = "kv"
            self.model._build_kv_cache()
            fast = self.model.predict_proba(frame)[:, 1]
        except Exception as error:  # fall back to the slow, uncached path
            self.model.model_kv_cache_ = None
            print(f"What-if: context cache unavailable ({error}); predictions take about 10 s.")
            return False
        order = lambda scores: np.lexsort((np.arange(len(scores)), -scores))
        gap = float(np.abs(fast - self.cohort).max())
        if gap > 1e-4 or not np.array_equal(order(fast), order(self.cohort)):
            self.model.model_kv_cache_ = None
            print(f"What-if: context cache did not reproduce the frozen cohort (max gap {gap:.1e}); "
                  "using the uncached path (about 10 s per prediction).")
            return False
        print(f"What-if: context cache on (matches frozen cohort within {gap:.1e}, identical ranking).")
        return True

    def position_of(self, source_row_id):
        ids = self.validation["source_row_id"].to_numpy(int)
        hits = self.np.flatnonzero(ids == source_row_id)
        if len(hits) != 1:
            raise ValueError("not a validation student")
        position = int(hits[0])
        if position == 0 or source_row_id in self.refused:
            raise ValueError("this student is a study or practice case and cannot be edited")
        return position

    def predict(self, source_row_id, edits, explain=False):
        from src.modeling import add_first_semester_features
        position = self.position_of(int(source_row_id))
        clean = validate_edits(edits, self.bounds)
        row = self.validation.iloc[[position]].copy()
        recorded = {f: float(row[f].iloc[0]) for f in EDITABLE}
        changed = [f for f in EDITABLE if abs(float(clean[f]) - recorded[f]) > 1e-6]
        for field in changed:  # untouched fields keep their exact stored value
            row[field] = clean[field]
        row = add_first_semester_features(row)
        with self.lock_obj:
            if changed:
                probability = float(self.model.predict_proba(self.prepare(row, self.columns))[:, 1][0])
            else:  # nothing edited: return the frozen score exactly
                probability = float(self.cohort[position])
            bars = self.explain(row) if explain else None
        rank = cohort_rank(probability, position, self.cohort, self.positions)
        original = float(self.cohort[position])
        return {"probability": probability, "rank": rank, "flagged": rank <= self.n_flag,
                "recorded_probability": original,
                "recorded_rank": cohort_rank(original, position, self.cohort, self.positions),
                "changed": changed,
                "bars": bars}

    def explain(self, row):
        from forms import case_pack as cp
        from src.explanations import (aggregate_shap_by_group, permutation_shap_values,
                                      semantic_feature_groups)
        if self.background is None:
            self.background = self.prepare(self.train, self.columns).sample(n=25, random_state=42)
        values = permutation_shap_values(self.model.predict_proba, self.background,
                                         self.prepare(row, self.columns),
                                         max_evals=self.protocol["shap"]["max_evals"], seed=42)
        groups = aggregate_shap_by_group(values.values[0], self.columns,
                                         semantic_feature_groups(self.columns)).head(5)
        labels = cp.bar_labels()
        return [{"label": labels[g.feature_group], "value": float(g.signed_shap)}
                for g in groups.itertuples()]


def make_handler(page_bytes, engine, host):
    class Handler(BaseHTTPRequestHandler):
        def _send(self, code, body, kind="application/json"):
            data = body if isinstance(body, bytes) else json.dumps(body).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", kind + "; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def _host_ok(self):
            # Blocks DNS-rebinding style access from other sites.
            return self.headers.get("Host") == host

        def do_GET(self):
            if not self._host_ok():
                return self._send(403, {"error": "forbidden"})
            if self.path in ("/", "/index.html") or self.path.startswith("/#"):
                return self._send(200, page_bytes, "text/html")
            if self.path == "/api/status":
                return self._send(200, {"what_if": True, "bounds": engine.bounds, "fast": engine.cached})
            self._send(404, {"error": "not found"})

        def do_POST(self):
            try:
                length = int(self.headers.get("Content-Length") or 0)
            except ValueError:
                length = -1
            if not 0 < length <= MAX_BODY:
                self.close_connection = True
                return self._send(413, {"error": "request missing or too large"})
            raw = self.rfile.read(length)  # always read the body so the reply is not cut off
            if not self._host_ok() or self.path != "/api/predict":
                return self._send(403, {"error": "forbidden"})
            if self.headers.get("Content-Type", "").split(";")[0] != "application/json":
                return self._send(415, {"error": "JSON only"})
            try:
                body = json.loads(raw)
                result = engine.predict(body["source_row_id"], body["edits"], bool(body.get("explain")))
            except (ValueError, KeyError, TypeError) as error:
                return self._send(400, {"error": str(error)})
            self._send(200, result)

        def log_message(self, *args):  # do not log request contents
            pass

    return Handler


class QuietHTTPServer(HTTPServer):
    """Ignore browsers closing a connection early (tab closed, reload); report other errors."""

    def handle_error(self, request, client_address):
        import sys
        if isinstance(sys.exc_info()[1], (ConnectionAbortedError, ConnectionResetError, BrokenPipeError)):
            return
        super().handle_error(request, client_address)


def serve(page_path, refused_ids, n_flag, port=8765, open_browser=True):
    import webbrowser
    host = f"127.0.0.1:{port}"
    try:
        server = QuietHTTPServer(("127.0.0.1", port), None)
    except OSError:
        raise SystemExit(f"Port {port} is already in use, probably by an older what-if server serving an "
                         "outdated page. Close that terminal (or stop the process), or use --port 8766.")
    model_path = ROOT / "data" / "final_evaluation" / "selected_model.joblib"
    if not model_path.is_file():
        server.server_close()
        raise SystemExit("What-if mode needs the private frozen model file data/final_evaluation/selected_model.joblib "
                         "(git-ignored; ask the model owner). The saved page still works without it: "
                         "python scripts/launch_interface.py")
    engine = WhatIfEngine(refused_ids, n_flag)
    server.RequestHandlerClass = make_handler(Path(page_path).read_bytes(), engine, host)
    url = f"http://{host}/"
    print(f"What-if mode running at {url}  (local only; press Ctrl+C to stop)")
    if open_browser:
        webbrowser.open(url + "#student=174")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
