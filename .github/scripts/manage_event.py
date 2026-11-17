"""Manage the GitHub audience ballot and publish the event's official awards."""

from datetime import datetime
import json
import os
from pathlib import Path
import re
import subprocess
import sys

from publish_submission import HANDLE, MANIFEST, gh_json

EVENT = Path("submissions/event.json")
BALLOT_LABEL = "audience-ballot"
BALLOT_MARKER = "<!-- flappy-ai-jam:audience-ballot -->"
VOTE = re.compile(r"Vote: ([a-z0-9][a-z0-9-]{0,38})", re.I | re.ASCII)


def api_pages(endpoint):
    output = subprocess.check_output(["gh", "api", "--paginate", endpoint, "--jq", ".[] | tostring"], text=True)
    return [json.loads(row) for row in output.splitlines()]


def mutate(endpoint, method, fields=()):
    args = ["gh", "api", "--method", method, endpoint]
    for field in fields:
        args.extend(["-f", field])
    output = subprocess.check_output(args, text=True)
    return json.loads(output) if output else None


def open_ballot(repo, event):
    if event["state"] == "open":
        return event
    if event["state"] != "pending":
        raise ValueError("The audience ballot is already closed.")
    builds = json.loads(MANIFEST.read_text())["builds"]
    candidates = [
        {key: build[key] for key in ("id", "title", "builder")}
        for build in builds if build["kind"] == "submission"
    ]
    if not candidates:
        raise ValueError("Approve at least one game before opening the ballot.")

    # A retry after creating the issue can reuse the same ballot.
    existing = api_pages(f"{repo}/issues?labels={BALLOT_LABEL}&state=all&per_page=100")
    issue = next((
        row for row in existing if "pull_request" not in row
        and row["user"]["login"] == "github-actions[bot]"
        and BALLOT_MARKER in (row["body"] or "")
    ), None)
    if issue is None:
        page = "https://uopaisociety.github.io/flappy-ai-jam/vote.html"
        body = (
            f"Pick a build on the [ballot page]({page}), then paste the generated "
            "vote as a comment here. Only your latest valid vote counts.\n\n"
            "Use your GitHub account. Keep student numbers and other personal details out of this public thread.\n\n"
            f"{BALLOT_MARKER}"
        )
        issue = mutate(f"{repo}/issues", "POST", (
            "title=Flappy AI Jam · Audience voting", f"body={body}", f"labels[]={BALLOT_LABEL}",
        ))
    if issue["state"] != "open" or issue["locked"]:
        raise ValueError("The ballot issue must be open and unlocked.")
    return {"state": "open", "issue": issue["number"], "opensAt": issue["created_at"], "candidates": candidates}


def timestamp(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def tally(event, comments, closes_at):
    counts = dict.fromkeys((row["id"] for row in event["candidates"]), 0)
    first, last = timestamp(event["opensAt"]), timestamp(closes_at)
    latest = {}
    for comment in comments:
        voter = comment["user"]
        vote = VOTE.fullmatch(comment["body"].strip())
        created = timestamp(comment["created_at"])
        updated = timestamp(comment["updated_at"])
        if (not voter or voter["type"] != "User" or not vote
                or not first <= created <= updated <= last):
            continue
        build = vote[1].lower()
        if build not in counts:
            continue
        order = (created, comment["id"])
        if voter["id"] not in latest or order > latest[voter["id"]][0]:
            latest[voter["id"]] = (order, build)
    for _, build in latest.values():
        counts[build] += 1
    highest = max(counts.values(), default=0)
    winners = [build for build, count in counts.items() if count == highest and highest > 0]
    return counts, winners


def close_ballot(repo, event):
    if event["state"] == "closed":
        return event
    if event["state"] != "open":
        raise ValueError("Open the audience ballot before closing it.")
    endpoint = f"{repo}/issues/{event['issue']}"
    issue = gh_json(endpoint)
    if not issue["locked"]:
        mutate(endpoint + "/lock", "PUT", ("lock_reason=resolved",))
    if issue["state"] == "open":
        issue = mutate(endpoint, "PATCH", ("state=closed",))
    counts, winners = tally(event, api_pages(endpoint + "/comments?per_page=100"), issue["closed_at"])
    return {
        **event, "state": "closed", "closesAt": issue["closed_at"],
        "counts": counts, "awards": {"audience": winners},
    }


def set_winners(event, technical, creative):
    if event["state"] != "closed":
        raise ValueError("Close the audience ballot before publishing the committee awards.")
    entries = {row["id"] for row in event["candidates"]}
    technical, creative = technical.strip().lower(), creative.strip().lower()
    if technical not in entries or creative not in entries:
        raise ValueError("Enter the gallery build ID for both award winners. See the ballot candidates below.")
    return {**event, "awards": {**event["awards"], "technical": [technical], "creative": [creative]}}


def main():
    repo = "repos/" + os.environ["GITHUB_REPOSITORY"]
    with Path(os.environ["GITHUB_EVENT_PATH"]).open() as payload:
        dispatch = json.load(payload)
    sender = dispatch["sender"]
    if sender["type"] != "User" or not HANDLE.fullmatch(sender["login"]):
        raise ValueError("Event operations require a committee account with repository write access.")
    permissions = gh_json(f"{repo}/collaborators/{sender['login']}/permission")
    if permissions.get("permission") not in {"write", "admin"}:
        raise ValueError("Event operations require repository write access.")

    event = json.loads(EVENT.read_text())
    task = dispatch["inputs"]["operation"]
    if task == "open-voting":
        event = open_ballot(repo, event)
    elif task == "close-voting":
        event = close_ballot(repo, event)
    elif task == "publish-winners":
        inputs = dispatch["inputs"]
        event = set_winners(event, inputs["technical_id"], inputs["creative_id"])
    else:
        raise ValueError("Unknown event operation.")
    EVENT.write_text(json.dumps(event, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for candidate in event.get("candidates", []):
        print("Candidate ID:", candidate["id"])


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        print(error, file=sys.stderr)
        sys.exit(1)
