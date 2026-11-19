"""Regression checks for the jam submission and ballot scripts."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import manage_event as ballot
import publish_submission as publish


def issue(number, login, url, *labels):
    return {
        "number": number,
        "user": {"type": "User", "login": login},
        "title": "[Game] Test game",
        "body": (
            "### Name or team name\n\nTeam Seagull\n\n"
            "### What did you ask the AI to change?\n\nAdd a shield\n\n"
            f"### Link to play your game\n\n{url}"
        ),
        "state": "open",
        "labels": [{"name": name} for name in ("submission", *labels)],
    }


class SubmissionTest(unittest.TestCase):
    repository = "uopaisociety/flappy-ai-jam"

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        manifest = Path(temp.name) / "manifest.json"
        manifest.write_text('{"version":1,"builds":[]}')
        event = Path(temp.name) / "event.json"
        event.write_text('{"state":"pending"}')
        for target, value in [
            ("MANIFEST", manifest),
            ("EVENT", event),
            ("repository_writer", lambda _repo, login: login == "Desk"),
        ]:
            mock = patch.object(publish, target, value)
            mock.start()
            self.addCleanup(mock.stop)

    def test_public_links(self):
        for url in [
            "share.gemini.google/abc123",
            "https://g.co/gemini/share/abc123",
            "https://gemini.google.com/share/abc123",
            "https://user.github.io/game/",
        ]:
            with self.subTest(url=url):
                entry = publish.parse_submission(issue(1, "Player", url), self.repository)
                self.assertTrue(entry["url"].startswith("https://"))
        for url in [
            "https://gemini.google.com/app/private",
            "https://share.gemini.google/",
            "https://g.co/other",
            "https://www.google.com/url?q=example.com",
            "https://github.com/user/game",
            "http://example.com/game",
            "https://example.com/game (the game)",
        ]:
            with self.subTest(url=url), self.assertRaises(ValueError):
                publish.parse_submission(issue(1, "Player", url), self.repository)

    def test_missing_assisted_label_cannot_overwrite_game(self):
        url = "https://example.com/game"
        first = issue(1, "Desk", url, "committee-assisted")
        self.assertEqual(publish.publish_row(first, self.repository), "entry--1")
        with self.assertRaisesRegex(ValueError, "need the committee-assisted label"):
            publish.publish_row(issue(2, "Desk", url), self.repository)
        with self.assertRaisesRegex(ValueError, "write access"):
            publish.publish_row(issue(3, "Player", url, "committee-assisted"), self.repository)
        second = issue(2, "Desk", url, "committee-assisted")
        self.assertEqual(publish.publish_row(second, self.repository), "entry--2")
        self.assertEqual([row["id"] for row in json.loads(publish.MANIFEST.read_text())["builds"]],
                         ["entry--1", "entry--2"])

    def test_batch_keeps_valid_entries_and_reports_rejections(self):
        entries = [
            issue(6, "Desk", "share.gemini.google/example", "committee-assisted"),
            issue(7, "Desk", "https://gemini.google.com/app/private", "committee-assisted"),
            issue(8, "Player", "https://example.com/game"),
        ]
        with patch.object(publish, "gh_json", side_effect=entries) as fetch:
            results = publish.publish_assisted(self.repository, "6, 7 8, 6")
        self.assertEqual(fetch.call_count, 3)
        self.assertEqual(results[0], {"issue": 6, "build": "entry--6", "assisted": True})
        self.assertIn("public share link", results[1]["error"])
        self.assertTrue(results[2]["silent"])
        self.assertEqual([row["id"] for row in json.loads(publish.MANIFEST.read_text())["builds"]],
                         ["entry--6"])

    def test_issue_edited_after_approval_requires_review_again(self):
        old = issue(1, "Player", "https://example.com/old", "approved")
        current = issue(1, "Player", "https://example.com/new", "approved")
        with patch.object(publish, "gh_json", return_value=current):
            with self.assertRaisesRegex(ValueError, "submission changed"):
                publish.approve_issue(self.repository, {"issue": old})


class BallotTest(unittest.TestCase):
    def test_paper_only_opens_and_closes_without_github(self):
        with tempfile.TemporaryDirectory() as temp:
            manifest = Path(temp) / "manifest.json"
            manifest.write_text(json.dumps({"builds": [
                {"id": "entry--9", "title": "Seagull", "builder": "Team A", "kind": "submission"},
                {"id": "entry--10", "title": "Football", "builder": "Team B", "kind": "submission"},
            ]}))
            with patch.object(ballot, "MANIFEST", manifest), patch.object(ballot, "gh_json") as api:
                event = ballot.open_ballot("unused", {"state": "pending"}, paper_only=True)
                self.assertNotIn("issue", event)
                with self.assertRaises(ValueError):
                    ballot.close_ballot("unused", event, "1=4", "#1")
                closed = ballot.close_ballot("unused", event, "1=4; 2=3,", "2", "#1")
                api.assert_not_called()
        self.assertEqual(closed["counts"], {"entry--9": 4, "entry--10": 3})
        self.assertEqual(closed["awards"], {
            "audience": ["entry--9"], "technical": ["entry--10"], "creative": ["entry--9"],
        })


if __name__ == "__main__":
    unittest.main()
