# Flappy AI Jam committee runbook

[Participant guide](https://uopaisociety.github.io/flappy-ai-jam/showcase.html) · [Projector timer and demo queue](https://uopaisociety.github.io/flappy-ai-jam/arcade.html) · [Publishing and voting](https://github.com/uopaisociety/flappy-ai-jam/actions/workflows/publish-submission.yml) · [Individual approval runs](https://github.com/uopaisociety/flappy-ai-jam/actions/workflows/review-submission.yml)

## Before 18:30

- Put two people with GitHub write access on hand-in and approvals if possible. Ask the host to run the projector and pair up anyone without a laptop or a Gemini login. Keep a spare device available if you have one.
- Check the venue Wi-Fi, scan the projector QR from the back row, and open a real Canvas share link on the projector and on a phone in a private browser window. If you test a university Google account, check both Canvas access and whether the share link plays while signed out. Recommend a personal Google account and use free Gemini.
- Download the starter and examples and bring blank slips. Check **Settings → Pages → Source** uses **GitHub Actions** or **main / (root)**. Running `deploy` on `main` creates missing labels and refreshes the site.
- Set up a shared hand-in log with the headers below. Keep it open on both desk laptops and on the projector laptop. Use a team display name and check the team agrees to publish its details.

```text
Paper number    Team    Game title    AI request    Game link or local file    Issue #    Status
```

## In the room

| Time (GMT) | What to do |
| --- | --- |
| 18:30–18:45 | Show the setup QR. Play one round, show the **Copy starter prompt** button and check people can flap and restart in Canvas Preview. |
| 18:45–19:05 | Start the 30-minute timer. Encourage one small change and a playtest. |
| 19:05–19:25 | When the QR switches to hand-in, check links and start the desk log. Accept working previews or local files for demos. |
| 19:25–19:45 | Demo from the log. Use **Demo queue → Queue link** or attach a local HTML file. Open Canvas shares in a browser tab. |
| 19:45–19:52 | Run the vote. Choose the paper fallback below if publishing is still catching up. |
| 19:52–20:00 | Count the slips, announce the awards and publish the results if the gallery is ready. |

## Hand in, review and publish

1. Play each link in a private browser window. Ask for the link from **Share → Copy link** if someone provides their private Gemini chat. Log the team, title, short AI request and link while the attendee is with you.
2. For help-desk entries, use the [committee-assisted issue form](https://github.com/uopaisociety/flappy-ai-jam/issues/new?template=committee-assisted.yml). It applies `submission` and `committee-assisted` together. For existing committee issues, add `committee-assisted` before approving. Each assisted game gets its own `entry--<issue-number>` ID.
3. When several assisted issues are ready, run `publish-assisted` on `main` and enter the issue numbers, for example `12, 13, 14`. This publishes the checked games with one Pages deployment. For one assisted entry or a standard participant issue, a writer can apply `approved` after review.
4. Check **Actions** and the issue. The bot puts the gallery link or validation feedback on the issue. If something needs editing, fix it, then remove and reapply `approved` or resubmit the issue number in a batch. Demo directly from the log if Pages is still deploying. Keep a submission issue open until its game appears. Closing it after publication preserves the gallery entry and moves the thread to the [Closed list](https://github.com/uopaisociety/flappy-ai-jam/issues?q=is%3Aissue+is%3Aclosed).

## Vote and publish awards

The live test submission took 57 seconds from approval to the bot’s gallery reply. Allow about a minute each for opening the online ballot and publishing results once the queue is free. If the room is ready to vote while Pages is still updating, use the numbered desk log and paper slips.
- **Gallery ready.** Once all eligible games appear, run `open-voting` to freeze the list. Project the [ballot and game numbers](https://uopaisociety.github.io/flappy-ai-jam/vote.html?projector). Tick `paper_only` when opening if everyone in the room will vote on paper. In a mixed ballot, ask each attendee to choose paper or GitHub and give out one slip per person.
- **Gallery still updating.** Give each eligible game a fixed number in the desk log, display the numbered game list and take one paper vote per person. Keep the tally and announce the result in the room. Once the gallery is ready, run `open-voting` with `paper_only` enabled. Match each team's paper number to the corresponding build in the workflow's ballot list before entering the tally. Keep the room result in the log if a winner's game could only be shown locally.
- **Close and publish.** Run `close-voting`. Enter totals as `1=4, 2=3` using the numbers printed by `open-voting`. Enter both committee award picks as `#2` or a build ID, or leave both blank and run `publish-winners` later. A tie shares People’s Choice. If there are no eligible games, skip the ballot.

## If setup runs into trouble

- A cut-off or broken Canvas edit: use the last working HTML in a fresh chat and ask for one small change.
- A sign-in or usage limit: pair up, or try [AI Studio Build mode](https://aistudio.google.com/learn/ai-app-builder).
- A Pages fork that is still building: take the Canvas link or demo the local HTML.
- A share link that needs sign-in or shows code on the projector: show the working Canvas preview from the participant’s laptop, or copy the full HTML into a plain-text file called `index.html`, test it in the browser, and use **Demo queue → Add HTML**.
