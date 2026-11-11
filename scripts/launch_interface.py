"""Build and open the local research interface (proposal section 5.6, reduced version).

A single self-contained HTML page that shows saved, precomputed results for validation students:
outreach status and cohort rank, the five largest grouped SHAP contributions, that student's
explanation-stability warning, the debtor/tuition recourse check (model behaviour, not advice) and an
audit panel. The saved page runs no model and needs no server or network; the optional --what-if mode
adds local re-prediction with the frozen model (scripts/whatif_server.py). The test split is never read.

Inputs (all saved evidence):
    W1_analysis/03_Full_Audit/Cases/case_*.json   544 validation cases (refit verified against the
                                                   frozen model: artifacts/w1_refit_identity.json)
    eda_uci_data/data/dropout_data.csv            public UCI profile values
    artifacts/final_test.lock, config protocol    versions for the audit panel
The study practice case (validation position 0) and any study case are refused.

Usage (repo root, .venv-core):
    python scripts/launch_interface.py              # build interface/student_support_demo.html and open it
    python scripts/launch_interface.py --no-open    # build only
    python scripts/launch_interface.py --what-if    # also allow edits re-predicted by the frozen model
                                                    # (local server on 127.0.0.1; see whatif_server.py)

Not used in the human study (that ran on Google Forms) and not tested with users.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import math
from pathlib import Path
import sys
import webbrowser

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "forms"))

INTERFACE_VERSION = "1.0"
CASES = ROOT / "W1_analysis" / "03_Full_Audit" / "Cases"
RAW = ROOT / "eda_uci_data" / "data" / "dropout_data.csv"
STUDY_LOOKUP = ROOT / "data" / "study_cases" / "private_lookup_study.json"
OUT = ROOT / "interface" / "student_support_demo.html"
PRACTICE_POSITION = 0
CAPACITY = 0.20
WARNING_LEVEL = 0.80
RECOURSE_STATUSES = {"not_flagged", "no_recourse", "recourse_found"}
STABILITY_KINDS = {"seed", "background", "perturbation"}
EDITABLE = ("curricular_units_1st_sem_enrolled", "curricular_units_1st_sem_evaluations",
            "curricular_units_1st_sem_approved", "curricular_units_1st_sem_without_evaluations",
            "curricular_units_1st_sem_grade", "tuition_fees_up_to_date", "debtor", "scholarship_holder")
CHANGE_LABELS = {"debtor": "debt to the university resolved",
                 "tuition_fees_up_to_date": "tuition fees brought up to date"}


def _number(value, name, low=None, high=None):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name} is not a finite number")
    if (low is not None and value < low) or (high is not None and value > high):
        raise ValueError(f"{name}={value} is out of range")
    return float(value)


def validate_case(case, labels):
    """Return a cleaned case or raise; never silently repairs a field."""
    for key in ("source_row_id", "validation_position", "predicted_probability", "flagged",
                "baseline_group_contributions", "stability", "recourse"):
        if key not in case:
            raise ValueError(f"case missing field: {key}")
    sid = case["source_row_id"]
    if not isinstance(sid, int) or isinstance(sid, bool) or sid < 0:
        raise ValueError("invalid source_row_id")
    if case["flagged"] not in (0, 1):
        raise ValueError(f"case {sid}: flagged must be 0 or 1")
    contributions = case["baseline_group_contributions"]
    if len(contributions) != 5:
        raise ValueError(f"case {sid}: expected five contributions")
    bars = []
    for item in contributions:
        group = item.get("feature_group")
        if group not in labels:
            raise ValueError(f"case {sid}: unknown feature group {group!r}")
        bars.append({"label": labels[group],
                     "members": [m.strip() for m in str(item.get("members", "")).split(",") if m.strip()],
                     "value": _number(item.get("signed_shap"), f"case {sid} contribution", -1, 1)})
    stability = {}
    for row in case["stability"]:
        kind = row.get("variation")
        if kind not in STABILITY_KINDS or kind in stability:
            raise ValueError(f"case {sid}: invalid stability variation {kind!r}")
        stability[kind] = _number(row.get("top_5_overlap"), f"case {sid} overlap", 0, 1)
    if set(stability) != STABILITY_KINDS:
        raise ValueError(f"case {sid}: stability must cover seed, background and perturbation")
    recourse = []
    for row in case["recourse"]:
        status = row.get("status")
        if status not in RECOURSE_STATUSES:
            raise ValueError(f"case {sid}: unknown recourse status {status!r}")
        if status == "recourse_found":
            changes = [c.strip() for c in str(row.get("changed_features", "")).split(",")]
            if not changes or any(c not in CHANGE_LABELS for c in changes):
                raise ValueError(f"case {sid}: recourse changes outside debtor/tuition")
            recourse.append({"changes": [CHANGE_LABELS[c] for c in changes],
                             "rank_after": int(row["capacity_rank"])})
        else:
            recourse.append({"status": status})
    if case["flagged"] and not recourse:
        raise ValueError(f"case {sid}: flagged case has no recourse record")
    return {"source_row_id": sid, "position": int(case["validation_position"]),
            "probability": _number(case["predicted_probability"], f"case {sid} probability", 0, 1),
            "flagged": int(case["flagged"]), "bars": bars, "stability": stability,
            "recourse": recourse,
            "topics": [str(t) for t in case.get("support_topics_for_human_review", [])]}


def rank_cases(cases):
    """Cohort rank by probability (ties by validation position), matching capacity_predictions."""
    ordered = sorted(cases, key=lambda c: (-c["probability"], c["position"]))
    n_flag = max(1, math.floor(len(cases) * CAPACITY))
    for rank, case in enumerate(ordered, start=1):
        case["rank"] = rank
        if (rank <= n_flag) != bool(case["flagged"]):
            raise ValueError(f"case {case['source_row_id']}: saved flag disagrees with the 20% rank rule")
    return n_flag


def study_source_ids():
    if not STUDY_LOOKUP.is_file():
        return set()
    lookup = json.loads(STUDY_LOOKUP.read_text(encoding="utf-8"))
    return {int(value["source_row_id"]) for value in lookup.values()}


def load_cases(folder, labels, refused_ids=frozenset()):
    files = sorted(Path(folder).glob("case_*.json"))
    if not files:
        raise ValueError("no saved validation cases found")
    cases = [validate_case(json.loads(path.read_text(encoding="utf-8")), labels) for path in files]
    if len({c["source_row_id"] for c in cases}) != len(cases):
        raise ValueError("duplicate validation cases")
    n_flag = rank_cases(cases)  # rank on the whole cohort before hiding any case
    shown = [c for c in cases if c["position"] != PRACTICE_POSITION
             and c["source_row_id"] not in refused_ids]
    cohort = [round(c["probability"], 4) for c in sorted(cases, key=lambda c: c["rank"])]
    return sorted(shown, key=lambda c: c["rank"]), len(cases), n_flag, cohort


def profile(raw_row):
    from forms import labels as lb
    from src.modeling import clean_column_name
    sections = []
    for heading, fields in lb.GROUPS:
        sections.append({"heading": heading,
                         "rows": [[label, lb.format_value(kind, field, raw_row[field]), clean_column_name(field)]
                                  for field, label, kind in fields]})
    return sections


def audit_info(n_cases, n_flag):
    from src.evaluation import load_protocol
    lock = json.loads((ROOT / "artifacts" / "final_test.lock").read_text(encoding="utf-8"))
    identity = json.loads((ROOT / "artifacts" / "w1_refit_identity.json").read_text(encoding="utf-8"))
    if identity.get("model_bundle_sha256") != lock.get("model_bundle_sha256"):
        raise ValueError("W1 refit identity check refers to a different model bundle")
    protocol = load_protocol()
    return {"interface_version": INTERFACE_VERSION,
            "protocol_version": protocol["protocol_version"],
            "model": "TabICL 2.2.0, 4 estimators (frozen settings)",
            "model_bundle_sha256": lock["model_bundle_sha256"][:16] + "…",
            "split": f"validation only, seed {protocol['seed']} (test split not read)",
            "cohort": f"{n_cases} validation students, {n_flag} flagged at 20% capacity",
            "scores": ("W1 refit with frozen settings; matches the frozen model within "
                       f"{identity['max_abs_probability_difference']:.5f}, "
                       f"{identity['refit_flags'] - identity['flag_disagreements']}/{identity['frozen_flags']} "
                       "identical flags"),
            "explanations": "permutation SHAP, 25 training background rows, 67 evaluations, grouped"}


def build(out=OUT, cases_folder=CASES, raw_path=RAW):
    from forms import case_pack as cp
    from src.modeling import clean_column_name
    cases, n_cases, n_flag, cohort = load_cases(cases_folder, cp.bar_labels(), study_source_ids())
    with open(raw_path, newline="", encoding="utf-8") as stream:
        raw = [{k.strip(): v.strip() for k, v in row.items()} for row in csv.DictReader(stream)]
    for case in cases:
        case["profile"] = profile(raw[case["source_row_id"]])
        cleaned = {clean_column_name(k): v for k, v in raw[case["source_row_id"]].items()}
        case["edit"] = {field: float(cleaned[field]) for field in EDITABLE}
        del case["position"]
    payload = {"cases": cases, "audit": audit_info(n_cases, n_flag), "warning_level": WARNING_LEVEL,
               "n_cases": n_cases, "n_flag": n_flag, "cohort": cohort}
    data = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    page = TEMPLATE.replace("__DATA__", data).replace(
        "__VERSION__", html.escape(INTERFACE_VERSION))
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    digest = hashlib.sha256(page.encode("utf-8")).hexdigest()
    print(f"Interface: {len(cases)} validation students -> {out} (sha256 {digest[:12]})")
    return out


TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Student Support Demo</title>
<style>
:root{--bg:#f7f7f5;--panel:#fff;--ink:#1d1d1b;--muted:#5c5c58;--line:#d9d9d4;--up:#c2410c;--down:#1d4ed8;
--warn-bg:#fff4e0;--warn:#8a4b00;--ok:#166534;--flag:#b42318;--what:#6d28d9}
@media (prefers-color-scheme:dark){:root{--bg:#161615;--panel:#21211f;--ink:#ececea;--muted:#a3a39e;--line:#3a3a37;
--up:#fb923c;--down:#60a5fa;--warn-bg:#3a2a10;--warn:#f5c26b;--ok:#4ade80;--flag:#f87171;--what:#c4b5fd}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif}
header{padding:16px;border-bottom:1px solid var(--line);background:var(--panel)}
header h1{font-size:18px;margin:0 0 4px}
header p{margin:0;color:var(--muted);font-size:13px}
.controls{display:flex;flex-wrap:wrap;gap:12px;align-items:center;margin-top:12px}
.controls label{display:flex;align-items:center;gap:6px;min-width:0;max-width:100%}
select{font:inherit;padding:6px 8px;min-width:0;width:340px;max-width:100%;background:var(--panel);color:var(--ink);border:1px solid var(--line);border-radius:6px}
main{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.4fr);gap:16px;padding:16px;max-width:1200px;margin:0 auto}
@media (max-width:820px){main{grid-template-columns:1fr}}
section{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:14px 16px}
h2{font-size:15px;margin:0 0 10px}
.col{display:flex;flex-direction:column;gap:16px;min-width:0}
table{width:100%;border-collapse:collapse;font-size:13px}
td{padding:3px 0;vertical-align:top;overflow-wrap:anywhere}td:first-child{color:var(--muted);padding-right:12px;width:48%}
.sub{font-weight:600;padding-top:10px;color:var(--ink)}
.status{font-size:20px;font-weight:700}.flag{color:var(--flag)}.noflag{color:var(--ok)}
.muted{color:var(--muted);font-size:13px}
.bar{display:grid;grid-template-columns:minmax(0,1.3fr) minmax(0,1fr) 56px;gap:8px;align-items:center;margin:6px 0;font-size:13px}
.track{position:relative;height:14px;background:linear-gradient(var(--line),var(--line)) center/1px 100% no-repeat}
.fill{position:absolute;top:0;height:14px;border-radius:2px}
.num{text-align:right;font-variant-numeric:tabular-nums}
.warn{background:var(--warn-bg);color:var(--warn);border-radius:6px;padding:10px 12px;font-size:13px}
svg.chart{width:100%;height:auto;display:block;margin-top:6px;overflow:visible}
svg.chart text{font:13px system-ui,sans-serif;fill:var(--muted)}
.legend{font-size:12px;color:var(--muted);margin-top:4px}
.form{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:8px 14px;margin:8px 0}
.form label{display:flex;flex-direction:column;gap:3px;font-size:12px;color:var(--muted)}
.form input,.form select{font:inherit;font-size:14px;padding:5px 7px;width:100%;background:var(--panel);color:var(--ink);border:1px solid var(--line);border-radius:6px}
.buttons{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-top:6px}
button{font:inherit;font-size:14px;padding:6px 14px;border-radius:6px;border:1px solid var(--what);background:var(--what);color:var(--panel);cursor:pointer}
button.secondary{background:transparent;color:var(--ink);border-color:var(--line)}button:disabled{opacity:.5;cursor:wait}
.result{border-left:3px solid var(--what);padding:6px 10px;margin-top:10px;font-size:14px}
.error{color:var(--flag);font-size:13px;margin-top:8px}
.intro{max-width:1200px;margin:16px auto 0;padding:0 16px}
.intro details{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:12px 16px;font-size:14px}
.intro summary,details summary{cursor:pointer;font-weight:600}
.intro ol{margin:10px 0;padding-left:20px}.intro li{margin:4px 0}.intro p{margin:8px 0}
code{font-size:12px;background:var(--bg);padding:1px 4px;border-radius:4px}
.nav{display:flex;gap:6px}.nav button{padding:5px 10px}
.axis{display:flex;justify-content:space-between;font-size:12px}.axisrow{margin-bottom:0}
.sym{font-weight:700}
.tip{position:fixed;z-index:10;pointer-events:none;max-width:280px;background:var(--ink);color:var(--panel);font-size:12px;line-height:1.4;padding:7px 9px;border-radius:6px;box-shadow:0 2px 8px rgba(0,0,0,.25);opacity:0;transition:opacity .1s}
.tip.on{opacity:1}
tr.hl td{background:color-mix(in srgb,var(--up) 14%,transparent)}tr.hl td:first-child{color:var(--ink);font-weight:600}
.bar{cursor:default;border-radius:4px}.bar:hover,.bar:focus{background:color-mix(in srgb,var(--line) 45%,transparent);outline:none}
.info{display:inline-block;margin-left:6px;width:17px;height:17px;line-height:17px;text-align:center;border-radius:50%;font-size:11px;font-weight:700;color:var(--muted);border:1px solid var(--line);cursor:help;vertical-align:1px}
.kbd{font-size:11px;color:var(--muted)}
.steps{margin:4px 0 10px;padding-left:20px;font-size:13px;color:var(--muted)}.steps li{margin:2px 0}
.field{position:relative}.field>span:first-child{color:var(--ink);font-weight:600;font-size:12.5px}
.inwrap{display:flex;align-items:center;gap:6px}.inwrap input,.inwrap select{flex:1;min-width:0}
.unit{font-size:12px;color:var(--muted);white-space:nowrap}
.hint{font-size:11.5px;color:var(--muted)}.hint.err{color:var(--flag)}
.field.changed input,.field.changed select{border-color:var(--what);box-shadow:0 0 0 1px var(--what)}
.field.invalid input,.field.invalid select{border-color:var(--flag);box-shadow:0 0 0 1px var(--flag)}
button.small{font-size:12.5px;padding:4px 10px}
ul{margin:6px 0 0;padding-left:18px;font-size:13px}
dl{display:grid;grid-template-columns:auto 1fr;gap:4px 12px;font-size:12px;margin:0}dt{color:var(--muted)}dd{margin:0;word-break:break-word}
</style>
</head>
<body>
<header>
<h1>Student support prioritisation: research demonstration</h1>
<p>A research demo of how a dropout-risk model could help staff decide whom to offer support after the first semester. Public data (UCI, Portugal); not for real decisions.</p>
<div class="controls">
<label>Student <select id="pick" aria-label="Choose a student"></select></label>
<span class="nav"><button class="secondary" id="prev" title="Previous student in the list">◀ Previous</button><button class="secondary" id="next" title="Next student in the list">Next ▶</button></span>
<label>Example <select id="examples" aria-label="Jump to an example"><option value="">Choose an example…</option></select></label>
<label><input type="checkbox" id="only"> flagged only</label>
<span class="kbd">543 of 4,424 students shown<span class="info" tabindex="0" data-tip="The dataset has 4,424 students. 794 were still enrolled with no final outcome, so the model was built on the other 3,630 (dropped out or graduated): 2,541 for training, 544 for checking (validation) and 545 for the one-time final test. This page shows the 544 validation students, minus one used as the study's practice example. Training students are left out because the model has already seen them, test students because the final test may be run only once, and enrolled students because their outcome is unknown." aria-label="The dataset has 4,424 students. 794 were still enrolled with no final outcome, so the model was built on the other 3,630 (dropped out or graduated): 2,541 for training, 544 for checking (validation) and 545 for the one-time final test. This page shows the 544 validation students, minus one used as the study's practice example. Training students are left out because the model has already seen them, test students because the final test may be run only once, and enrolled students because their outcome is unknown.">i</span> · ← → keys move between students</span>
</div>
</header>
<div class="intro"><details id="about" open><summary>How to read this page (first time? start here)</summary>
<ol>
<li><strong>Pick a student</strong> with the list, the arrows, or an example. Each is a real but anonymous record from the public dataset.</li>
<li><strong>Section 1</strong> says whether the model would put this student on the support-contact list. Staff can contact only about 1 in 5 students, so the model ranks everyone and flags the top 20%.</li>
<li><strong>Section 2</strong> shows which information pushed the model's estimate up or down for this student.</li>
<li><strong>Section 3</strong> shows how much to trust that list of reasons: the same calculation was repeated 10 times with small changes.</li>
<li><strong>Section 4</strong> asks whether clearing a fee or debt record would change the flag. <strong>Section 5</strong> lets you try your own changes (only when started with <code>--what-if</code>).</li>
</ol>
<p class="muted">Terms: <strong>estimate</strong> = the model's dropout probability, a score rather than a certainty. <strong>Rank</strong> = position from highest to lowest estimate among the 544. <strong>Flagged</strong> = in the top 108 (20%). <strong>Contribution</strong> = how much one group of information moved the estimate (SHAP); it shows association, not cause.</p>
</details></div>
<main>
<div class="col">
<section><h2>Profile after the first semester</h2><table id="profile"></table></section>
</div>
<div class="col">
<section><h2>1. Would this student be flagged for a support contact?<span class="info" tabindex="0" data-tip="Staff can contact about 1 in 5 students. The model ranks all 544 students by estimated dropout risk and flags the top 108. Hover over the curve to see any rank; click it to open that student." aria-label="Staff can contact about 1 in 5 students. The model ranks all 544 students by estimated dropout risk and flags the top 108. Hover over the curve to see any rank; click it to open that student.">i</span></h2><div id="status"></div></section>
<section><h2>2. Why: what moved the estimate most<span class="info" tabindex="0" data-tip="Grouped SHAP: each bar is how much a group of information moved this student's estimate compared with 25 typical training students. Hover over a bar to see what it includes; the matching profile rows light up." aria-label="Grouped SHAP: each bar is how much a group of information moved this student's estimate compared with 25 typical training students. Hover over a bar to see what it includes; the matching profile rows light up.">i</span></h2>
<p class="muted">The five groups of information with the biggest effect, compared with a typical student. These are patterns the model learned, not causes of dropout.</p>
<div class="bar axisrow"><div></div><div class="axis"><span style="color:var(--down)">◀ lowered</span><span style="color:var(--up)">raised ▶</span></div><div></div></div>
<div id="bars"></div></section>
<section><h2>3. How much to trust these reasons<span class="info" tabindex="0" data-tip="The explanation was recalculated 10 times with a different random start, a different comparison group of students, and tiny grade changes. 0.80 or more of the top five staying the same counts as stable." aria-label="The explanation was recalculated 10 times with a different random start, a different comparison group of students, and tiny grade changes. 0.80 or more of the top five staying the same counts as stable.">i</span></h2><div id="reliability"></div></section>
<section><h2>4. Would clearing fees or debt change the flag?<span class="info" tabindex="0" data-tip="Only fee and debt status were treated as things that could realistically change before the next semester. Other students' scores stay fixed. This describes the model, not what paying would do for the student." aria-label="Only fee and debt status were treated as things that could realistically change before the next semester. Other students' scores stay fixed. This describes the model, not what paying would do for the student.">i</span></h2><p class="muted">Shows how the model reacts, not advice to the student.</p><div id="recourse"></div></section>
<section><h2>5. Try a change (what-if)<span class="info" tabindex="0" data-tip="Runs the frozen model again on an edited copy of this student. Only first-semester results and fee/scholarship status can be changed. Needs the page to be started with --what-if." aria-label="Runs the frozen model again on an edited copy of this student. Only first-semester results and fee/scholarship status can be changed. Needs the page to be started with --what-if.">i</span></h2><div id="whatif"></div></section>
<section><h2>Read before acting</h2><ul>
<li>The flag means "in this cohort's top 20% of estimated risk" (outreach capacity), not a fixed cut-off.</li>
<li>A model estimate for adviser review, not a decision or diagnosis. Outreach should be voluntary support.</li>
<li>Trained and checked on one Portuguese dataset; not validated for any other institution.</li>
<li>Enrolled students (outcome unknown) were excluded from training and this cohort.</li>
</ul></section>
<section><details><summary><strong>Technical details for reviewers</strong></summary><dl id="audit" style="margin-top:10px"></dl></details></section>
</div>
</main>
<div class="tip" id="tip" role="tooltip"></div>
<script id="data" type="application/json">__DATA__</script>
<script>
const D = JSON.parse(document.getElementById("data").textContent);
const $ = id => document.getElementById(id);
function el(tag, text, cls){const e=document.createElement(tag); if(text!==undefined) e.textContent=text; if(cls) e.className=cls; return e;}
const NS="http://www.w3.org/2000/svg";
function sv(tag,attrs,parent){const e=document.createElementNS(NS,tag); for(const k in attrs) e.setAttribute(k,attrs[k]); if(parent) parent.appendChild(e); return e;}
function svText(parent,x,y,str,anchor){const e=sv("text",{x,y,"text-anchor":anchor||"start"},parent); e.textContent=str; return e;}
const TIP=document.getElementById("tip");
function tipShow(text,x,y){TIP.textContent=text; TIP.style.whiteSpace='pre-line'; TIP.classList.add("on");
  const w=TIP.offsetWidth,h=TIP.offsetHeight; let left=x+14, top=y+14;
  if(left+w>innerWidth-8) left=x-w-14; if(top+h>innerHeight-8) top=y-h-14;
  TIP.style.left=Math.max(8,left)+"px"; TIP.style.top=Math.max(8,top)+"px";}
function tipHide(){TIP.classList.remove("on");}
function tipFor(node,text){node.addEventListener("mousemove",e=>tipShow(typeof text==="function"?text():text,e.clientX,e.clientY));
  node.addEventListener("mouseleave",tipHide);
  node.addEventListener("focus",()=>{const r=node.getBoundingClientRect(); tipShow(typeof text==="function"?text():text,r.left,r.bottom);});
  node.addEventListener("blur",tipHide);}
document.querySelectorAll("[data-tip]").forEach(n=>tipFor(n,n.dataset.tip));
const BY_RANK={}; for(const c of D.cases) BY_RANK[c.rank]=c;
const FIELD_LABEL={first_semester_pass_rate:"Pass rate (units passed ÷ enrolled)",first_semester_no_enrollment:"No units enrolled",first_semester_no_evaluations:"No evaluations taken"};
for(const c of D.cases.slice(0,1)) for(const s of c.profile) for(const r of s.rows) FIELD_LABEL[r[2]]=r[0];
function chartWidth(id){return Math.max(300,Math.min(560,$(id).clientWidth||560));}
function cohortChart(c,W){
  const H=190,L=40,R=12,T=14,B=34,n=D.cohort.length, iw=W-L-R, ih=H-T-B;
  const X=r=>L+(r-1)/(n-1)*iw, Y=p=>T+(1-p)*ih;
  const s=sv("svg",{viewBox:`0 0 ${W} ${H}`,class:"chart",role:"img","aria-label":`Risk curve of ${n} validation students; this student is rank ${c.rank}. Hover to read any rank; click to open that student.`});
  sv("rect",{x:L,y:T,width:X(D.n_flag)-L,height:ih,style:"fill:var(--flag);opacity:.08"},s);
  for(const p of [0,0.5,1]){sv("line",{x1:L,x2:W-R,y1:Y(p),y2:Y(p),style:"stroke:var(--line)"},s); svText(s,L-6,Y(p)+4,p.toFixed(1),"end");}
  sv("polyline",{points:D.cohort.map((p,i)=>`${X(i+1).toFixed(1)},${Y(p).toFixed(1)}`).join(" "),style:"fill:none;stroke:var(--muted);stroke-width:1.5"},s);
  sv("line",{x1:X(D.n_flag),x2:X(D.n_flag),y1:T,y2:T+ih,style:"stroke:var(--flag);stroke-dasharray:4 3"},s);
  svText(s,X(D.n_flag)+5,T+ih-6,W>=420?`top 20% cut-off (rank ${D.n_flag})`:`top-20% cut-off`);
  svText(s,L,H-6,"rank 1"); svText(s,W-R,H-6,`rank ${n}`,"end");
  if(W>=420) svText(s,L+iw/2,H-6,"students ordered by estimated risk","middle");
  const cy=Y(c.probability);
  for(const r of c.recourse.filter(x=>x.changes)){const ry=Y(D.cohort[r.rank_after-1]);
    sv("line",{x1:X(c.rank),y1:cy,x2:X(r.rank_after),y2:ry,style:"stroke:var(--down);stroke-dasharray:2 2"},s);
    sv("circle",{cx:X(r.rank_after),cy:ry,r:4,style:"fill:var(--panel);stroke:var(--down);stroke-width:1.5"},s);}
  sv("circle",{cx:X(c.rank),cy,r:6,style:`fill:${c.flagged?"var(--flag)":"var(--ok)"};stroke:var(--panel);stroke-width:2`},s);
  const guide=sv("line",{x1:0,x2:0,y1:T,y2:T+ih,style:"stroke:var(--ink);opacity:0"},s);
  const hot=sv("circle",{cx:0,cy:0,r:4,style:"fill:var(--ink);opacity:0"},s);
  const overlay=sv("rect",{x:L,y:T,width:iw,height:ih,style:"fill:transparent;cursor:pointer"},s);
  const rankAt=e=>{const b=s.getBoundingClientRect(); const x=(e.clientX-b.left)*W/b.width; return Math.min(n,Math.max(1,Math.round((x-L)/iw*(n-1))+1));};
  overlay.addEventListener("mousemove",e=>{const r=rankAt(e), p=D.cohort[r-1], who=BY_RANK[r];
    guide.setAttribute("x1",X(r)); guide.setAttribute("x2",X(r)); guide.style.opacity=.35;
    hot.setAttribute("cx",X(r)); hot.setAttribute("cy",Y(p)); hot.style.opacity=1;
    tipShow(`Rank ${r} of ${n} · estimate ${p.toFixed(3)} · ${r<=D.n_flag?"flagged":"not flagged"}`+(who?`\nRecord ${who.source_row_id}${who.source_row_id===c.source_row_id?" (this student)":" · click to open"}`:"\n(practice example, not shown)"),e.clientX,e.clientY);});
  overlay.addEventListener("mouseleave",()=>{guide.style.opacity=0; hot.style.opacity=0; tipHide();});
  overlay.addEventListener("click",e=>{const who=BY_RANK[rankAt(e)]; if(who) goTo(who.source_row_id);});
  const wi=WI[c.source_row_id];
  if(wi&&wi.result){const x=X(wi.result.rank), y=Y(wi.result.probability), d=7;
    sv("line",{x1:X(c.rank),y1:cy,x2:x,y2:y,style:"stroke:var(--what);stroke-width:1.5"},s);
    sv("path",{d:`M${x} ${y-d}L${x+d} ${y}L${x} ${y+d}L${x-d} ${y}Z`,style:"fill:var(--what);stroke:var(--panel);stroke-width:1.5"},s);}
  return s;
}
function stabilityChart(st,W){
  const rowH=26,L=W>=420?185:128,R=48,T=6,rows=[[W>=420?"Different random start":"Random start","seed"],[W>=420?"Different comparison group":"Comparison group","background"],[W>=420?"Tiny grade changes":"Tiny grade change","perturbation"]];
  const iw=W-L-R, X=v=>L+v*iw, bottom=T+rows.length*rowH, H=bottom+20;
  const s=sv("svg",{viewBox:`0 0 ${W} ${H}`,class:"chart",role:"img","aria-label":"Explanation stability: top-five overlap across reruns"});
  rows.forEach(([label,key],i)=>{const y=T+i*rowH, v=st[key], low=v<D.warning_level;
    svText(s,L-8,y+15,label,"end");
    sv("rect",{x:L,y:y+4,width:iw,height:14,style:"fill:var(--line);opacity:.5"},s);
    sv("rect",{x:L,y:y+4,width:Math.max(1,v*iw),height:14,style:`fill:${low?"var(--warn)":"var(--ok)"}`},s);
    svText(s,W-R+6,y+15,v.toFixed(2));
    const HELP={seed:"The explanation uses random sampling. Re-run 10 times with different random starts.",
      background:"Contributions are measured against a comparison group of 25 training students. Re-run with 10 different groups.",
      perturbation:"Grades nudged by a tiny amount (1% of their spread) that barely changes the estimate."};
    const hit=sv("rect",{x:0,y:y,width:W,height:rowH,style:"fill:transparent"},s);
    tipFor(hit,`${HELP[key]} On average ${(v*5).toFixed(1)} of the top 5 reasons stayed the same (${v.toFixed(2)}). ${low?"Below 0.80: unstable.":"At or above 0.80: stable."}`);});
  const wx=X(D.warning_level);
  sv("line",{x1:wx,x2:wx,y1:T,y2:bottom,style:"stroke:var(--ink);stroke-dasharray:4 3"},s);
  svText(s,wx,bottom+14,`warning level ${D.warning_level.toFixed(2)}`,"middle");
  svText(s,L,bottom+14,"0","middle"); svText(s,L+iw,bottom+14,"1","middle");
  return s;
}
function renderBars(b,bars){
  b.innerHTML=""; const m=Math.max(...bars.map(x=>Math.abs(x.value)))||1;
  for(const x of bars){const row=el("div",undefined,"bar"); row.appendChild(el("div",x.label)); row.tabIndex=0;
    const pts=Math.abs(x.value*100).toFixed(1), members=(x.members||[]).map(f=>FIELD_LABEL[f]||f.replace(/_/g," "));
    tipFor(row,`${x.label} ${x.value>=0?"raised":"lowered"} the estimate by ${pts} percentage points compared with typical students.`+(members.length?`\nIncludes: ${members.join(", ")}.`:""));
    const mark=on=>document.querySelectorAll("#profile tr[data-field]").forEach(tr=>tr.classList.toggle("hl",on&&(x.members||[]).includes(tr.dataset.field)));
    row.addEventListener("mouseenter",()=>mark(true)); row.addEventListener("mouseleave",()=>mark(false));
    row.addEventListener("focus",()=>mark(true)); row.addEventListener("blur",()=>mark(false));
    const tr=el("div",undefined,"track"), f=el("div",undefined,"fill"), w=Math.abs(x.value)/m*50;
    f.style.width=w+"%"; f.style.left=(x.value>=0?50:50-w)+"%"; f.style.background=x.value>=0?"var(--up)":"var(--down)";
    tr.appendChild(f); row.appendChild(tr); row.appendChild(el("div",(x.value>=0?"+":"")+x.value.toFixed(3),"num")); b.appendChild(row);}
}
let WHATIF=false; const WI={};
let BOUNDS={}, FAST=false;
const FIELDS=[
 ["curricular_units_1st_sem_enrolled","Units enrolled","n","units","Course units (subjects) the student registered for in semester 1."],
 ["curricular_units_1st_sem_evaluations","Evaluations taken","n","exams","Exams or assessments the student sat; can be more than the units because of resits."],
 ["curricular_units_1st_sem_approved","Units passed","n","units","Units passed; cannot be more than units enrolled or evaluations taken."],
 ["curricular_units_1st_sem_without_evaluations","Units with no evaluation","n","units","Enrolled units where the student took no exam or assessment at all."],
 ["curricular_units_1st_sem_grade","Average grade of passed units","g","/ 20","Portuguese 0–20 scale, pass mark 10. Average of the passed units only; enter 0 if no units were passed."],
 ["tuition_fees_up_to_date","Tuition fees paid up to date","b","","Whether tuition fees were paid on time at the end of semester 1."],
 ["debtor","Owes money to the university","b","","Whether the student has an outstanding debt to the university."],
 ["scholarship_holder","Scholarship","b","","Whether the student holds a scholarship."]];
const LABEL=Object.fromEntries(FIELDS.map(f=>[f[0],f[1]]));
const fmt=(kind,v)=>kind==="b"?(Number(v)===1?"Yes":"No"):kind==="g"?(+v).toFixed(2).replace(/\.?0+$/,""):String(v);
function checkValues(v){
  const e={}, E="curricular_units_1st_sem_", n=k=>v[E+k];
  for(const [key,label,kind] of FIELDS){const x=v[key];
    if(kind!=="b"&&(x===""||!Number.isFinite(x))){e[key]="Enter a number."; continue;}
    if(kind==="n"&&!Number.isInteger(x)) e[key]="Whole numbers only.";
    else if(kind==="n"&&BOUNDS[key]&&(x<BOUNDS[key][0]||x>BOUNDS[key][1])) e[key]=`Allowed ${BOUNDS[key][0]}–${BOUNDS[key][1]}.`;}
  if(!e[E+"approved"]&&n("approved")>n("enrolled")) e[E+"approved"]="Cannot be more than units enrolled.";
  else if(!e[E+"approved"]&&n("approved")>n("evaluations")) e[E+"approved"]="Cannot be more than evaluations taken.";
  if(!e[E+"without_evaluations"]&&n("without_evaluations")>n("enrolled")) e[E+"without_evaluations"]="Cannot be more than units enrolled.";
  const g=n("grade"), gb=BOUNDS[E+"grade"]||[9.8,18.875];
  if(!e[E+"grade"]){ if(n("approved")===0&&g!==0) e[E+"grade"]="Must be 0 when no units were passed.";
    else if(n("approved")>0&&(g<gb[0]||g>gb[1])) e[E+"grade"]=`With units passed, use ${gb[0]}–${gb[1]}.`;}
  return e;}
function renderWhatIf(c){
  const box=$("whatif"); box.innerHTML="";
  if(!WHATIF){box.appendChild(el("p","Not available in this saved copy of the page. To change a student's first-semester results or fee status and see the model's new estimate, start the page with: python scripts/launch_interface.py --what-if","muted")); return;}
  const state=WI[c.source_row_id]||(WI[c.source_row_id]={values:{...c.edit}});
  const steps=el("ol",undefined,"steps");
  for(const s of ["Change one or more boxes below (or use a quick example). Changed boxes turn purple and show the recorded value.",
                  `Press Predict. The frozen model re-scores this student (${FAST?"about 1 second":"about 10 seconds"}).`,
                  "Compare the new estimate and rank with the recorded ones; the purple diamond in section 1 shows the new position."]) steps.appendChild(el("li",s));
  box.appendChild(steps);
  const quick=el("div",undefined,"buttons"); quick.appendChild(el("span","Quick examples:","muted"));
  const presets=[["Fees paid, no debt",v=>{v.tuition_fees_up_to_date=1; v.debtor=0;}],
    ["Passed every enrolled unit",v=>{const E="curricular_units_1st_sem_"; v[E+"approved"]=v[E+"enrolled"]; v[E+"evaluations"]=Math.max(v[E+"evaluations"],v[E+"enrolled"]); v[E+"without_evaluations"]=0; if(v[E+"enrolled"]>0&&v[E+"grade"]<10) v[E+"grade"]=12;}],
    ["Passed no units",v=>{const E="curricular_units_1st_sem_"; v[E+"approved"]=0; v[E+"grade"]=0;}]];
  for(const [label,fn] of presets){const b=el("button",label,"secondary small"); b.addEventListener("click",()=>{fn(state.values); state.result=null; state.error=null; show();}); quick.appendChild(b);}
  box.appendChild(quick);
  const errors=checkValues(state.values);
  const form=el("div",undefined,"form");
  for(const [key,label,kind,unit,help] of FIELDS){
    const changed=Math.abs(Number(state.values[key])-Number(c.edit[key]))>1e-6;
    const lab=el("label",undefined,"field"+(changed?" changed":"")+(errors[key]?" invalid":""));
    const head=el("span",label); const i=el("span","i","info"); i.tabIndex=0; tipFor(i,help); head.appendChild(i); lab.appendChild(head);
    const wrap=el("div",undefined,"inwrap"); let inp;
    if(kind==="b"){inp=el("select"); for(const [v,tx] of [[1,"Yes"],[0,"No"]]){const o=el("option",tx); o.value=v; inp.appendChild(o);} inp.value=String(Number(state.values[key]));}
    else{inp=el("input"); inp.type="number"; inp.inputMode=kind==="g"?"decimal":"numeric"; inp.step=kind==="g"?"any":"1";
      if(BOUNDS[key]){inp.min=kind==="g"?0:BOUNDS[key][0]; inp.max=BOUNDS[key][1];}
      inp.value=kind==="g"?fmt("g",state.values[key]):state.values[key];}
    inp.setAttribute("aria-label",label);
    inp.addEventListener("change",()=>{state.values[key]=inp.value===""?"":Number(inp.value); state.result=null; state.error=null; show();});
    wrap.appendChild(inp); if(unit) wrap.appendChild(el("span",unit,"unit")); lab.appendChild(wrap);
    const range=kind==="n"&&BOUNDS[key]?` · allowed ${BOUNDS[key][0]}–${BOUNDS[key][1]}`:kind==="g"?" · 0 if none passed, else 9.8–18.9":"";
    lab.appendChild(el("span",errors[key]||`Recorded: ${fmt(kind,c.edit[key])}${unit&&kind!=="g"?" "+(Number(c.edit[key])===1?unit.replace(/s$/,""):unit):""}${range}`,errors[key]?"hint err":"hint"));
    form.appendChild(lab);}
  box.appendChild(form);
  const nChanged=FIELDS.filter(([k])=>Math.abs(Number(state.values[k])-Number(c.edit[k]))>1e-6).length, invalid=Object.keys(errors).length>0;
  const btns=el("div",undefined,"buttons"), go=el("button","Predict"), reset=el("button","Reset to recorded values","secondary");
  go.disabled=invalid||state.busy;
  const exp=el("label"); const cb=el("input"); cb.type="checkbox"; cb.checked=!!state.explain; cb.addEventListener("change",()=>{state.explain=cb.checked;});
  exp.appendChild(cb); exp.appendChild(document.createTextNode(` also recompute the reasons (${FAST?"a few seconds":"about 25 s"})`)); exp.className="muted";
  btns.appendChild(go); btns.appendChild(reset); btns.appendChild(exp); box.appendChild(btns);
  box.appendChild(el("p",invalid?"Fix the boxes marked in red to enable Predict.":nChanged?`${nChanged} value${nChanged>1?"s":""} changed from the recorded profile.`:"No changes yet: Predict will simply re-score the recorded profile.",invalid?"hint err":"muted"));
  const out=el("div"); box.appendChild(out);
  reset.addEventListener("click",()=>{WI[c.source_row_id]={values:{...c.edit}}; show();});
  go.addEventListener("click",async()=>{
    state.busy=true; go.disabled=true; out.innerHTML=""; out.appendChild(el("p",state.explain?"Predicting and recomputing reasons with the frozen model…":"Predicting with the frozen model…","muted"));
    try{const r=await fetch("/api/predict",{method:"POST",headers:{"Content-Type":"application/json"},
          body:JSON.stringify({source_row_id:c.source_row_id,edits:state.values,explain:!!state.explain})});
        const j=await r.json(); if(!r.ok) throw new Error(j.error||"request failed");
        state.result=j; state.error=null;}
    catch(e){state.result=null; state.error=e.message;}
    state.busy=false; show();});
  if(state.error) out.appendChild(el("div","Not accepted: "+state.error,"error"));
  if(state.result){const r=state.result, res=el("div",undefined,"result");
    const moved=r.rank<r.recorded_rank?"higher risk":r.rank>r.recorded_rank?"lower risk":"same position";
    res.appendChild(el("strong",`New estimate ${r.probability.toFixed(3)} · rank ${r.rank} of ${D.n_cases} · ${r.flagged?"would be FLAGGED":"would not be flagged"}`));
    res.appendChild(el("div",`Recorded: ${r.recorded_probability.toFixed(3)}, rank ${r.recorded_rank} (${r.recorded_rank<=D.n_flag?"flagged":"not flagged"}). Rank moved ${Math.abs(r.recorded_rank-r.rank)} place${Math.abs(r.recorded_rank-r.rank)===1?"":"s"} (${moved}).`,"muted"));
    res.appendChild(el("div",`Changed: ${r.changed.length?r.changed.map(k=>LABEL[k].toLowerCase()).join(", "):"nothing"}.`,"muted"));
    if(r.bars){res.appendChild(el("p","Top five reasons for the edited profile:","muted")); const b=el("div"); renderBars(b,r.bars); res.appendChild(b);}
    res.appendChild(el("p","A new prediction from the frozen model with the other 543 scores fixed. It has no stability audit or fee/debt check, and it shows how the model responds, not what would happen to the student or what they should do.","muted"));
    out.appendChild(res);}
}
function fillPicker(){
  const only=$("only").checked, pick=$("pick"), keep=pick.value; pick.innerHTML="";
  for(const c of D.cases){ if(only && !c.flagged) continue;
    const o=el("option",`Rank ${c.rank} of ${D.n_cases} · record ${c.source_row_id}${c.flagged?" · flagged":" · not flagged"}`); o.value=c.source_row_id; pick.appendChild(o);}
  if([...pick.options].some(o=>o.value===keep)) pick.value=keep;
  show();
}
function show(){
  const c=D.cases.find(x=>String(x.source_row_id)===$("pick").value); if(!c) return;
  const t=$("profile"); t.innerHTML="";
  for(const s of c.profile){const r=t.insertRow(); const h=r.insertCell(); h.colSpan=2; h.className="sub"; h.textContent=s.heading;
    for(const [k,v,f] of s.rows){const row=t.insertRow(); row.dataset.field=f; row.insertCell().textContent=k; row.insertCell().textContent=v;}}
  const st=$("status"); st.innerHTML="";
  st.appendChild(el("div", c.flagged?"Yes: flagged for a support contact":"No: not flagged", "status "+(c.flagged?"flag":"noflag")));
  st.appendChild(el("p",`Ranked ${c.rank} of ${D.n_cases} by estimated risk; the top ${D.n_flag} (20%) are flagged. Estimated dropout probability: ${c.probability.toFixed(3)}. This is a model score, not a certainty.`,"muted"));
  if(Math.abs(c.rank-D.n_flag)<=10) st.appendChild(el("p",`Close to the cut-off (rank ${D.n_flag}): a small change in other students' scores could change this flag.`,"muted"));
  st.appendChild(cohortChart(c,chartWidth("status")));
  const lg=el("div",undefined,"legend");
  const item=(sym,color,text)=>{const s=el("span",sym+" ","sym"); s.style.color=color; lg.appendChild(s); lg.appendChild(document.createTextNode(text+"   "));};
  lg.appendChild(document.createTextNode("The line shows all 544 students from highest to lowest estimate. "));
  item("●",c.flagged?"var(--flag)":"var(--ok)","this student");
  if(c.recourse.some(x=>x.changes)) item("○","var(--down)","rank if fees/debt were cleared (section 4)");
  if(WI[c.source_row_id]&&WI[c.source_row_id].result) item("◆","var(--what)","your what-if result (section 5)");
  item("▮","var(--flag)","shaded area = flagged top 20%");
  st.appendChild(lg);
  renderBars($("bars"),c.bars);
  renderWhatIf(c);
  const r=$("reliability"); r.innerHTML=""; const s=c.stability;
  const low=Object.entries(s).filter(([,v])=>v<D.warning_level).map(([k])=>k);
  const NAMES={seed:"random start",background:"comparison group",perturbation:"tiny grade changes"};
  if(low.length){const w=el("div",undefined,"warn"); w.appendChild(el("strong","Treat these reasons as approximate. ")); w.appendChild(document.createTextNode(`When the calculation was repeated with a different ${low.map(k=>NAMES[k]).join(" or ")}, the top five reasons often changed.`)); r.appendChild(w);}
  else r.appendChild(el("p","The top five reasons stayed mostly the same when the calculation was repeated.","muted"));
  r.appendChild(el("p","Share of the top five reasons that stayed the same over 10 repeats (1 = identical every time). Below the dashed line counts as unstable.","muted"));
  r.appendChild(stabilityChart(s,chartWidth("reliability")));
  const rc=$("recourse"); rc.innerHTML="";
  if(!c.flagged) rc.appendChild(el("p","This student is not flagged, so this check does not apply.","muted"));
  else if(c.recourse.every(x=>x.status==="no_recourse")) rc.appendChild(el("p","No. Even with fees paid and no debt, the model would still flag this student.","muted"));
  else {rc.appendChild(el("p","Yes. With the change below (and everyone else's scores unchanged), the model would no longer flag this student:","muted"));
    const ul=el("ul"); for(const x of c.recourse.filter(x=>x.changes)) ul.appendChild(el("li",`${x.changes.join(" and ")} → rank ${x.rank_after}`)); rc.appendChild(ul);}
  rc.appendChild(el("p","Fee or debt status can reflect financial hardship. This is not a cause, a prediction that paying would prevent dropout, or an obligation on the student.","muted"));
  if(c.flagged && c.topics.length){rc.appendChild(el("p","Topics an adviser could raise, if the student agrees:","muted")); const ul=el("ul"); for(const t of c.topics) ul.appendChild(el("li",t)); rc.appendChild(ul);}
}
const a=$("audit"); for(const [k,v] of Object.entries(D.audit)){a.appendChild(el("dt",k.replace(/_/g," "))); a.appendChild(el("dd",v));}
$("pick").addEventListener("change",()=>{history.replaceState(null,"","#student="+$("pick").value); show();});
$("only").addEventListener("change",fillPicker);
let resizeTimer; addEventListener("resize",()=>{clearTimeout(resizeTimer); resizeTimer=setTimeout(show,150);});
function goTo(id){
  if(![...$("pick").options].some(o=>o.value===String(id))){$("only").checked=false; fillPicker();}
  $("pick").value=String(id); history.replaceState(null,"","#student="+id); show();}
function step(d){const o=[...$("pick").options], i=o.findIndex(x=>x.value===$("pick").value), j=i+d;
  if(j>=0&&j<o.length) goTo(o[j].value);}
addEventListener("keydown",e=>{if(e.target.closest("input,select,textarea,button")||e.altKey||e.ctrlKey||e.metaKey) return;
  if(e.key==="ArrowLeft"){step(-1); e.preventDefault();} if(e.key==="ArrowRight"){step(1); e.preventDefault();}});
$("prev").addEventListener("click",()=>step(-1)); $("next").addEventListener("click",()=>step(1));
(function(){const C=D.cases, flagged=C.filter(c=>c.flagged), not=C.filter(c=>!c.flagged);
  const ex=[["Highest estimated risk",C[0]],
    ["Flagged, just inside the cut-off",flagged[flagged.length-1]],
    ["Not flagged, just outside the cut-off",not[0]],
    ["Flagged, reasons unstable",flagged.slice().sort((a,b)=>a.stability.background-b.stability.background)[0]],
    ["Flagged, clearing fees would change the flag",flagged.find(c=>c.recourse.some(x=>x.changes))],
    ["Lowest estimated risk",C[C.length-1]]];
  for(const [label,c] of ex){if(!c) continue; const o=el("option",label); o.value=c.source_row_id; $("examples").appendChild(o);}
  $("examples").addEventListener("change",e=>{if(e.target.value) goTo(e.target.value); e.target.value="";});})();
try{ if(localStorage.getItem("aboutClosed")==="1") $("about").open=false; }catch(e){}
$("about").addEventListener("toggle",()=>{try{localStorage.setItem("aboutClosed",$("about").open?"0":"1");}catch(e){}});
fillPicker();
if(location.protocol.startsWith("http")) fetch("/api/status").then(r=>r.ok?r.json():null).then(j=>{if(j&&j.what_if){WHATIF=true; FAST=!!j.fast; BOUNDS=j.bounds||{}; show();}}).catch(()=>{});
addEventListener("hashchange",()=>{const id=(location.hash.match(/student=(\d+)/)||[])[1]; if(id&&id!==$("pick").value&&BY_RANK&&D.cases.some(c=>String(c.source_row_id)===id)) goTo(id);});
const wanted=(location.hash.match(/student=(\d+)/)||[])[1];
if(wanted && [...$("pick").options].some(o=>o.value===wanted)){$("pick").value=wanted; show();}
</script>
</body>
</html>
"""


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--no-open", action="store_true", help="build the page without opening a browser")
    parser.add_argument("--out", default=str(OUT))
    parser.add_argument("--what-if", action="store_true",
                        help="serve the page locally with live re-prediction by the frozen model")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args(argv)
    out = build(Path(args.out))
    if args.what_if:
        from scripts.whatif_server import serve
        n_flag = json.loads(out.read_text(encoding="utf-8").split('type="application/json">', 1)[1]
                            .split("</script>", 1)[0].replace("<\\/", "</"))["n_flag"]
        serve(out, study_source_ids(), n_flag, port=args.port, open_browser=not args.no_open)
        return 0
    if not args.no_open:
        webbrowser.open(out.resolve().as_uri())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
