// Rasterize story scene SVGs to PNG with headless Chromium (Playwright).
// Usage: node tools/svg2png.mjs <out_dir> <scale> <defs.svg|-> <scene1.svg> [scene2.svg ...]
// Each scene is drawn on a 1080x1920 canvas; `scale` > 1 leaves headroom for camera moves.
import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

const [outDir, scaleArg, defsPath, ...scenes] = process.argv.slice(2);
const scale = Number(scaleArg || 1.2);
const fontsDir = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..", "assets", "fonts");
const font = (family, file, weight = 400) =>
  `@font-face{font-family:'${family}';src:url('${pathToFileURL(path.join(fontsDir, file))}');font-weight:${weight};}`;
const css = [
  font("Marker", "permanent-marker-latin-400-normal.woff2"),
  font("Typewriter", "special-elite-latin-400-normal.woff2"),
  font("Oswald", "oswald-latin-400-normal.woff2", 400),
  font("Oswald", "oswald-latin-700-normal.woff2", 700),
  "html,body{margin:0;padding:0;background:#000;overflow:hidden}",
  "svg.scene{display:block;width:1080px;height:1920px}",
].join("\n");
const defs = defsPath && defsPath !== "-" ? fs.readFileSync(defsPath, "utf8") : "";

fs.mkdirSync(outDir, { recursive: true });
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: scale });
for (const scene of scenes) {
  const svg = fs.readFileSync(scene, "utf8").replace("<svg", '<svg class="scene"');
  const html = `<!doctype html><html><head><meta charset="utf-8"><style>${css}</style></head><body>
<svg width="0" height="0" style="position:absolute">${defs}</svg>${svg}</body></html>`;
  const tmp = path.join(outDir, ".render.html");
  fs.writeFileSync(tmp, html);
  await page.goto(pathToFileURL(tmp).href);
  await page.evaluate(() => document.fonts.ready);
  const out = path.join(outDir, path.basename(scene).replace(/\.svg$/, ".png"));
  await page.screenshot({ path: out, clip: { x: 0, y: 0, width: 1080, height: 1920 } });
  fs.unlinkSync(tmp);
  console.log(out);
}
await browser.close();
