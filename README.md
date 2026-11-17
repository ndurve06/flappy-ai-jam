<div align="center">

# Flappy AI Jam

The 30-Minute AI Game Jam · Flappy Bird Edition

University of Portsmouth AI Society<br>
Thursday 19 November 2026 · 18:30–20:00

[![Forks](https://img.shields.io/github/forks/uopaisociety/flappy-ai-jam?style=flat-square&color=073B5C)](https://github.com/uopaisociety/flappy-ai-jam/network/members)
[![Stars](https://img.shields.io/github/stars/uopaisociety/flappy-ai-jam?style=flat-square&color=073B5C)](https://github.com/uopaisociety/flappy-ai-jam/stargazers)
[![Stack](https://img.shields.io/badge/stack-HTML5_Canvas_%7C_Vanilla_JS-073B5C?style=flat-square)](https://github.com/uopaisociety/flappy-ai-jam/blob/main/index.html)
[![Sprint](https://img.shields.io/badge/sprint-30_minutes-E6B325?style=flat-square&labelColor=073B5C)](https://github.com/uopaisociety/flappy-ai-jam)

[Play the starter](https://uopaisociety.github.io/flappy-ai-jam/) · [Event hub and Hall of Fame](https://uopaisociety.github.io/flappy-ai-jam/showcase.html)

[![Submit Your Build](https://img.shields.io/badge/Submit_Your_Build-Open_GitHub_Form-073B5C?style=flat-square)](https://github.com/uopaisociety/flappy-ai-jam/issues/new?template=submit-build.yml)

</div>

## Overview

One file. Thirty minutes. Turn this small Flappy Bird into a better game, or a stranger one, by talking to Gemini. You do not need to know how to code. First-years from any course and third-year computer science students start from the same file.

The whole game is [`index.html`](index.html), in the top folder of this repo. The live starter is already at <https://uopaisociety.github.io/flappy-ai-jam/>. Keep your game in that same file, in that same place, so your own link works the same way.

Nothing to install, and no local server. Gemini Canvas can run the file, and so can a double-click.

**Taking part?** Start with the [participant guide](https://uopaisociety.github.io/flappy-ai-jam/showcase.html#setup). Free Gemini Canvas is enough. If you’re using a phone or can’t sign in, ask at the help desk to join someone with a laptop.

## Publish your own copy on GitHub (optional)

If you want a public game link of your own, you can publish a copy from a web browser.

1. **Sign up or sign in.** Open [github.com/signup](https://github.com/signup) or [github.com/login](https://github.com/login). The buttons say **Sign up** and **Sign in**.
2. **Star.** On this page, click **Star** at the top right.
3. **Fork.** Click **Fork**, leave the boxes as they are, and click **Create fork**. GitHub copies the project to `github.com/<your-username>/flappy-ai-jam`. Click **Fork**, not **Use this template**, even if you see that button.
4. **Paste your game.** In **your** copy, open `index.html` and click the pencil icon (**Edit this file**). Select all (Ctrl+A, or Cmd+A on a Mac), delete, and paste the full file Gemini gave you. The prompt guide is [further down](#prompt-guide) if you have not made a version yet.
5. **Commit changes.** Click **Commit changes**. In the box that opens, leave **Commit directly to the `main` branch** selected, then click **Commit changes** again. A message like "Seagull edition" is enough.
6. **Turn on Pages.** In your copy, open **Settings**, then **Pages**. Under **Build and deployment**, choose **Deploy from a branch**. Set the branch to **main** and the folder to **/ (root)**. Click **Save**. Wait about a minute. The repo needs to stay public.
7. **Submit the link.** Your game is live at `https://<your-username>.github.io/flappy-ai-jam/`. Open it once. The address must contain your username, not `uopaisociety`. You can share that link or use it for a live demo. To enter the gallery, follow [Submission and judging](#submission-and-judging).

## No GitHub account?

Bring your game link, game name, team name and the request you sent to AI to the help desk. The committee can submit it for you. If sharing fails, bring your working preview or game file for a live demo. Ask for a paper slip to vote in the room.

## Repository architecture

```text
flappy-ai-jam/
├── index.html      standalone starter game
├── showcase.html   attendee guide, reference mods, gallery and awards
├── arcade.html     projector timer, demo queue and local judging
├── vote.html       audience ballot and projector QR
├── event/          shared branding and event page assets
└── submissions/    approved entries and published ballot state
```

Leave `index.html` in the top folder. GitHub Pages serves that folder from the `main` branch. If you move the file, your link stops working.

These comments in the file mark the parts Gemini should keep. They appear in this order:

- `CONFIG` — speeds, sizes, and colours. Change these numbers first.
- `PHYSICS` — gravity, the flap, and the short pause so a restart is not an accident.
- `PIPES / LEVEL` — where the gaps appear, and what counts as a hit.
- `GRAPHICS` — sky, pipes, ground, and the bird, drawn with shapes.
- `SCORE & GAME OVER` — the score, your best score, and the end screen.

## Quickstart

### Star and Fork

If you want a GitHub-hosted copy, follow [Publish your own copy on GitHub](#publish-your-own-copy-on-github-optional).

### Choose where you build

**Gemini Canvas (recommended).** Nothing to install.

1. Open the [participant guide](https://uopaisociety.github.io/flappy-ai-jam/showcase.html#setup) and select **Copy starter prompt**.
2. Open [Gemini](https://gemini.google.com), sign in and choose **Canvas** under **Tools**.
3. Paste into the chat and send it. Open **Preview** and play a round.
4. Ask for one change in the same chat and play again.

**On your own computer (optional).** Gemini Canvas is still the route for the evening. This path is only if you already work on your own machine.

Nothing to install if you just want to play: click **Code**, then **Download ZIP**, unzip, and double-click `index.html`. If you already use git, clone your fork and double-click the file:

```bash
git clone https://github.com/<your-username>/flappy-ai-jam.git
```

**VS Code or Zed (advanced).** Open that folder, edit `index.html`, save, and refresh the browser. Then use steps 5 to 7 above, or commit `index.html` and push to `main`.

**Antigravity IDE (advanced).** Google's desktop agentic IDE. Install it before Thursday from the [Google Antigravity download page](https://antigravity.google/download), not during the event. If it is already installed: clone your fork or open that folder, open `index.html`, and ask the agent with the same prompts A–D. Open `index.html` in a browser to preview, then commit and push to your fork.

## Prompt guide

Paste **Prompt A** first and wait until Gemini replies that it is ready. Then paste the whole `index.html`. After that, use B, C, or D, or write your own. Every reply should be the full file.

### Prompt A: Ground rules

```text
You are my game developer for a 30-minute game jam. I will give you a complete single-file
HTML5 Canvas game (index.html). Rules for EVERY reply:
1. Always return the FULL, complete, working index.html in one code block, from <!DOCTYPE html>
   to </html>. Never truncate. Never write "rest of code unchanged", "...", or "same as before".
2. Keep everything in ONE file: HTML, CSS and JavaScript together. No external files, images,
   libraries, CDNs, fonts or npm packages. Draw everything with Canvas shapes. Emoji are fine.
3. Keep the "// === AI PROMPT ZONE: ... ===" comments so the code stays easy to edit.
4. Keep the controls working: Space, arrow up, mouse click and touch (phones). The page must
   fit the window, remember the best score, and wait a short moment before a restart counts.
5. Check that your code has no errors before replying. Then add a 2-line summary of what changed.
Reply "Ready" and wait for my code.
```

### Prompt B: Make it look like a different game

Swap the theme for anything you like. A lecture you are late for, your cat, a game you already love. This example is Portsmouth. Gameplay stays the same.

```text
Reskin this game into "Flappy Seagull: Portsmouth Edition". The bird becomes a cheeky seagull
(drawn with Canvas shapes) that has just stolen a chip. Pipes become the Spinnaker Tower and
stacks of Southsea deckchairs. Background: a sunset over the Solent, with the Isle of Wight
as a silhouette and a ferry scrolling past. Rename the title, the start screen and the game
over text to match ("You dropped your chip!"). Keep the gameplay the same. Return the FULL index.html.
```

### Prompt C: New ways to play

```text
Add new gameplay. Keep it fair for someone playing for the first time.
- 3 lives, shown as hearts. Hitting a pipe loses a life, then the bird flashes and cannot be hit for 1.5 seconds.
- Power-ups that float through the gaps: a shield (one free hit), slow motion for 5 seconds,
  and a tiny-bird shrink for 5 seconds. Give each one its own colour and a short label.
- A combo: pass pipes without flapping too often and the score builds to x2, x3 and x4.
- Every 10 points, a large obstacle appears on the right and shoots slow projectiles for 10 seconds.
Return the FULL index.html.
```

### Prompt D: Make it feel good

```text
Make the game feel satisfying to play:
- Bursts of particles when the bird flaps, when you score, and when you crash.
- A short screen shake and a quick white flash on a crash.
- Sounds made only with the Web Audio API (no audio files): a flap, a score ding, a crash,
  and a simple tune that loops and starts on the first click or tap.
- Three background layers that scroll at different speeds.
- The bird squashes and stretches when it flaps. The start screen has a small bounce, and the score pops.
- A mute control on the M key, and a speaker mark you can tap.
Return the FULL index.html.
```

### If Gemini breaks the game

```text
The game is broken. Here is what happens: [describe it, for example "black screen" or "the bird does not move"].
Here is the error from the browser console: [paste the red text].
Fix only that bug, keep every feature, and return the FULL working index.html.
```

- To see the error, press **F12** (on a Mac, **Cmd + Option + I**) and open **Console**. Copy the red text into the prompt above.
- If the reply stops halfway, say: "You cut the file short. Send the FULL file again."
- After two failed fixes, go back to the last version that worked. Scroll up in Gemini, or open your last commit, and ask for a smaller change.
- Save every version that runs. Commit it as you go, so you always have something to hand in.

## Submission and judging

In the room, bring your game link, display name, game name and AI request to the help desk. You can also use [Submit Your Build](https://github.com/uopaisociety/flappy-ai-jam/issues/new?template=submit-build.yml) while signed in to GitHub. A share link from Gemini Canvas, GitHub Pages or another public HTTPS host works. The game, display name and AI request appear in the public gallery after review. GitHub submissions receive a reply with the gallery link when deployment completes.

If the preview is blocked, select **Open game in new tab**. For an updated game, tell the help desk or submit a new issue online. The newest approved online submission per GitHub account owns that account’s gallery link.

| Category | What it rewards | How we judge it |
| --- | --- | --- |
| Best Engineered | Technical execution | The game runs, the new ideas work, and the build is the strongest in the room. |
| Most Unhinged Prompt | Creative prompting | The idea is bold and the prompts are specific. No coding is required, so this category is open to everyone. |
| People's Choice | The room vote | The audience votes once on paper or with a GitHub account. Combined votes decide the award. |

## Hall of Fame

Open the [live gallery](https://uopaisociety.github.io/flappy-ai-jam/showcase.html) or run `python3 -m http.server 8000` in the repository root and open <http://localhost:8000/showcase.html>. You can double-click any example file for standalone play.

| Reference mod | Quick preview |
| --- | --- |
| [Autonomous Trajectory Solver](examples/01-neural-autopilot.html) | Press **A** or tap **Autopilot** to launch and draw the flight plan. |
| [Acoustic Pitch Controller](examples/02-voice-frequency-thruster.html) | Open standalone on HTTPS or localhost, choose **Enable mic**, launch, and try voice pulses or whistles. **Space** and tap also work. |
| [Overclock Boss Protocol](examples/03-overclock-boss-protocol.html) | Choose **Boss practice** for an immediate encounter. Press **Shift** or tap **Dash**. Normal flights encounter the boss every 10 points. |

### Committee run of show

**Before doors open.** Have one host manage the projector and demos and a second person cover the help desk and approvals. Open the [participant guide](https://uopaisociety.github.io/flappy-ai-jam/showcase.html) on a signed-out phone. Test the QR from the back row, paste the starter into a fresh Canvas chat, and check a real Canvas share link in a private browser before the session. Keep `index.html` and the example games downloaded, and bring blank paper slips for voting. Check **Settings → Pages → Source** uses **GitHub Actions** or **main / (root)**, then use `deploy` in [Publish Jam Showcase](https://github.com/uopaisociety/flappy-ai-jam/actions/workflows/publish-submission.yml) on `main` to publish and create the labels.

| Time (UK) | What to do |
| --- | --- |
| 18:30–18:45 | Show the [projector timer](https://uopaisociety.github.io/flappy-ai-jam/arcade.html). Its first QR leads to setup. Play the original together, show how to send one request, and wait until beginners can flap and restart in Preview. Help people without a working laptop or login pair up. |
| 18:45–19:15 | Start the 30-minute clock. The timer changes to the hand-in QR at five minutes left. Ask people to keep a playable version and get their share link ready. |
| 19:15–19:25 | Help desk checks links in a private browser and submits for anyone without GitHub. Log each team, title, AI request and link. On assisted issues apply `committee-assisted` before `approved`. For online issues, check the details and apply `approved`. Keep a local demo queue if publication is slow. |
| 19:25–19:45 | Select **Demo queue → Queue approved builds**. Open each game and invite a quick walk-through of what changed. Open Gemini Canvas links in an external tab if the preview frame doesn’t work. Play local files or screen-share working previews for teams that need a hand with sharing. |
| 19:45–19:52 | Once the final approved game is visible, run `open-voting` to freeze the ballot. Show the [projector ballot](https://uopaisociety.github.io/flappy-ai-jam/vote.html?projector) and its game numbers. Offer a paper slip or the QR for online voting. Ask people to choose one route. |
| 19:52–20:00 | Count slips by ballot number. Run `close-voting` with `paper_votes` such as `1=4, 2=3`. Enter both committee award picks as ballot numbers such as `#2`, or as build IDs, to publish all three awards in the same run. Once it deploys, show the [awards page](https://uopaisociety.github.io/flappy-ai-jam/showcase.html#winners). |

**If something fails**

- **Canvas unavailable or share link private.** Pair the attendee with someone who can open Canvas, or demo from a working preview or exported file. A playable public link is needed for the online gallery and ballot. Ask before publishing a game or name on someone’s behalf.
- **Issue edited after approval.** Recheck the title, request and link, then remove and reapply `approved`. If the queue is slow, demo from local files or direct links during the wait.
- **Vote site slow.** Read the ballot numbers from the `open-voting` workflow log and write them on the board. Start with paper while the page catches up. If GitHub is unavailable, record one paper choice per person against a local team and title list, then match those titles to the approved ballot when publishing. If there are no eligible entries, skip the ballot and play the examples.
- **Results still publishing or committee undecided.** Close the ballot with the paper tally. You can run `publish-winners` afterwards for the two committee picks. A People’s Choice tie shares the award. Local judging scores can be exported from the projector.

The participant pages have no host controls. Repository write access is required to approve submissions and operate the ballot. A paper slip is counted alongside online ballots. Online repeats are reduced to the latest valid vote per GitHub account. Ask the room to use one route, and hand out one slip per attendee.

### Shared event page styles

Future event pages can import `event/brand/shell.css` for the join-page header and background. It includes `event/brand/tokens.css`. Use the `.society-header` and `.ambient` markup from `showcase.html` and link `event/brand/icon.svg` for the theme-aware favicon. Add `data-animate` to the body when the page benefits from the 32-second drift. The CSS respects reduced motion. `event/site.css` supplies the event hub and ballot layouts. The starter requires only its own HTML.

## About the society

University of Portsmouth AI Society. Free to join, for every course and every level.

[GitHub](https://github.com/uopaisociety) · [Instagram](https://instagram.com/uopaisociety) · [X](https://x.com/uopaisociety) · [Luma](https://luma.com/uopaisociety) · [LinkedIn](https://linkedin.com/company/aisocietyuop) · [aisociety@upsu.net](mailto:aisociety@upsu.net)

If you post your game, tag @uopaisociety and use #FlappyAIJam.
