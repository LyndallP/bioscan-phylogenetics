#!/usr/bin/env python3
"""
generate_index.py — Generate GitHub Pages index for UK BIOSCAN Taxonium trees.

Scans data/{Family}/ for tree/metadata file pairs, builds a self-contained
index.html with:
  - Description and usage guide
  - Family count and order summary
  - Live search/filter
  - Taxonomic tree grouped by order (collapsible)
  - Taxonium link per family

Run from the repo root:
    python generate_index.py

Automatically triggered by .github/workflows/generate_pages.yml on push.

Expected file layout in this repo:
    data/
      Sciaridae/
        Sciaridae_final_tree.newick
        sciaridae_metadata_FINAL.tsv
      Empididae/
        Empididae_final_tree.newick
        empididae_metadata_FINAL.tsv
    config.json
    generate_index.py   ← this file
    index.html          ← generated output
"""

import os
import urllib.parse
from pathlib import Path
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Configuration — edit these if the repo name or branch ever changes
# ---------------------------------------------------------------------------
GITHUB_USER   = "LyndallP"
GITHUB_REPO   = "bioscan-phylogenetics"
GITHUB_BRANCH = "main"
CONFIG_FILE   = "config.json"
DATA_DIR      = Path("data")
OUTPUT_FILE   = Path("index.html")

# ---------------------------------------------------------------------------
# Taxonomic order → family mapping (UK arthropods)
# Add families here as new groups are processed.
# ---------------------------------------------------------------------------
ORDER_FAMILIES = {
    "Diptera": [
        "Agromyzidae","Anisopodidae","Anthomyiidae","Asilidae","Bibionidae",
        "Bombyliidae","Calliphoridae","Cecidomyiidae","Chironomidae",
        "Chloropidae","Conopidae","Culicidae","Dolichopodidae","Drosophilidae",
        "Empididae","Ephydridae","Fanniidae","Heleomyzidae","Hybotidae",
        "Lauxaniidae","Limoniidae","Lonchaeidae","Muscidae","Mycetophilidae",
        "Opomyzidae","Phoridae","Pipunculidae","Platypezidae","Psychodidae",
        "Ptychopteridae","Rhagionidae","Sarcophagidae","Scathophagidae",
        "Sciaridae","Sciomyzidae","Simuliidae","Sphaeroceridae","Stratiomyidae",
        "Syrphidae","Tabanidae","Tachinidae","Tephritidae","Therevidae",
        "Tipulidae","Ulidiidae","Xylomyidae","Xylophagidae",
    ],
    "Hymenoptera": [
        "Andrenidae","Apidae","Argidae","Braconidae","Chalcididae","Cimbicidae",
        "Colletidae","Cynipidae","Diapriidae","Encyrtidae","Eulophidae",
        "Eupelmidae","Eurytomidae","Figitidae","Formicidae","Halictidae",
        "Ichneumonidae","Megachilidae","Mutillidae","Mymaridae","Pamphiliidae",
        "Platygastridae","Pompilidae","Pteromalidae","Scelionidae","Siricidae",
        "Sphecidae","Tenthredinidae","Tiphiidae","Torymidae",
        "Trichogrammatidae","Vespidae","Xiphydriidae",
    ],
    "Coleoptera": [
        "Aderidae","Anobiidae","Anthicidae","Apionidae","Buprestidae",
        "Cantharidae","Carabidae","Cerambycidae","Chrysomelidae","Ciidae",
        "Cleridae","Coccinellidae","Cryptophagidae","Curculionidae",
        "Dermestidae","Dytiscidae","Elateridae","Elmidae","Endomychidae",
        "Erotylidae","Geotrupidae","Gyrinidae","Haliplidae","Histeridae",
        "Hydrophilidae","Lampyridae","Lathridiidae","Leiodidae","Lucanidae",
        "Meloidae","Mordellidae","Nitidulidae","Oedemeridae","Phalacridae",
        "Ptiliidae","Pyrochroidae","Rhynchitidae","Scarabaeidae","Scirtidae",
        "Silphidae","Salpingidae","Staphylinidae","Tenebrionidae","Throscidae",
    ],
    "Lepidoptera": [
        "Argyresthiidae","Blastobasidae","Coleophoridae","Cosmopterigidae",
        "Crambidae","Depressariidae","Elachistidae","Gelechiidae","Geometridae",
        "Gracillariidae","Lasiocampidae","Lycaenidae","Momphidae","Nepticulidae",
        "Noctuidae","Nymphalidae","Oecophoridae","Papilionidae","Pieridae",
        "Plutellidae","Pterophoridae","Pyralidae","Saturniidae","Sphingidae",
        "Tineidae","Tischeriidae","Tortricidae","Ypsolophidae","Zygaenidae",
    ],
    "Hemiptera": [
        "Anthocoridae","Aphididae","Aradidae","Berytidae","Cercopidae",
        "Cicadellidae","Cimicidae","Coccidae","Corixidae","Delphacidae",
        "Diaspididae","Gerridae","Hydrometridae","Lygaeidae","Miridae",
        "Nabidae","Naucoridae","Nepidae","Notonectidae","Pentatomidae",
        "Psyllidae","Pyrrhocoridae","Reduviidae","Rhopalidae","Saldidae",
        "Scutelleridae","Tingidae","Veliidae",
    ],
    "Neuroptera": [
        "Berothidae","Chrysopidae","Coniopterygidae","Dilaridae","Hemerobiidae",
        "Mantispidae","Myrmeleontidae","Osmylidae","Raphidiidae","Sisyridae",
    ],
    "Trichoptera": [
        "Beraeidae","Brachycentridae","Glossosomatidae","Goeridae",
        "Hydropsychidae","Hydroptilidae","Lepidostomatidae","Leptoceridae",
        "Limnephilidae","Molannidae","Philopotamidae","Phryganeidae",
        "Polycentropodidae","Psychomyiidae","Rhyacophilidae","Sericostomatidae",
    ],
    "Ephemeroptera": [
        "Baetidae","Caenidae","Ephemeridae","Ephemerellidae","Heptageniidae",
        "Leptophlebiidae","Polymitarcyidae","Potamanthidae","Siphlonuridae",
    ],
    "Plecoptera": [
        "Capniidae","Chloroperlidae","Leuctridae","Nemouridae","Perlidae",
        "Perlodidae","Taeniopterygidae",
    ],
    "Odonata": [
        "Aeshnidae","Calopterygidae","Coenagrionidae","Cordulegastridae",
        "Corduliidae","Gomphidae","Lestidae","Libellulidae","Platycnemididae",
    ],
    "Orthoptera": [
        "Acrididae","Gryllidae","Gryllotalpidae","Phaneropteridae",
        "Raphidophoridae","Tetrigidae","Tettigoniidae",
    ],
    "Araneae": [
        "Agelenidae","Araneidae","Clubionidae","Dictynidae","Dysderidae",
        "Gnaphosidae","Linyphiidae","Lycosidae","Mimetidae","Miturgidae",
        "Philodromidae","Pisauridae","Salticidae","Segestriidae",
        "Tetragnathidae","Theridiidae","Thomisidae","Uloboridae",
    ],
}

ORDER_ICONS = {
    "Diptera":       "🦟",
    "Hymenoptera":   "🐝",
    "Coleoptera":    "🪲",
    "Lepidoptera":   "🦋",
    "Hemiptera":     "🪳",
    "Neuroptera":    "✨",
    "Trichoptera":   "🪲",
    "Ephemeroptera": "🪲",
    "Plecoptera":    "🪲",
    "Odonata":       "🦗",
    "Orthoptera":    "🦗",
    "Araneae":       "🕷️",
    "Other":         "🪲",
}

FAMILY_TO_ORDER = {
    fam: order
    for order, families in ORDER_FAMILIES.items()
    for fam in families
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def raw_url(path: str) -> str:
    return (
        f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}"
        f"/{GITHUB_BRANCH}/{path}"
    )


def taxonium_url(family: str) -> str:
    fam_lower = family.lower()
    params = urllib.parse.urlencode({
        "treeUrl":   raw_url(f"data/{family}/{family}_final_tree.newick"),
        "metaUrl":   raw_url(f"data/{family}/{fam_lower}_metadata_FINAL.tsv"),
        "configUrl": raw_url(CONFIG_FILE),
    })
    return f"https://taxonium.org/?{params}"


def scan_families():
    """Return list of dicts for every family with both required files present."""
    families = []
    if not DATA_DIR.exists():
        return families
    for subdir in sorted(DATA_DIR.iterdir()):
        if not subdir.is_dir():
            continue
        fam = subdir.name
        tree = subdir / f"{fam}_final_tree.newick"
        meta = subdir / f"{fam.lower()}_metadata_FINAL.tsv"
        if tree.exists() and meta.exists():
            families.append({
                "family": fam,
                "order":  FAMILY_TO_ORDER.get(fam, "Other"),
                "url":    taxonium_url(fam),
            })
    return families


# ---------------------------------------------------------------------------
# HTML generation
# ---------------------------------------------------------------------------
def build_html(families: list) -> str:
    by_order: dict = {}
    for f in families:
        by_order.setdefault(f["order"], []).append(f["family"])

    # Sort orders alphabetically; "Other" always last
    sorted_orders = sorted(o for o in by_order if o != "Other")
    if "Other" in by_order:
        sorted_orders.append("Other")

    n_families = len(families)
    n_orders   = len(by_order)
    updated    = datetime.now(timezone.utc).strftime("%d %B %Y")

    # ---- per-order HTML blocks -----------------------------------------
    order_blocks = []
    for order in sorted_orders:
        fams   = sorted(by_order[order])
        icon   = ORDER_ICONS.get(order, "🪲")
        count  = len(fams)

        family_rows = []
        for i, fam in enumerate(fams):
            is_last   = (i == count - 1)
            connector = "└─" if is_last else "├─"
            url       = taxonium_url(fam)
            family_rows.append(
                f'<li class="family-item" data-family="{fam.lower()}">'
                f'<span class="tree-connector">{connector}</span>'
                f'<a href="{url}" target="_blank" rel="noopener" '
                f'   class="family-link" title="Open {fam} tree in Taxonium">'
                f'{fam}</a>'
                f'<span class="link-arrow">↗</span>'
                f'</li>'
            )

        order_blocks.append(f"""
        <div class="order-block" data-order="{order.lower()}">
          <button class="order-header" onclick="toggleOrder(this)" aria-expanded="true">
            <span class="order-toggle">▾</span>
            <span class="order-icon">{icon}</span>
            <span class="order-name">{order}</span>
            <span class="order-count">{count} {'family' if count == 1 else 'families'}</span>
          </button>
          <ul class="family-list">
            {''.join(family_rows)}
          </ul>
        </div>""")

    orders_html = "\n".join(order_blocks)

    no_results_style = "display:none" if families else "display:block"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>UK BIOSCAN Phylogenetics</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #f4f6f9;
      color: #2d3748;
      min-height: 100vh;
    }}

    /* ── Header ─────────────────────────────────────────────────── */
    header {{
      background: linear-gradient(135deg, #1a365d 0%, #2a6049 100%);
      color: #fff;
      padding: 2.5rem 2rem 2rem;
    }}
    header h1 {{
      font-size: 1.9rem;
      font-weight: 700;
      letter-spacing: -0.02em;
      margin-bottom: 0.5rem;
    }}
    header .subtitle {{
      font-size: 1rem;
      opacity: 0.85;
      max-width: 680px;
      line-height: 1.55;
    }}

    /* ── Guide box ───────────────────────────────────────────────── */
    .guide {{
      background: rgba(255,255,255,0.12);
      border: 1px solid rgba(255,255,255,0.2);
      border-radius: 8px;
      padding: 1rem 1.25rem;
      margin-top: 1.25rem;
      font-size: 0.88rem;
      line-height: 1.6;
      max-width: 680px;
    }}
    .guide strong {{ opacity: 1; }}
    .guide ol {{ padding-left: 1.2rem; margin-top: 0.4rem; }}
    .guide li {{ margin-bottom: 0.25rem; }}

    /* ── Stats bar ───────────────────────────────────────────────── */
    .stats {{
      display: flex;
      gap: 1.5rem;
      padding: 1rem 2rem;
      background: #fff;
      border-bottom: 1px solid #e2e8f0;
      font-size: 0.9rem;
      flex-wrap: wrap;
    }}
    .stat {{ display: flex; align-items: center; gap: 0.4rem; }}
    .stat-value {{ font-weight: 700; color: #2a6049; font-size: 1.1rem; }}
    .stat-label {{ color: #718096; }}
    .updated {{ margin-left: auto; color: #a0aec0; font-size: 0.8rem; align-self: center; }}

    /* ── Search ──────────────────────────────────────────────────── */
    .search-bar {{
      padding: 1rem 2rem;
      background: #fff;
      border-bottom: 1px solid #e2e8f0;
    }}
    .search-wrap {{
      position: relative;
      max-width: 420px;
    }}
    .search-wrap::before {{
      content: "🔍";
      position: absolute;
      left: 0.75rem;
      top: 50%;
      transform: translateY(-50%);
      font-size: 0.9rem;
      pointer-events: none;
    }}
    #search {{
      width: 100%;
      padding: 0.55rem 0.75rem 0.55rem 2.2rem;
      border: 1.5px solid #cbd5e0;
      border-radius: 8px;
      font-size: 0.95rem;
      outline: none;
      transition: border-color 0.15s;
    }}
    #search:focus {{ border-color: #2a6049; box-shadow: 0 0 0 3px rgba(42,96,73,0.12); }}

    /* ── Tree container ──────────────────────────────────────────── */
    .tree-container {{
      max-width: 860px;
      margin: 1.5rem auto;
      padding: 0 1.5rem 3rem;
    }}

    /* ── Order block ─────────────────────────────────────────────── */
    .order-block {{
      background: #fff;
      border: 1px solid #e2e8f0;
      border-radius: 10px;
      margin-bottom: 0.85rem;
      overflow: hidden;
      box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }}
    .order-header {{
      width: 100%;
      display: flex;
      align-items: center;
      gap: 0.6rem;
      padding: 0.85rem 1.1rem;
      background: none;
      border: none;
      cursor: pointer;
      font-size: 1rem;
      font-weight: 600;
      color: #2d3748;
      text-align: left;
      transition: background 0.1s;
    }}
    .order-header:hover {{ background: #f7fafc; }}
    .order-toggle {{ font-size: 0.8rem; color: #718096; transition: transform 0.2s; }}
    .order-header[aria-expanded="false"] .order-toggle {{ transform: rotate(-90deg); }}
    .order-icon {{ font-size: 1.15rem; }}
    .order-name {{ flex: 1; }}
    .order-count {{
      font-size: 0.78rem;
      font-weight: 500;
      background: #ebf8f1;
      color: #2a6049;
      padding: 0.15rem 0.55rem;
      border-radius: 99px;
    }}

    /* ── Family list (tree lines) ────────────────────────────────── */
    .family-list {{
      list-style: none;
      padding: 0 1.1rem 0.7rem 1.5rem;
      border-top: 1px solid #f0f0f0;
      font-family: "SFMono-Regular", "Consolas", "Liberation Mono", monospace;
      font-size: 0.88rem;
    }}
    .family-item {{
      display: flex;
      align-items: center;
      padding: 0.28rem 0;
      gap: 0.5rem;
    }}
    .tree-connector {{
      color: #a0aec0;
      user-select: none;
      min-width: 1.6rem;
    }}
    .family-link {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      font-size: 0.92rem;
      color: #1a365d;
      text-decoration: none;
      font-weight: 500;
      padding: 0.2rem 0.6rem;
      border-radius: 5px;
      transition: background 0.1s, color 0.1s;
    }}
    .family-link:hover {{
      background: #ebf8f1;
      color: #2a6049;
      text-decoration: underline;
    }}
    .link-arrow {{
      font-size: 0.75rem;
      color: #a0aec0;
      margin-left: -0.25rem;
    }}

    /* ── No results ──────────────────────────────────────────────── */
    #no-results {{
      text-align: center;
      padding: 3rem 1rem;
      color: #718096;
      font-size: 1rem;
      {no_results_style};
    }}

    /* ── Hidden by collapse / search ────────────────────────────── */
    .order-block.collapsed .family-list {{ display: none; }}
    .family-item.hidden {{ display: none; }}
    .order-block.all-hidden {{ display: none; }}
  </style>
</head>
<body>

<header>
  <h1>🔬 UK BIOSCAN Phylogenetics</h1>
  <p class="subtitle">
    Phylogenetic trees for UK BIOSCAN insect specimens placed onto BGE
    reference trees. Each family links to an interactive Taxonium viewer
    showing specimen placements, BAGS quality grades, and metadata.
  </p>
  <div class="guide">
    <strong>How to use:</strong>
    <ol>
      <li>Click a family name to open its tree in Taxonium (opens in a new tab).</li>
      <li>In Taxonium, use <em>Color by</em> to explore BAGS grades, placement quality,
          geography, and more.</li>
      <li>Click any tip node to see specimen metadata, BOLD links, and NCBI BLAST.</li>
      <li>Copy the browser URL after loading — it encodes the full view and is
          shareable without needing access to any files.</li>
    </ol>
  </div>
</header>

<div class="stats">
  <div class="stat">
    <span class="stat-value">{n_families}</span>
    <span class="stat-label">{'family' if n_families == 1 else 'families'}</span>
  </div>
  <div class="stat">
    <span class="stat-value">{n_orders}</span>
    <span class="stat-label">{'order' if n_orders == 1 else 'orders'}</span>
  </div>
  <span class="updated">Updated {updated}</span>
</div>

<div class="search-bar">
  <div class="search-wrap">
    <input id="search" type="text" placeholder="Filter families…"
           oninput="filterFamilies(this.value)" autocomplete="off">
  </div>
</div>

<div class="tree-container">
{orders_html}
  <div id="no-results">No families match your search.</div>
</div>

<script>
  function toggleOrder(btn) {{
    const block = btn.closest('.order-block');
    const expanded = btn.getAttribute('aria-expanded') === 'true';
    btn.setAttribute('aria-expanded', String(!expanded));
    block.classList.toggle('collapsed', expanded);
  }}

  function filterFamilies(query) {{
    const q = query.trim().toLowerCase();
    let anyVisible = false;

    document.querySelectorAll('.order-block').forEach(block => {{
      let blockHasMatch = false;
      block.querySelectorAll('.family-item').forEach(item => {{
        const name = item.dataset.family || '';
        const match = !q || name.includes(q);
        item.classList.toggle('hidden', !match);
        if (match) blockHasMatch = true;
      }});
      block.classList.toggle('all-hidden', !blockHasMatch);
      if (blockHasMatch) anyVisible = true;

      // Auto-expand when searching
      if (q && blockHasMatch) {{
        block.classList.remove('collapsed');
        block.querySelector('.order-header').setAttribute('aria-expanded', 'true');
      }}
    }});

    document.getElementById('no-results').style.display =
      anyVisible ? 'none' : 'block';
  }}
</script>

</body>
</html>"""


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    families = scan_families()
    html     = build_html(families)
    OUTPUT_FILE.write_text(html, encoding="utf-8")

    print(f"Generated {OUTPUT_FILE} with {len(families)} families")
    for f in families:
        print(f"  {f['order']:15s}  {f['family']}")
