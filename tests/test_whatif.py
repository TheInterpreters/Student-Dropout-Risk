import json
import threading
import unittest
import urllib.error
import urllib.request
from http.server import HTTPServer

from scripts import whatif_server as wi

BOUNDS = {"curricular_units_1st_sem_enrolled": (0, 26), "curricular_units_1st_sem_evaluations": (0, 45),
          "curricular_units_1st_sem_approved": (0, 26),
          "curricular_units_1st_sem_without_evaluations": (0, 12),
          "curricular_units_1st_sem_grade": (9.8, 18.875)}


def edits(**changes):
    base = {"curricular_units_1st_sem_enrolled": 6, "curricular_units_1st_sem_evaluations": 8,
            "curricular_units_1st_sem_approved": 4, "curricular_units_1st_sem_without_evaluations": 0,
            "curricular_units_1st_sem_grade": 11.5, "tuition_fees_up_to_date": 0, "debtor": 1,
            "scholarship_holder": 0}
    base.update(changes)
    return base


class ValidateEditsTests(unittest.TestCase):
    def test_accepts_consistent_values(self):
        clean = wi.validate_edits(edits(), BOUNDS)
        self.assertEqual(clean["curricular_units_1st_sem_approved"], 4)
        clean = wi.validate_edits(edits(curricular_units_1st_sem_approved=0,
                                        curricular_units_1st_sem_grade=0), BOUNDS)
        self.assertEqual(clean["curricular_units_1st_sem_grade"], 0.0)

    def test_rejects_inconsistent_or_out_of_range_values(self):
        bad = [edits(curricular_units_1st_sem_approved=7),               # passed > enrolled
               edits(curricular_units_1st_sem_evaluations=3),            # passed > evaluations
               edits(curricular_units_1st_sem_without_evaluations=7),    # missing > enrolled
               edits(curricular_units_1st_sem_approved=0),               # grade must be 0
               edits(curricular_units_1st_sem_grade=19.5),               # above development range
               edits(curricular_units_1st_sem_enrolled=27),              # above development range
               edits(curricular_units_1st_sem_enrolled=6.5),             # not whole
               edits(debtor=2), edits(debtor=True)]
        for record in bad:
            with self.assertRaises(ValueError):
                wi.validate_edits(record, BOUNDS)

    def test_rejects_extra_or_missing_fields(self):
        with self.assertRaises(ValueError):
            wi.validate_edits({**edits(), "gender": 1}, BOUNDS)
        record = edits()
        del record["debtor"]
        with self.assertRaises(ValueError):
            wi.validate_edits(record, BOUNDS)


class RankTests(unittest.TestCase):
    def test_rank_replaces_own_score_and_breaks_ties_by_position(self):
        cohort, positions = [0.9, 0.8, 0.7, 0.6], [0, 1, 2, 3]
        self.assertEqual(wi.cohort_rank(0.95, 3, cohort, positions), 1)
        self.assertEqual(wi.cohort_rank(0.8, 3, cohort, positions), 3)   # tie with position 1
        self.assertEqual(wi.cohort_rank(0.8, 0, cohort, positions), 1)   # own old score ignored
        self.assertEqual(wi.cohort_rank(0.1, 0, cohort, positions), 4)


class FakeEngine:
    bounds = BOUNDS

    def predict(self, source_row_id, edit_values, explain=False):
        wi.validate_edits(edit_values, BOUNDS)
        return {"probability": 0.5, "rank": 200, "flagged": False}


class HandlerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), wi.make_handler(b"<html>page</html>", FakeEngine(), "x"))
        port = cls.server.server_address[1]
        cls.host = f"127.0.0.1:{port}"
        cls.server.RequestHandlerClass = wi.make_handler(b"<html>page</html>", FakeEngine(), cls.host)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def request(self, path, body=None, headers=None):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(f"http://{self.host}{path}", data=data, headers=headers or {})
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                return response.status, response.read()
        except urllib.error.HTTPError as error:
            return error.code, error.read()

    def test_serves_page_and_predicts(self):
        self.assertEqual(self.request("/")[1], b"<html>page</html>")
        status, body = self.request("/api/predict", {"source_row_id": 1, "edits": edits()},
                                    {"Content-Type": "application/json"})
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["rank"], 200)

    def test_rejects_bad_requests(self):
        status, _ = self.request("/api/predict", {"source_row_id": 1, "edits": edits(debtor=5)},
                                 {"Content-Type": "application/json"})
        self.assertEqual(status, 400)
        status, _ = self.request("/api/predict", {"source_row_id": 1, "edits": edits()},
                                 {"Content-Type": "text/plain"})
        self.assertEqual(status, 415)
        status, _ = self.request("/api/status", headers={"Host": "evil.example"})
        self.assertEqual(status, 403)
        status, _ = self.request("/other")
        self.assertEqual(status, 404)


if __name__ == "__main__":
    unittest.main()
