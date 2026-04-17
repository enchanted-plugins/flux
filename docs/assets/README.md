# docs/assets — rendered diagrams & equations

These SVGs are **pre-rendered** so GitHub's mobile app (which renders neither
` ```mermaid ` blocks nor `$$...$$` math) shows them correctly. README.md and
docs/science/README.md reference the files here as `<img>`.

## Files

| File | Source | Regenerate |
|------|--------|-----------|
| `pipeline.svg` | `pipeline.mmd` | `npx @mermaid-js/mermaid-cli -i pipeline.mmd -o pipeline.svg -c mermaid.config.json -b "#0d1117"` |
| `lifecycle.svg` | `lifecycle.mmd` | `npx @mermaid-js/mermaid-cli -i lifecycle.mmd -o lifecycle.svg -c mermaid.config.json -b "#0d1117"` |
| `math/*.svg` | `render-math.js` | `npm install --prefix . mathjax-full && node render-math.js` |

Run the commands from `docs/assets/` (paths are relative). The toolchain
(`node_modules/`, `package.json`, `package-lock.json`) is gitignored; only the
rendered SVGs and source files are committed.
