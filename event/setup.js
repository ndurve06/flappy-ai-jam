const copyStarter = document.getElementById("copy-starter");
const starterStatus = document.getElementById("starter-status");

async function loadStarter() {
  try {
    const response = await fetch("index.html");
    if (!response.ok) throw new Error("Starter unavailable");
    const html = await response.text();
    const prompt = "Open this complete HTML game in Gemini Canvas and show a playable preview. Keep the game as it is for now. Follow the rules at the top of the file for all later edits.\n\n" + html;
    copyStarter.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(prompt);
        starterStatus.textContent = "Copied. Open Gemini, choose Canvas, then paste into the chat.";
      } catch {
        const field = document.getElementById("starter-prompt");
        field.value = prompt;
        document.getElementById("starter-fallback").hidden = false;
        field.focus();
        field.select();
        starterStatus.textContent = "Copy the selected text, then paste it into Gemini Canvas.";
      }
    });
    copyStarter.hidden = false;
  } catch {
    document.getElementById("starter-manual").hidden = false;
    starterStatus.textContent = "Automatic copy is unavailable. Copy it manually or ask the help desk for the game file.";
  }
}

void loadStarter();

const sampleButton = document.querySelector("[data-copy]");
sampleButton.hidden = false;
sampleButton.addEventListener("click", async () => {
  const sample = document.getElementById(sampleButton.dataset.copy);
  const status = document.getElementById("change-status");
  try {
    await navigator.clipboard.writeText(sample.textContent);
    status.textContent = "Copied. Paste it into the same Canvas chat.";
  } catch {
    const range = document.createRange();
    range.selectNodeContents(sample);
    const selection = window.getSelection();
    selection.removeAllRanges();
    selection.addRange(range);
    status.textContent = "Copy the highlighted example, then paste it into Canvas.";
  }
});
