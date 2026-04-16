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
        "Acartophthalmidae","Agromyzidae","Anisopodidae","Anthomyiidae",
        "Anthomyzidae","Asilidae","Asteiidae","Atelestidae","Bibionidae",
        "Bolitophilidae","Bombyliidae","Brachystomatidae","Calliphoridae",
        "Camillidae","Carnidae","Cecidomyiidae","Ceratopogonidae",
        "Chamaemyiidae","Chaoboridae","Chironomidae","Chloropidae","Chyromyidae",
        "Clusiidae","Conopidae","Cryptochetidae","Culicidae","Cylindrotomidae",
        "Diadocidiidae","Diastatidae","Ditomyiidae","Dixidae","Dolichopodidae",
        "Drosophilidae","Dryomyzidae","Empididae","Ephydridae","Fanniidae",
        "Heleomyzidae","Hippoboscidae","Hybotidae","Keroplatidae","Lauxaniidae",
        "Limoniidae","Lonchaeidae","Lonchopteridae","Micropezidae","Milichiidae",
        "Muscidae","Mycetophilidae","Odiniidae","Oestridae","Opetiidae",
        "Opomyzidae","Pallopteridae","Pediciidae","Periscelididae","Phoridae",
        "Piophilidae","Pipunculidae","Platypezidae","Platystomatidae",
        "Polleniidae","Psilidae","Psychodidae","Ptychopteridae","Rhagionidae",
        "Sarcophagidae","Scathophagidae","Scatopsidae","Scenopinidae","Sciaridae",
        "Sciomyzidae","Sepsidae","Simuliidae","Sphaeroceridae","Stratiomyidae",
        "Syrphidae","Tabanidae","Tachinidae","Tephritidae","Thaumaleidae",
        "Therevidae","Tipulidae","Trichoceridae","Ulidiidae","Xylomyidae",
        "Xylophagidae",
    ],
    "Hymenoptera": [
        "Andrenidae","Aphelinidae","Apidae","Argidae","Bembicidae","Bethylidae",
        "Braconidae","Ceidae","Ceraphronidae","Cephidae",
        "Chalcidoidea_incertae_sedis","Chrysididae","Cleonymidae","Colletidae",
        "Crabronidae","Cynipidae","Diapriidae","Diplolepididae","Diprionidae",
        "Dryinidae","Embolemidae","Encyrtidae","Eunotidae","Eupelmidae",
        "Eurytomidae","Figitidae","Formicidae","Gasteruptiidae","Halictidae",
        "Heloridae","Heptamelidae","Ichneumonidae","Ismaridae","Megachilidae",
        "Megaspilidae","Megastigmidae","Mellinidae","Mymaridae","Myrmosidae",
        "Ormyridae","Pemphredonidae","Perilampidae","Philanthidae","Pirenidae",
        "Platygastridae","Pompilidae","Proctotrupidae","Psenidae","Pteromalidae",
        "Scelionidae","Signiphoridae","Spalangiidae","Systasidae","Tenthredinidae",
        "Tetracampidae","Tiphiidae","Torymidae","Trichogrammatidae","Vespidae",
        "Xyelidae",
    ],
    "Coleoptera": [
        "Anthicidae","Anthribidae","Attelabidae","Biphyllidae","Brentidae",
        "Buprestidae","Byturidae","Cantharidae","Carabidae","Cerambycidae",
        "Chrysomelidae","Ciidae","Clambidae","Cleridae","Coccinellidae",
        "Corylophidae","Cryptophagidae","Curculionidae","Dascillidae",
        "Dermestidae","Dryopidae","Dytiscidae","Elateridae","Endomychidae",
        "Erotylidae","Eucnemidae","Gyrinidae","Helophoridae","Heteroceridae",
        "Hydraenidae","Hydrochidae","Hydrophilidae","Kateretidae","Lampyridae",
        "Latridiidae","Leiodidae","Lymexylidae","Melandryidae","Melyridae",
        "Monotomidae","Mordellidae","Mycetophagidae","Nitidulidae","Noteridae",
        "Oedemeridae","Phalacridae","Phloiophilidae","Ptiliidae","Ptinidae",
        "Pyrochroidae","Salpingidae","Scarabaeidae","Scirtidae","Scraptiidae",
        "Silvanidae","Sphindidae","Staphylinidae","Tenebrionidae","Throscidae",
        "Zopheridae",
    ],
    "Lepidoptera": [
        "Adelidae","Alucitidae","Argyresthiidae","Autostichidae","Batrachedridae",
        "Bedelliidae","Blastobasidae","Bucculatricidae","Choreutidae",
        "Coleophoridae","Cossidae","Crambidae","Depressariidae","Drepanidae",
        "Elachistidae","Epermeniidae","Erebidae","Eriocraniidae","Gelechiidae",
        "Geometridae","Glyphipterigidae","Gracillariidae","Heliozelidae",
        "Hepialidae","Hesperiidae","Incurvariidae","Lycaenidae","Lyonetiidae",
        "Lypusidae","Micropterigidae","Momphidae","Nepticulidae","Noctuidae",
        "Nolidae","Notodontidae","Nymphalidae","Oecophoridae","Opostegidae",
        "Pieridae","Plutellidae","Praydidae","Prodoxidae","Psychidae",
        "Pterophoridae","Pyralidae","Roeslerstammiidae","Schreckensteiniidae",
        "Scythropiidae","Sesiidae","Tineidae","Tischeriidae","Tortricidae",
        "Yponomeutidae","Ypsolophidae","Zygaenidae",
    ],
    "Hemiptera": [
        "Acanthosomatidae","Adelgidae","Aleyrodidae","Anthocoridae","Aphalaridae",
        "Aphididae","Aphrophoridae","Artheneidae","Berytidae","Blissidae",
        "Cercopidae","Cicadellidae","Cixiidae","Coccoidea_incertae_sedis",
        "Coreidae","Corixidae","Cydnidae","Cymidae","Delphacidae","Diaspididae",
        "Heterogastridae","Issidae","Liviidae","Lygaeidae","Membracidae",
        "Microphysidae","Micronectidae","Miridae","Nabidae","Oxycarenidae",
        "Pentatomidae","Phylloxeridae","Piesmatidae","Pleidae","Pseudococcidae",
        "Psyllidae","Reduviidae","Rhyparochromidae","Rhopalidae","Saldidae",
        "Scutelleridae","Tingidae","Triozidae",
    ],
    "Araneae": [
        "Agelenidae","Amaurobiidae","Anyphaenidae","Araneidae","Cheiracanthiidae",
        "Clubionidae","Dictynidae","Gnaphosidae","Hahniidae","Lathyidae",
        "Linyphiidae","Lycosidae","Mimetidae","Oonopidae","Philodromidae",
        "Pisauridae","Salticidae","Tetragnathidae","Theridiidae","Thomisidae",
    ],
    "Trichoptera": [
        "Apataniidae","Beraeidae","Brachycentridae","Ecnomidae","Glossosomatidae",
        "Goeridae","Hydropsychidae","Hydroptilidae","Lepidostomatidae",
        "Leptoceridae","Limnephilidae","Molannidae","Philopotamidae",
        "Phryganeidae","Polycentropodidae","Psychomyiidae","Rhyacophilidae",
        "Sericostomatidae",
    ],
    "Neuroptera": [
        "Chrysopidae","Coniopterygidae","Hemerobiidae","Sisyridae",
    ],
    "Ephemeroptera": [
        "Baetidae","Caenidae","Ephemerellidae","Heptageniidae","Leptophlebiidae",
    ],
    "Plecoptera": [
        "Chloroperlidae","Leuctridae","Nemouridae","Perlodidae","Taeniopterygidae",
    ],
    "Odonata": [
        "Aeshnidae","Coenagrionidae",
    ],
    "Orthoptera": [
        "Acrididae","Tettigoniidae",
    ],
    "Sarcoptiformes": [
        "Achipteriidae","Acaridae","Carabodidae","Cepheusidae","Ceratozetidae",
        "Chamobatidae","Crotoniidae","Damaeidae","Eremaeidae","Euzetidae",
        "Humerobatidae","Hydrozetidae","Liacaridae","Nothridae","Oribatellidae",
        "Peloppiidae","Phthiracaridae",
    ],
    "Mesostigmata": [
        "Ascidae","Blattisociidae","Halolaelapidae","Laelapidae","Macrochelidae",
        "Melicharidae","Parasitidae","Phytoseiidae",
    ],
    "Trombidiformes": [
        "Anystidae","Bdellidae","Calyptostomatidae","Erythraeidae","Eupodidae",
        "Hygrobatidae","Labidostommatidae","Microtrombidiidae","Pionidae",
        "Scutacaridae","Sperchontidae","Trombidiidae","Unionicolidae",
    ],
    "Psocodea": [
        "Amphipsocidae","Caeciliusidae","Ectopsocidae","Elipsocidae",
        "Lachesillidae","Liposcelididae","Mesopsocidae","Paracaeciliidae",
        "Peripsocidae","Philotarsidae","Psocidae","Stenopsocidae",
        "Trichopsocidae","Trogiidae",
    ],
    "Thysanoptera": [
        "Aeolothripidae","Melanthripidae","Phlaeothripidae","Thripidae",
    ],
    "Entomobryomorpha": [
        "Entomobryidae","Isotomidae","Lepidocyrtidae","Orchesellidae","Tomoceridae",
    ],
    "Symphypleona": [
        "Bourletiellidae","Dicyrtomidae","Katiannidae","Sminthuridae","Sminthurididae",
    ],
    "Poduromorpha": [
        "Hypogastruridae","Neanuridae","Onychiuridae",
    ],
    "Opiliones": [
        "Nemastomatidae","Phalangiidae","Sclerosomatidae",
    ],
    "Isopoda": [
        "Armadillidiidae","Philosciidae","Porcellionidae","Trichoniscidae",
    ],
    "Amphipoda": [
        "Arcitalitridae","Gammaridae","Talitridae",
    ],
    "Dermaptera": [
        "Forficulidae","Spongiphoridae",
    ],
    "Blattodea": [
        "Ectobiidae",
    ],
    "Strepsiptera": [
        "Elenchidae","Halictophagidae",
    ],
    "Megaloptera": [
        "Sialidae",
    ],
    "Mecoptera": [
        "Panorpidae",
    ],
    "Raphidioptera": [
        "Raphidiidae",
    ],
    "Mantodea": [
        "Mantidae",
    ],
    "Pseudoscorpiones": [
        "Chthoniidae","Neobisiidae",
    ],
    "Ixodida": [
        "Ixodidae",
    ],
    "Julida": [
        "Julidae","Nemasomatidae",
    ],
    "Polydesmida": [
        "Polydesmidae",
    ],
    "Polyxenida": [
        "Polyxenidae",
    ],
    "Glomerida": [
        "Glomeridae",
    ],
    "Geophilomorpha": [
        "Schendylidae",
    ],
    "Balanomorpha": [
        "Balanidae","Elminiidae",
    ],
    "Amphipoda": [
        "Arcitalitridae","Gammaridae","Talitridae",
    ],
    "Calanoida": [
        "Acartiidae",
    ],
    "Mysida": [
        "Mysidae",
    ],
    "Rhabditida": [
        "Sphaerulariidae",
    ],
}

ORDER_ICONS = {
    "Diptera":           "🦟",
    "Hymenoptera":       "🐝",
    "Coleoptera":        "🪲",
    "Lepidoptera":       "🦋",
    "Hemiptera":         "🪳",
    "Neuroptera":        "✨",
    "Trichoptera":       "🪲",
    "Ephemeroptera":     "🪲",
    "Plecoptera":        "🪲",
    "Odonata":           "🦗",
    "Orthoptera":        "🦗",
    "Araneae":           "🕷️",
    "Sarcoptiformes":    "🕷️",
    "Mesostigmata":      "🕷️",
    "Trombidiformes":    "🕷️",
    "Psocodea":          "🪲",
    "Thysanoptera":      "🌿",
    "Entomobryomorpha":  "🦗",
    "Symphypleona":      "🦗",
    "Poduromorpha":      "🦗",
    "Opiliones":         "🕷️",
    "Isopoda":           "🦐",
    "Amphipoda":         "🦐",
    "Dermaptera":        "🪲",
    "Blattodea":         "🪳",
    "Strepsiptera":      "🪲",
    "Megaloptera":       "🪲",
    "Mecoptera":         "🪲",
    "Raphidioptera":     "🪲",
    "Mantodea":          "🪲",
    "Pseudoscorpiones":  "🦂",
    "Ixodida":           "🕷️",
    "Julida":            "🐛",
    "Polydesmida":       "🐛",
    "Polyxenida":        "🐛",
    "Glomerida":         "🐛",
    "Geophilomorpha":    "🐛",
    "Balanomorpha":      "🦐",
    "Calanoida":         "🦐",
    "Mysida":            "🦐",
    "Rhabditida":        "🪱",
    "Other":             "🪲",
}

FAMILY_TO_ORDER = {
    fam: order
    for order, families in ORDER_FAMILIES.items()
    for fam in families
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
GLOBAL_FAMILY = "Arthropoda_global"
GLOBAL_DIR    = DATA_DIR / GLOBAL_FAMILY


def raw_url(path: str) -> str:
    return (
        f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}"
        f"/{GITHUB_BRANCH}/{path}"
    )


def detect_global_tree():
    """Return the Taxonium URL for the global Arthropoda tree, or None if the
    expected files are not present in data/Arthropoda_global/."""
    meta = GLOBAL_DIR / "arthropoda_global_metadata_FINAL.tsv"
    if not meta.exists():
        return None
    tree = GLOBAL_DIR / f"{GLOBAL_FAMILY}_final_tree.newick"
    if not tree.exists():
        return None
    p = {
        "treeUrl":       raw_url(f"data/{GLOBAL_FAMILY}/{GLOBAL_FAMILY}_final_tree.newick"),
        "metaUrl":       raw_url(f"data/{GLOBAL_FAMILY}/arthropoda_global_metadata_FINAL.tsv"),
        "ladderizeTree": "true",
    }
    return f"https://taxonium.org/?{urllib.parse.urlencode(p)}"


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
        if fam == GLOBAL_FAMILY:   # handled separately — see detect_global_tree()
            continue
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
def build_html(families: list, global_url=None) -> str:
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

    if global_url:
        global_banner_html = f"""<div class="global-tree-banner">
  <div class="global-tree-info">
    <span class="global-tree-icon">🌍</span>
    <div>
      <strong>All Arthropoda — Global Overview</strong>
      <p>3,264-family synthesis tree &middot; <a href="https://doi.org/10.5281/zenodo.19195926" target="_blank" rel="noopener" style="color:rgba(255,255,255,0.8);text-decoration:underline;">Alhalabi (2026)</a></p>
    </div>
  </div>
  <a href="{global_url}" target="_blank" rel="noopener" class="global-tree-btn">
    Open in Taxonium ↗
  </a>
</div>"""
    else:
        global_banner_html = ""

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
    .header-top {{
      display: flex;
      align-items: center;
      gap: 20px;
      margin-bottom: 1rem;
    }}
    .bioscan-logo {{
      height: 60px;
      width: auto;
    }}
    header h1 {{
      font-size: 1.9rem;
      font-weight: 700;
      letter-spacing: -0.02em;
    }}
    header .subtitle {{
      font-size: 1rem;
      opacity: 0.85;
      max-width: 780px;
      line-height: 1.6;
      margin-bottom: 0;
    }}

    /* ── Content sections (below header) ────────────────────────── */
    .content-sections {{
      padding: 2rem 2rem 0.5rem;
    }}
    .scientific-context,
    .how-to-guide,
    .metadata-guide {{
      background: #f8f9fa;
      border-left: 4px solid #2a6049;
      padding: 1.5rem;
      margin-bottom: 1.5rem;
      border-radius: 0 6px 6px 0;
    }}
    .scientific-context h2,
    .how-to-guide h2,
    .metadata-guide h2 {{
      margin-top: 0;
      margin-bottom: 0.75rem;
      color: #1a365d;
      font-size: 1.15rem;
    }}
    .scientific-context h3 {{
      margin-top: 1.25rem;
      margin-bottom: 0.5rem;
      color: #2a6049;
      font-size: 1rem;
    }}
    .scientific-context p,
    .how-to-guide p,
    .metadata-guide p {{
      line-height: 1.65;
      margin-bottom: 0.75rem;
      font-size: 0.95rem;
    }}
    .scientific-context p:last-child,
    .metadata-guide p:last-child {{ margin-bottom: 0; }}
    .citation-note {{
      background: #eef2f7;
      border-left: 3px solid #718096;
      padding: 0.6rem 0.9rem;
      border-radius: 0 4px 4px 0;
      font-size: 0.88rem !important;
    }}
    .scientific-context a,
    .how-to-guide a,
    .metadata-guide a {{
      color: #2a6049;
      text-decoration: underline;
    }}
    .how-to-guide ol {{
      padding-left: 1.4rem;
      margin-top: 0.5rem;
    }}
    .how-to-guide li {{
      margin-bottom: 0.5rem;
      font-size: 0.95rem;
      line-height: 1.6;
    }}

    /* ── Metadata table ──────────────────────────────────────────── */
    .metadata-table {{
      width: 100%;
      border-collapse: collapse;
      margin: 1rem 0;
      font-size: 0.88rem;
    }}
    .metadata-table th,
    .metadata-table td {{
      padding: 10px 12px;
      text-align: left;
      border: 1px solid #dee2e6;
      vertical-align: top;
    }}
    .metadata-table th {{
      background-color: #1a365d;
      color: #fff;
      font-weight: 600;
    }}
    .metadata-table tr:nth-child(even) td {{
      background-color: #f8f9fa;
    }}
    .metadata-table code {{
      background: #e9ecef;
      padding: 2px 5px;
      border-radius: 3px;
      font-family: "SFMono-Regular", "Consolas", monospace;
      font-size: 0.85em;
      color: #c7254e;
    }}
    .section-header td {{
      background: #e9ecef !important;
      font-style: italic;
      text-align: center;
      color: #555;
    }}

    /* ── Search tips box ─────────────────────────────────────────── */
    .search-tips {{
      background: #fff3cd;
      border-left: 4px solid #ffc107;
      padding: 1rem 1.25rem;
      margin-top: 1.25rem;
      border-radius: 0 6px 6px 0;
    }}
    .search-tips h3 {{
      margin-top: 0;
      margin-bottom: 0.5rem;
      color: #856404;
      font-size: 0.95rem;
    }}
    .search-tips ul {{
      padding-left: 1.2rem;
      margin-bottom: 0;
    }}
    .search-tips li {{
      margin-bottom: 0.3rem;
      font-size: 0.88rem;
      line-height: 1.55;
    }}
    .search-tips code {{
      background: #fff;
      padding: 1px 5px;
      border-radius: 3px;
      border: 1px solid #ffc107;
      font-family: "SFMono-Regular", "Consolas", monospace;
      font-size: 0.85em;
    }}

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

    /* ── Global Arthropoda banner ────────────────────────────────── */
    .global-tree-banner {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
      flex-wrap: wrap;
      padding: 0.9rem 1.25rem;
      background: linear-gradient(135deg, #1a365d 0%, #2a6049 100%);
      color: #fff;
    }}
    .global-tree-info {{
      display: flex;
      align-items: center;
      gap: 0.7rem;
    }}
    .global-tree-icon {{ font-size: 1.6rem; line-height: 1; }}
    .global-tree-info strong {{
      display: block;
      font-size: 0.92rem;
      font-weight: 700;
    }}
    .global-tree-info p {{
      font-size: 0.78rem;
      opacity: 0.85;
      margin: 0.1rem 0 0;
    }}
    .global-tree-btn {{
      display: inline-block;
      padding: 0.4rem 0.9rem;
      background: rgba(255,255,255,0.15);
      color: #fff;
      font-size: 0.85rem;
      font-weight: 600;
      border-radius: 6px;
      text-decoration: none;
      border: 1px solid rgba(255,255,255,0.3);
      white-space: nowrap;
      transition: background 0.15s;
    }}
    .global-tree-btn:hover {{ background: rgba(255,255,255,0.28); }}

    /* ── Hidden by collapse / search ────────────────────────────── */
    .order-block.collapsed .family-list {{ display: none; }}
    .family-item.hidden {{ display: none; }}
    .order-block.all-hidden {{ display: none; }}

    /* ── Two-panel layout ────────────────────────────────────────── */
    .page-body {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      align-items: start;
      min-height: calc(100vh - 140px);
    }}
    .left-panel {{
      background: #fff;
      border-right: 2px solid #e2e8f0;
      overflow-y: auto;
    }}
    .right-panel {{
      position: sticky;
      top: 0;
      height: 100vh;
      overflow-y: auto;
      background: #f4f6f9;
    }}
    .right-panel .stats {{
      border-bottom: 1px solid #e2e8f0;
      background: #fff;
    }}
    .right-panel .search-bar {{
      background: #fff;
      border-bottom: 1px solid #e2e8f0;
    }}
    @media (max-width: 900px) {{
      .page-body {{
        grid-template-columns: 1fr;
      }}
      .right-panel {{
        position: static;
        height: auto;
      }}
    }}
  </style>
</head>
<body>

<header>
  <div class="header-top">
    <img src="bioscan_logo.png" alt="BIOSCAN logo" class="bioscan-logo">
    <h1>🔬 UK BIOSCAN Phylogenetics</h1>
  </div>
  <p class="subtitle">
    Phylogenetic placement of UK BIOSCAN arthropod specimens onto BGE reference trees,
    revealing biodiversity coverage and highlighting species gaps in the UK barcode library.
  </p>
</header>

<div class="page-body">
<div class="left-panel">
<div class="content-sections">

  <div class="scientific-context">
    <h2>About This Resource</h2>
    <p>
      The <a href="https://bioscan.tol.sanger.ac.uk/" target="_blank">BIOSCAN UK project</a>
      is systematically collecting and DNA barcoding arthropods across the UK, generating
      comprehensive COI-5P barcode coverage for British arthropod diversity. This visualization
      platform places BIOSCAN specimens onto high-quality reference phylogenies from the
      <strong>Biodiversity Genomics Europe (BGE)</strong> project, creating interactive trees that
      span <strong>450+ arthropod families across 40 orders</strong>.
    </p>
    <p>
      Each tree integrates multiple data sources: BIOSCAN UK specimens, European reference
      barcodes, <strong>Darwin Tree of Life (DToL) genome assemblies</strong>, and UK Species
      Inventory (UKSI) taxonomy. The modular design allows new datasets—such as genome-sequenced
      specimens or regional barcode initiatives—to be seamlessly added to existing trees.
    </p>
    <h3>Global Arthropoda Overview Tree</h3>
    <p>
      In addition to the per-family barcode trees, this resource includes a
      <strong>family-level synthesis phylogeny spanning all 3,264 extant families of
      Panarthropoda</strong>. This global tree provides taxonomic context for the
      per-family BIOSCAN trees, showing where each family sits within the broader
      arthropod tree of life and which families have been processed so far.
    </p>
    <p>
      The global tree is based on the synthesis phylogeny of
      <a href="https://doi.org/10.5281/zenodo.19195926" target="_blank">Alhalabi (2026)</a>,
      constructed manually in Treegraph2 from 219 phylogenetic and taxonomic sources.
      Families present in the UK BIOSCAN dataset are highlighted; clicking the
      <em>Open in Taxonium</em> button at the top of the tree panel loads the global
      tree with per-family metadata (including UK presence and dataset status).
    </p>
    <p class="citation-note">
      <strong>Citation:</strong> Alhalabi, A. (2026). <em>Family Level Synthesis Phylogeny
      of Extant Arthropoda and Related Phyla</em> (Version 7) [Dataset]. Zenodo.
      <a href="https://doi.org/10.5281/zenodo.19195926" target="_blank">https://doi.org/10.5281/zenodo.19195926</a>
    </p>
    <h3>Why This Matters</h3>
    <p>
      These trees reveal the <strong>UKSI gap analysis</strong> in action: which British species
      lack COI barcodes, where taxonomic uncertainties exist, and which lineages would benefit
      from genome sequencing. By visualizing <strong>BAGS quality grades</strong>
      (<a href="https://doi.org/10.1111/1755-0998.13262" target="_blank">Pentinsaari et al. 2020</a>),
      BIN assignments, and phylogenetic placement confidence together, the trees support
      biodiversity surveillance, taxonomic validation, and genome prioritization decisions.
    </p>
    <p>
      The UKSI gap analysis underlying these visualizations is part of the broader
      <a href="https://ukbol.org/" target="_blank">UKBOL (UK Barcode of Life)</a> initiative.
      See the <a href="https://ukbol.org/species/bold_coi.html?kingdom=Animalia" target="_blank">UKBOL species coverage overview</a>
      for context on which British species have COI barcodes.
    </p>
  </div>

  <div class="how-to-guide">
    <h2>How to Use These Trees</h2>
    <ol>
      <li><strong>Click a family name</strong> in the table below to open its interactive tree in Taxonium (opens in new tab).</li>
      <li><strong>Explore the data:</strong> In Taxonium, use the <em>Color by</em> dropdown to visualize different metadata dimensions—BAGS grades, BIN quality issues, placement confidence, geography, UKSI status, and more.</li>
      <li><strong>Click any tip node</strong> to see full specimen metadata, including direct links to BOLD records, NCBI BLAST searches, GBIF distribution maps, NBN Atlas records, and DToL genome assemblies (where available).</li>
      <li><strong>Use the Search button</strong> (top-right in Taxonium) to find specific specimens, species, BINs, or metadata values. See the searchable terms table below.</li>
      <li><strong>Share your view:</strong> After exploring, copy the browser URL—it encodes the current zoom, coloring, and search state, creating a shareable link that works without file access.</li>
    </ol>
  </div>

  <div class="metadata-guide">
    <h2>Searchable Metadata Fields</h2>
    <p>Use the <strong>Search</strong> button in Taxonium to filter specimens by any of these metadata fields.</p>
    <table class="metadata-table">
      <thead>
        <tr><th>Field Name</th><th>Description</th><th>Searchable Values</th></tr>
      </thead>
      <tbody>
        <tr><td><code>species</code></td><td>Species name (or genus + "sp." for unidentified)</td><td>Scientific names (e.g., "Empis tessellata", "Unknown species")</td></tr>
        <tr><td><code>bin</code></td><td>BOLD Barcode Index Number</td><td>BIN URIs (e.g., "BOLD:ACD3004")</td></tr>
        <tr><td><code>processid</code></td><td>BOLD process ID (unique specimen identifier)</td><td>Process IDs (e.g., "YARN1707-23")</td></tr>
        <tr><td><code>Specimen ID</code></td><td>BIOSCAN specimen tube ID</td><td>Tube IDs (e.g., "SHAP_062_D11")</td></tr>
        <tr><td><code>category</code></td><td>Specimen source category</td><td><strong>BIOSCAN_collected</strong> = BIOSCAN UK specimen &nbsp;|&nbsp; <strong>UKSI_no_specimens</strong> = UKSI-listed species, no BIOSCAN specimens yet &nbsp;|&nbsp; <strong>Europe_reference</strong> = European reference barcode &nbsp;|&nbsp; <strong>Not_in_UKSI</strong> = Not in UK Species Inventory</td></tr>
        <tr><td><code>dataset</code></td><td>Data source</td><td><strong>BIOSCAN</strong> | <strong>Reference</strong> | <strong>DToL</strong></td></tr>
        <tr><td><code>geography</code></td><td>Country of collection</td><td>Country names (e.g., "United Kingdom", "Finland")</td></tr>
        <tr><td><code>geography_broad</code></td><td>Broader geographic region</td><td>"British Isles", "Scandinavia", "Western Europe", etc.</td></tr>
        <tr><td><code>in_uksi</code></td><td>Is species listed in UK Species Inventory?</td><td><strong>True</strong> | <strong>False</strong></td></tr>
        <tr><td><code>UKSI_name_match</code></td><td>Matched name in UKSI (if applicable)</td><td>Species names or blank</td></tr>
        <tr><td><code>Bioscan specimen count</code></td><td>Number of BIOSCAN specimens for this BIN across all families</td><td>Numbers (e.g., "0", "87", "12")</td></tr>
        <tr><td><code>placement_type</code></td><td>How specimen was placed on the tree</td><td><strong>reference_tree</strong> = Part of original reference tree &nbsp;|&nbsp; <strong>validation</strong> = BIOSCAN specimen placed via EPA-ng &nbsp;|&nbsp; <strong>novel</strong> = Novel placement (species not in reference tree)</td></tr>
        <tr><td><code>placement_quality</code></td><td>Phylogenetic placement confidence</td><td><strong>High</strong> = EPA-ng LWR &ge; 0.90 &nbsp;|&nbsp; <strong>Moderate</strong> = LWR 0.75&ndash;0.89 &nbsp;|&nbsp; <strong>Low</strong> = LWR &le; 0.74</td></tr>
        <tr><td><code>epa_lwr_score</code></td><td>EPA-ng likelihood weight ratio (0–1)</td><td>Numerical scores (e.g., "1.0", "0.3367799324")</td></tr>
        <tr><td><code>parent_bootstrap</code></td><td>Bootstrap support for parent node</td><td>Values 0–1 (e.g., "0.92", "1.0")</td></tr>
        <tr><td><code>Node support / Placement</code></td><td>Human-readable placement quality summary</td><td>"High (0.90–1.00)" | "Moderate (0.75–0.89)" | "Low (0–0.74)" | "No support data" | "Novel placement"</td></tr>
        <tr><td><code>bags_grade</code></td><td>Barcode audit grade (<a href="https://doi.org/10.1111/1755-0998.13262" target="_blank">Pentinsaari et al. 2020</a>)</td><td><strong>A</strong> = Ideal &nbsp;|&nbsp; <strong>B</strong> = Acceptable &nbsp;|&nbsp; <strong>C</strong> = Species split across BINs &nbsp;|&nbsp; <strong>D</strong> = Problematic &nbsp;|&nbsp; <strong>E</strong> = BIN shared by multiple species</td></tr>
        <tr><td><code>bin_quality_issue</code></td><td>BIN assignment flag</td><td><strong>clean</strong> | <strong>shares_BIN_with_other_species</strong> | <strong>split_across_2_BINs</strong> | <strong>split_across_3_BINs</strong> | <strong>split_across_4_BINs</strong></td></tr>
        <tr><td><code>n_bins_for_species</code></td><td>How many BINs this species spans</td><td>Numbers (e.g., "1", "2", "3")</td></tr>
        <tr><td><code>needs_attention</code></td><td>Flagged for review (Grade C/D/E)</td><td><strong>True</strong> | <strong>False</strong></td></tr>
        <tr><td><code>tolid</code></td><td>Tree of Life ID (DToL genome specimen)</td><td>ToL IDs (e.g., "idCorForc3") or blank</td></tr>
        <tr><td><code>assembly_status</code></td><td>DToL genome assembly stage</td><td>"Scaffolding" | "Curating" | "Done" | "Pre-curation" | "In assembly" | blank</td></tr>
        <tr><td><code>genome_status</code></td><td>Overall genome availability</td><td>"Public" | "Sample Collected" | blank</td></tr>
        <tr><td><code>species_in_GOAT</code></td><td>Species present in GOAT genome portal?</td><td><strong>True</strong> | <strong>False</strong></td></tr>
        <tr class="section-header"><td colspan="3"><em>Database links (GBIF, GOAT, NBN, TOLQC, BLAST, BOLD) are clickable in the metadata panel but not searchable terms</em></td></tr>
      </tbody>
    </table>
    <div class="search-tips">
      <h3>Search Tips</h3>
      <ul>
        <li><strong>Exact match:</strong> Search <code>bags_grade: A</code> for all Grade A specimens</li>
        <li><strong>Partial match:</strong> Search <code>Empis</code> to find all Empis species</li>
        <li><strong>BIN search:</strong> Search <code>BOLD:ACD3004</code> to see all specimens in that BIN</li>
        <li><strong>Geographic filter:</strong> Search <code>United Kingdom</code> or <code>British Isles</code></li>
        <li><strong>Quality flags:</strong> Search <code>shares_BIN_with_other_species</code> to find potential misidentifications</li>
        <li><strong>UKSI gaps:</strong> Search <code>UKSI_no_specimens</code> to find UKSI-listed species still lacking BIOSCAN coverage</li>
      </ul>
    </div>
  </div>

</div>
</div><!-- end left-panel -->

<div class="right-panel">
{global_banner_html}
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
</div><!-- end right-panel -->
</div><!-- end page-body -->

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
    families   = scan_families()
    global_url = detect_global_tree()
    html       = build_html(families, global_url)
    OUTPUT_FILE.write_text(html, encoding="utf-8")

    print(f"Generated {OUTPUT_FILE} with {len(families)} families")
    if global_url:
        print("  [global]         Arthropoda_global")
    for f in families:
        print(f"  {f['order']:15s}  {f['family']}")
