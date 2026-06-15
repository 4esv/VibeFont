"""Write the static specimen page next to the built fonts."""

from __future__ import annotations

from pathlib import Path

from eslop.skeletons import GLYPHS
from eslop.styles import BUILD_ORDER, FAMILIES

PANGRAM = "Sphinx of black quartz, judge my vow."

BLURBS = {
    "billboard": "Headlines so heavy they qualify as infrastructure. "
                 "Counters were preserved wherever the math allowed.",
    "default": "A geometric sans assembled from first principles by "
               "something that has only ever read about geometry.",
    "serious": "Slab serifs detected automatically at every vertical "
               "terminal. Some of them are even in the right places.",
    "code": "Exactly 600 units per glyph, no exceptions, no favorites. "
            "The i got a serif so it would stop looking lonely.",
    "friendly": "Bottom-weighted, gently wobbly, every letter bounced by "
                "a fixed random seed. The b and the d wobble differently "
                "on purpose — mirror twins confuse readers.",
}

CSS_NAMES = {
    "billboard": "Eslop Billboard", "default": "Eslop Default",
    "serious": "Eslop Serious", "code": "Eslop Code",
    "friendly": "Eslop Friendly",
}


def _charset_html() -> str:
    chars = sorted((c for c in GLYPHS if c != " "), key=ord)
    return "".join(
        f"<span>{c.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')}</span>"
        for c in chars)


def write_specimen(out: Path) -> None:
    faces, sections = [], []
    for key in BUILD_ORDER:
        fam = FAMILIES[key]
        file = f"{fam.name.replace(' ', '')}-Regular"
        faces.append(f"""
@font-face {{
  font-family: '{fam.name}';
  src: url('{file}.woff2') format('woff2'),
       url('{file}.ttf') format('truetype');
  font-weight: {fam.weight_class};
  font-display: swap;
}}""")
        sections.append(f"""
<section id="{key}">
  <header>
    <h2>{fam.name}</h2>
    <p class="tag">{fam.tagline}</p>
  </header>
  <p class="hero" style="font-family:'{fam.name}'">{PANGRAM}</p>
  <p class="alphabet" style="font-family:'{fam.name}'">ABCDEFGHIJKLMNOPQRSTUVWXYZ<br>
  abcdefghijklmnopqrstuvwxyz<br>0123456789 !?&amp;@#$%*()[]&#123;&#125;</p>
  <p class="body-sample" style="font-family:'{fam.name}'">{BLURBS[key]}</p>
  <div class="charset" style="font-family:'{fam.name}'">{_charset_html()}</div>
  <pre>font-family: '{fam.name}';  /* {file}.woff2 */</pre>
</section>""")

    html = f"""<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Eslop — fonts by an AI, flaws included</title>
<style>
{''.join(faces)}
:root {{ --ink: #111; --paper: #fff; --rule: #111; }}
* {{ margin: 0; box-sizing: border-box; }}
body {{
  background: var(--paper); color: var(--ink);
  font-family: 'Eslop Default', sans-serif;
  max-width: 64rem; margin: 0 auto; padding: 2rem 1.25rem 6rem;
}}
h1 {{ font-family: 'Eslop Billboard'; font-size: clamp(3rem, 11vw, 7rem);
     line-height: .95; letter-spacing: .01em; }}
.sub {{ font-family: 'Eslop Code', monospace; margin: 1rem 0 0;
        font-size: .95rem; }}
.story {{ font-family: 'Eslop Serious'; font-size: 1.2rem; line-height: 1.55;
          margin: 2.5rem 0; max-width: 46rem; }}
.story em {{ font-family: 'Eslop Friendly'; font-style: normal; }}
section {{ border-top: 4px solid var(--rule); margin-top: 3.5rem;
           padding-top: 1.25rem; }}
section header {{ display: flex; justify-content: space-between;
                  flex-wrap: wrap; gap: .5rem; align-items: baseline; }}
h2 {{ font-size: 1.4rem; }}
.tag {{ font-family: 'Eslop Code', monospace; font-size: .85rem; }}
.hero {{ font-size: clamp(1.8rem, 5.5vw, 3.4rem); line-height: 1.15;
         margin: 1.5rem 0; }}
.alphabet {{ font-size: 1.5rem; line-height: 1.5; margin: 1rem 0;
             word-break: break-all; }}
.body-sample {{ font-size: 1.05rem; line-height: 1.6; max-width: 42rem;
                margin: 1rem 0; }}
.charset {{ display: grid; grid-template-columns: repeat(auto-fill, 2.6rem);
            gap: 2px; margin: 1.25rem 0; }}
.charset span {{ border: 1px solid #ddd; height: 2.6rem; display: grid;
                 place-items: center; font-size: 1.3rem; }}
pre {{ font-family: 'Eslop Code', monospace; background: #f4f4f4;
       padding: .6rem .8rem; font-size: .85rem; overflow-x: auto; }}
footer {{ border-top: 4px solid var(--rule); margin-top: 4rem;
          padding-top: 1.5rem; font-size: .95rem; line-height: 1.6; }}
footer p {{ margin-bottom: .6rem; }}
a {{ color: inherit; }}
</style>

<h1>Eslop</h1>
<p class="sub">five fonts // one transformer // zero supervision // OFL-1.1</p>

<p class="story">Eslop is what happens when you let a language model run a
type foundry. Every curve was chosen by something that has never held a
pen, squinted at a street sign, or kerned in anger — just coordinates and
<em>considerable optimism</em>. The flaws are not bugs; they are
provenance. Install them, ship them, judge them. They are free, because
charging money would invite questions.</p>

{''.join(sections)}

<footer>
  <p><strong>Install:</strong> download the .ttf, double-click, press the
  button that says install. Your OS has been pretending fonts are scary
  for decades.</p>
  <p><strong>Web:</strong> ship the .woff2 files and the
  <code>@font-face</code> blocks above.</p>
  <p><strong>License:</strong> SIL Open Font License 1.1 — free for any
  use, embedding allowed, fsType 0, no strings. See OFL.txt.</p>
  <p><strong>Provenance:</strong> designed and built end-to-end by Claude
  (an AI by Anthropic): skeleton coordinates, stroke expansion, spacing,
  kerning, this very page. A human said "make it endearing" and then
  watched.</p>
</footer>
</html>
"""
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
