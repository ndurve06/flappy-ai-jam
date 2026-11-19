"""Manage the GitHub audience ballot and publish the event's official awards."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import sys

from publish_submission import EVENT, HANDLE, MANIFEST, gh_json, repository_writer

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


def open_ballot(repo, event, paper_only=False):
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

    if paper_only:
        return {"state": "open", "opensAt": now(), "candidates": candidates, "paperOnly": True}

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
            "vote into the comment box here and press Comment. "
            "Only your latest valid online vote counts. If you voted on paper, use that vote only.\n\n"
            "Use your GitHub account. Keep student numbers and other personal details out of this public thread.\n\n"
            f"{BALLOT_MARKER}"
        )
        issue = mutate(f"{repo}/issues", "POST", (
            "title=Flappy AI Jam · Audience voting", f"body={body}", f"labels[]={BALLOT_LABEL}",
        ))
    if issue["state"] != "open" or issue["locked"]:
        raise ValueError("The ballot issue must be open and unlocked.")
    return {"state": "open", "issue": issue["number"], "opensAt": issue["created_at"], "candidates": candidates}


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def timestamp(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def parse_paper_votes(event, ballots):
    counts = {}
    if not ballots.strip():
        return counts
    candidates = event["candidates"]
    for item in re.split(r"[,;]", ballots.strip().removesuffix(",").removesuffix(";")):
        match = re.fullmatch(r"([0-9]+)\s*=\s*([0-9]+)", item.strip())
        if not match:
            raise ValueError("Enter paper votes as ballot_number=count, for example 1=4, 2=3.")
        number, count = map(int, match.groups())
        if not 1 <= number <= len(candidates):
            raise ValueError("Unknown ballot number: " + str(number))
        identifier = candidates[number - 1]["id"]
        if identifier in counts:
            raise ValueError("Repeated ballot number: " + str(number))
        if count > 2**53 - 1:
            raise ValueError("Paper vote tally is too large.")
        counts[identifier] = count
    return counts


def tally(event, comments, closes_at, paper_counts=None):
    counts = dict.fromkeys((row["id"] for row in event["candidates"]), 0)
    counts.update(paper_counts or {})
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


def close_ballot(repo, event, paper_votes="", technical="", creative=""):
    if event["state"] == "closed":
        return event
    if event["state"] != "open":
        raise ValueError("Open the audience ballot before closing it.")
    paper_counts = parse_paper_votes(event, paper_votes)
    jury = resolve_winners(event, technical, creative) if technical.strip() or creative.strip() else {}
    if event.get("paperOnly"):
        closes_at, comments = now(), []
    else:
        endpoint = f"{repo}/issues/{event['issue']}"
        issue = gh_json(endpoint)
        if not issue["locked"]:
            mutate(endpoint + "/lock", "PUT", ("lock_reason=resolved",))
        if issue["state"] == "open":
            issue = mutate(endpoint, "PATCH", ("state=closed",))
        closes_at = issue["closed_at"]
        comments = api_pages(endpoint + "/comments?per_page=100")
    counts, winners = tally(event, comments, closes_at, paper_counts)
    return {
        **event, "state": "closed", "closesAt": closes_at,
        "counts": counts, "awards": {"audience": winners, **jury},
    }


def resolve_winners(event, technical, creative):
    entries = {row["id"] for row in event["candidates"]}
    numbered = {str(index): row["id"] for index, row in enumerate(event["candidates"], start=1)}
    technical, creative = technical.strip().lower(), creative.strip().lower()
    technical = technical if technical in entries else numbered.get(technical.removeprefix("#"))
    creative = creative if creative in entries else numbered.get(creative.removeprefix("#"))
    if technical not in entries or creative not in entries:
        raise ValueError("Enter a valid build ID or a ballot number (e.g. #2) for each of the two committee awards.")
    return {"technical": [technical], "creative": [creative]}


def set_winners(event, technical, creative):
    if event["state"] != "closed":
        raise ValueError("Close the audience ballot before publishing the committee awards.")
    jury = resolve_winners(event, technical, creative)
    return {**event, "awards": {**event["awards"], **jury}}


def main():
    repository = os.environ["GITHUB_REPOSITORY"]
    repo = "repos/" + repository
    with Path(os.environ["GITHUB_EVENT_PATH"]).open() as payload:
        dispatch = json.load(payload)
    sender = dispatch["sender"]
    if sender["type"] != "User" or not HANDLE.fullmatch(sender["login"]):
        raise ValueError("Event operations require a committee account with repository write access.")
    if not repository_writer(repository, sender["login"]):
        raise ValueError("Event operations require repository write access.")

    event = json.loads(EVENT.read_text())
    inputs = dispatch["inputs"]
    task = inputs["operation"]
    if task == "open-voting":
        event = open_ballot(repo, event, str(inputs.get("paper_only", "")).lower() == "true")
    elif task == "close-voting":
        event = close_ballot(
            repo, event, inputs.get("paper_votes", ""),
            inputs.get("technical_id", ""), inputs.get("creative_id", ""),
        )
    elif task == "publish-winners":
        event = set_winners(event, inputs["technical_id"], inputs["creative_id"])
    else:
        raise ValueError("Unknown event operation.")
    EVENT.write_text(json.dumps(event, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for number, candidate in enumerate(event.get("candidates", []), start=1):
        print(f"Ballot #{number} · {candidate['title']} · {candidate['builder']} [ID: {candidate['id']}]")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        print(error, file=sys.stderr)
        sys.exit(1)
