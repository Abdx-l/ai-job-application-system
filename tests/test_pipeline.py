import unittest
from pipeline import build, score, validate


PROFILE = {"name":"Sam","location":"Toronto","skills":["Python","SQL","Docker"],"experience":["Built Python services with SQL.","Used Docker for deployments."],"minimum_score":0.5}
JOB = {"title":"Python Developer","companyName":"Acme","description":"Python SQL","location":"Toronto","url":"https://example.com/1"}


class PipelineTests(unittest.TestCase):
    def test_filter_and_deduplicate(self):
        result = build([JOB, JOB, {**JOB, "url":"https://example.com/2","description":"Illustration"}], PROFILE)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["matched_skills"], ["Python", "SQL"])
        self.assertIn("Built Python services with SQL", result[0]["resume_summary"])
        self.assertIn("Posting: https://example.com/1", result[0]["email_draft"])

    def test_location_and_validation(self):
        self.assertEqual(score({**JOB, "location":"Vancouver"}, PROFILE)[0], 0.333)
        with self.assertRaises(ValueError): validate({**JOB, "url":"file:///etc/passwd"})

    def test_no_fabricated_experience(self):
        item = build([JOB], PROFILE)[0]
        self.assertNotIn("Acme", item["resume_summary"])


if __name__ == "__main__": unittest.main()

