import { drawQr } from "./qr.js";
import { loadEvent, repository } from "./state.js";

const byId = (id) => document.getElementById(id);
const form = byId("vote-form");
const choices = byId("choices");
const comment = byId("comment");
const cast = byId("cast");
const resultList = byId("results");
const status = byId("status");
const projectorStatus = byId("projector-status");
const projector = new URLSearchParams(location.search).has("projector");
byId("ballot").hidden = projector;
byId("projector").hidden = !projector;
const ballotUrl = new URL("vote.html", location.href).href;
const qr = byId(projector ? "projector-qr" : "share-qr");
qr.hidden = !drawQr(qr, ballotUrl);

const full = byId("fullscreen");
if (document.fullscreenEnabled) {
  full.hidden = false;
  full.addEventListener("click", async () => {
    try {
      if (document.fullscreenElement) await document.exitFullscreen();
      else await document.documentElement.requestFullscreen();
    } catch {
      full.textContent = "Use browser fullscreen";
    }
  });
  document.addEventListener("fullscreenchange", () => {
    full.textContent = document.fullscreenElement ? "Exit fullscreen" : "Fullscreen";
  });
}

function element(tag, text) {
  const node = document.createElement(tag);
  if (text) node.textContent = text;
  return node;
}

function galleryLink(candidate) {
  return `showcase.html?build=${encodeURIComponent(candidate.id)}`;
}

function renderChoices(event) {
  for (const candidate of event.candidates) {
    const row = element("div");
    row.className = "choice";
    const radio = element("input");
    radio.type = "radio";
    radio.name = "build";
    radio.id = "candidate-" + candidate.id;
    radio.value = candidate.id;
    radio.required = true;
    const label = element("label", candidate.title);
    label.htmlFor = radio.id;
    label.append(element("small", candidate.builder));
    const play = element("a", "Play ↗︎");
    play.href = galleryLink(candidate);
    play.target = "_blank";
    play.rel = "noopener";
    play.setAttribute("aria-label", "Play " + candidate.title + " in a new tab");
    row.append(radio, label, play);
    choices.append(row);
  }
  cast.href = repository + "/issues/" + event.issue;
}

form.addEventListener("change", () => { byId("vote-code").hidden = true; });
form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const build = new FormData(form).get("build");
  if (!build) return;
  comment.value = "Vote: " + build;
  byId("vote-code").hidden = false;
  try {
    await navigator.clipboard.writeText(comment.value);
    byId("copy-note").textContent = "Vote copied. Continue to GitHub and post it.";
  } catch {
    byId("copy-note").textContent = "Copy the selected line, then continue to GitHub.";
    comment.select();
    return;
  }
  cast.focus();
});

function renderResults(event) {
  const ranked = [...event.candidates].sort((a, b) => event.counts[b.id] - event.counts[a.id]);
  resultList.replaceChildren(...ranked.map((candidate) => {
    const count = event.counts[candidate.id];
    const result = element("li", `${candidate.title} · ${count} ${count === 1 ? "vote" : "votes"}`);
    if (event.awards?.audience?.includes(candidate.id)) result.append(" · People’s Choice");
    return result;
  }));
}

let rendered;
async function refresh() {
  try {
    const event = await loadEvent();
    const key = JSON.stringify(event);
    if (rendered === key) return;
    const open = event.state === "open";
    const closed = event.state === "closed";
    status.textContent = open ? "Voting is open."
      : closed ? "Voting is closed."
      : "Voting opens once the committee has checked the submitted builds.";
    projectorStatus.textContent = open ? "Choose your favourite build and cast your vote on GitHub."
      : closed ? "Voting has closed. Scan to see the results."
      : "Scan to open the ballot. Voting starts after the demos.";
    choices.replaceChildren();
    form.hidden = !open;
    byId("vote-code").hidden = true;
    resultList.hidden = !closed;
    if (open) renderChoices(event);
    if (closed) renderResults(event);
    rendered = key;
  } catch {
    status.textContent = "Couldn’t load the ballot. This page will retry automatically.";
    projectorStatus.textContent = status.textContent;
    form.hidden = true;
    resultList.hidden = true;
    rendered = undefined;
  }
}

void refresh();
setInterval(refresh, 12000);
document.addEventListener("visibilitychange", () => {
  if (!document.hidden) void refresh();
});
