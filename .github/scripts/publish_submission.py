"""Add the approved issue snapshot and its game link to the gallery manifest."""

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit

MANIFEST = Path("submissions/manifest.json")
HANDLE = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,37}[a-z0-9])?", re.I | re.ASCII)
LEGACY_LABELS = (
    "Build Title",
    "Builder Name",
    "LinkedIn URL (optional)",
    "Track",
    "Key Prompt Used",
    "Game URL",
)
LABELS = ("Name or team name", "What did you ask the AI to change?", "Link to play your game")
TRACKS = {
    "Technical Execution": "technical-execution",
    "Game Feel": "game-feel",
    "Creative Mutation": "creative-mutation",
}
REQUIRED_LABELS = {"submission", "approved"}
ASSISTED = "committee-assisted"
WRITERS = {"write", "maintain", "admin"}
EVENT = Path("submissions/event.json")


def gh_json(endpoint):
    return json.loads(subprocess.check_output(["gh", "api", endpoint], text=True))


def repository_writer(repository, login):
    permissions = gh_json(f"repos/{repository}/collaborators/{login}/permission")
    return permissions.get("permission") in WRITERS


def public_url(value):
    value = value.strip()
    if "://" not in value and not value.startswith(("/", "#", "?")):
        value = "https://" + value
    try:
        if len(value) > 2048 or re.search(r"[\s<>\\\x00-\x1f\x7f]", value):
            raise ValueError
        url = urlsplit(value)
        host = (url.hostname or "").encode("idna").decode("ascii")
        if (url.scheme != "https" or url.username is not None or url.password is not None
                or url.port not in {None, 443} or not re.fullmatch(r"[a-z0-9.-]+\.[a-z][a-z0-9-]*", host)
                or host.endswith((".localhost", ".local"))):
            raise ValueError
    except ValueError:
        raise ValueError("Use a public HTTPS URL without embedded credentials.") from None
    return value


def public_game_url(value):
    value = public_url(value)
    url = urlsplit(value)
    share_prefix = {
        "gemini.google.com": "/share/",
        "g.co": "/gemini/share/",
        "share.gemini.google": "/",
    }.get(url.hostname)
    if share_prefix:
        share_id = url.path.removeprefix(share_prefix).rstrip("/")
        if not url.path.startswith(share_prefix) or not re.fullmatch(r"[A-Za-z0-9_-]+", share_id):
            raise ValueError("In Gemini Canvas, choose Share, then Copy link. Paste the public share link.")
    elif (url.hostname in {"google.com", "www.google.com"} and url.path.rstrip("/") == "/url"
            or url.hostname == "github.com"):
        raise ValueError("Paste the direct link to play the game, rather than a redirect or GitHub repository.")
    return value


def extract_fields(body, labels):
    remaining = body.replace("\r\n", "\n").lstrip()
    values = []
    for index, label in enumerate(labels):
        heading = "### " + label + "\n"
        if not remaining.startswith(heading):
            raise ValueError("Use the repository's Submit Your Build issue form.")
        remaining = remaining[len(heading):]
        if index == len(labels) - 1:
            values.append(remaining.strip())
        else:
            next_heading = "\n### " + labels[index + 1] + "\n"
            value, marker, remainder = remaining.partition(next_heading)
            if not marker:
                raise ValueError("The issue form is missing a field.")
            values.append(value.strip())
            remaining = marker[1:] + remainder
    return values


def parse_submission(issue, repository):
    github = issue["user"]["login"]
    if issue["user"]["type"] != "User" or not HANDLE.fullmatch(github):
        raise ValueError("Submissions must come from a GitHub user account.")
    assisted = ASSISTED in label_names(issue)
    is_writer = repository_writer(repository, github)
    if is_writer and not assisted:
        raise ValueError("Committee submissions need the committee-assisted label before approval.")
    if assisted and not is_writer:
        raise ValueError("Ask a committee member with write access to file this assisted submission.")
    identifier = f"entry--{issue['number']}" if assisted else github.lower()
    body = issue["body"] or ""
    legacy = body.lstrip().startswith("### Build Title\n") or body.lstrip().startswith("### Build Title\r\n")
    extras = {}
    if legacy:
        title, builder, linkedin, track, prompt, game_url = extract_fields(body, LEGACY_LABELS)
        if track not in TRACKS:
            raise ValueError("The original issue form is missing a valid track.")
        extras["track"] = TRACKS[track]
        if linkedin not in {"", "_No response_"}:
            linkedin_url = public_url(linkedin)
            if urlsplit(linkedin_url).hostname not in {"linkedin.com", "www.linkedin.com"}:
                raise ValueError("The optional LinkedIn URL must use linkedin.com.")
            extras["linkedin"] = linkedin_url
    else:
        builder, prompt, game_url = extract_fields(body, LABELS)
        title = issue["title"].removeprefix("[Game]").strip()
    if not (0 < len(title) <= 100 and 0 < len(builder) <= 100 and 0 < len(prompt) <= 1500
            and all(value != "_No response_" for value in (title, builder, prompt))
            and all("\n" not in value for value in (title, builder))):
        raise ValueError("Check the game title, team name and your AI request.")
    row = {
        "id": identifier, "kind": "submission", "title": title, "builder": builder,
        "github": github, "prompt": prompt, "issue": issue["number"],
        "url": public_game_url(game_url), **extras,
    }
    if assisted:
        row["assisted"] = True
    return row


def record_submission(row):
    manifest = json.loads(MANIFEST.read_text())
    if manifest.get("version") != 1 or not isinstance(manifest.get("builds"), list):
        raise ValueError("The existing manifest must use schema version 1.")
    rows = manifest["builds"]
    identifier = row["id"]
    for index, current in enumerate(rows):
        # Replace the old row if an already-published issue is corrected to assisted.
        if current["id"] != identifier and current.get("issue") != row["issue"]:
            continue
        if current["kind"] != "submission":
            raise ValueError("This GitHub handle is reserved by a curated build.")
        if current["issue"] > row["issue"]:
            raise ValueError("A newer submission from this GitHub account is already in the gallery.")
        if current.get("winner") is True:
            row["winner"] = True
        rows[index] = row
        break
    else:
        rows.append(row)
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def label_names(issue):
    return {label["name"] for label in issue["labels"]}


def ensure_pending():
    if json.loads(EVENT.read_text())["state"] != "pending":
        raise ValueError("The submission list is locked for the audience ballot.")


def approve_issue(repository, event):
    issue = event["issue"]
    number = int(issue["number"])
    current = gh_json(f"repos/{repository}/issues/{number}")
    approval_labels = REQUIRED_LABELS | {ASSISTED}
    approved_labels = label_names(issue) & approval_labels
    current_labels = label_names(current) & approval_labels
    if (current["state"] != "open" or not REQUIRED_LABELS.issubset(approved_labels)
            or current_labels != approved_labels or issue["body"] != current["body"]
            or issue["title"] != current["title"]):
        raise ValueError("The submission changed, closed or lost approval. Review it and apply approved again.")
    ensure_pending()
    return publish_row(current, repository)


def publish_assisted(repository, numbers):
    ensure_pending()
    if not re.fullmatch(r"\s*[1-9][0-9]*(?:[,\s]+[1-9][0-9]*)*\s*", numbers):
        raise ValueError("Enter issue numbers separated by spaces or commas, for example 12, 13.")
    issues = list(dict.fromkeys(map(int, re.findall(r"[0-9]+", numbers))))
    if len(issues) > 30:
        raise ValueError("Publish up to 30 assisted issues in one batch.")
    results = []
    for number in issues:
        try:
            issue = gh_json(f"repos/{repository}/issues/{number}")
        except subprocess.CalledProcessError:
            results.append({"issue": number, "error": "Could not read this issue.", "silent": True})
            continue
        if "pull_request" in issue or issue["state"] != "open" or not {"submission", ASSISTED} <= label_names(issue):
            results.append({"issue": number, "error": "Use an open committee-assisted build issue.", "silent": True})
            continue
        results.append(review(number, lambda: publish_row(issue, repository), assisted=True))
    return results


def publish_row(issue, repository):
    row = parse_submission(issue, repository)
    record_submission(row)
    return row["id"]


def review(number, publish, assisted=False):
    try:
        build = publish()
    except ValueError as error:
        return {"issue": number, "error": str(error)}
    return {"issue": number, "build": build, "assisted": assisted}


def main():
    repository = os.environ["GITHUB_REPOSITORY"]
    event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())
    sender = event["sender"]
    if sender["type"] != "User" or not HANDLE.fullmatch(sender["login"]):
        raise ValueError("A repository maintainer must approve submissions.")
    if not repository_writer(repository, sender["login"]):
        raise ValueError("Applying approval requires write access to the repository.")
    if event.get("action") == "labeled" and event["label"]["name"] == "approved":
        number = int(event["issue"]["number"])
        results = [review(number, lambda: approve_issue(repository, event))]
    elif event.get("inputs", {}).get("operation") == "publish-assisted":
        results = publish_assisted(repository, event["inputs"]["issue_numbers"])
    else:
        raise ValueError("Use an approved label event or the publish-assisted operation.")
    for result in results:
        outcome = result.get("build") or result["error"]
        print(f"Issue #{result['issue']}: {outcome}")
    with Path(os.environ["JAM_REVIEW_RESULTS"]).open("w", encoding="utf-8") as output:
        json.dump(results, output, ensure_ascii=True)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        print(error, file=sys.stderr)
        sys.exit(1)
