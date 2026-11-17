export const repository = "https://github.com/uopaisociety/flappy-ai-jam";
export const awardNames = {
  technical: "Best Engineered",
  creative: "Most Unhinged Prompt",
  audience: "People’s Choice",
};

export async function loadEvent() {
  const response = await fetch("submissions/event.json", { cache: "no-cache" });
  if (!response.ok) throw new Error("Event status unavailable");
  const event = await response.json();
  if (!["pending", "open", "closed"].includes(event.state)) throw new Error("Unknown ballot state");
  return event;
}

export function awardsFor(event, build) {
  if (build.kind !== "submission") return [];
  const byCategory = Object.entries(awardNames)
    .filter(([key]) => event?.awards?.[key]?.includes(build.id))
    .map(([, name]) => name);
  return !byCategory.length && build.winner === true ? ["Event winner"] : byCategory;
}

export async function loadManifest() {
  const response = await fetch("submissions/manifest.json", { cache: "no-cache" });
  if (!response.ok) throw new Error("Manifest unavailable");
  const manifest = await response.json();
  if (manifest.version !== 1 || !Array.isArray(manifest.builds)) {
    throw new Error("Unsupported manifest");
  }
  return manifest.builds;
}

export function publicGameUrl(value) {
  if (typeof value !== "string" || value.length > 2048 || /[\s<>\\\x00-\x1f\x7f]/u.test(value)) return "";
  try {
    const url = new URL(value);
    return url.protocol === "https:" && !url.username && !url.password && !url.port
      && /^[a-z0-9.-]+\.[a-z][a-z0-9-]*$/.test(url.hostname)
      && !url.hostname.endsWith(".localhost") && !url.hostname.endsWith(".local") ? url.href : "";
  } catch {
    return "";
  }
}
