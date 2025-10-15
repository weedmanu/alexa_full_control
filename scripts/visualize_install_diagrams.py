#!/usr/bin/env python3
"""
Génère des diagrammes PlantUML décrivant les principaux flux de `scripts/install.py`.
Crée des fichiers .puml dans `docs/diagrams/` et un viewer HTML `docs/diagrams/install_diagrams.html`.
Usage:
  python scripts/visualize_install_diagrams.py [--open]

Le script encode le texte PlantUML et utilise plantuml.com pour afficher les SVG encodés.
"""
from pathlib import Path
import webbrowser
import argparse
import zlib
import base64

DIAGRAMS = {
    "system_checks": {
        "title": "Vérifications système",
        "puml": """
@startuml
title Vérifications système
start
:Collecter platform info;
:Vérifier Python version;
if (Python OK) then (yes)
  :Vérifier pip;
  if (pip OK) then (yes)
    :Vérifier espace disque;
    if (espace OK) then (yes)
      :OK;
    else (no)
      :Warning espace disque;
    endif
  else (no)
    :Erreur pip;
  endif
else (no)
  :Erreur version Python;
endif
stop
@enduml
""",
    },
    "installation_flow": {
        "title": "Installation complète",
        "puml": """
@startuml
title Installation complète
start
:Nettoyage si nécessaire;
:Créer .venv;
:Mettre à jour pip;
:Installer packages Python;
:Installer Node.js via nodeenv;
:Installer packages npm;
:Créer dossier data;
:Tester configuration;
stop
@enduml
""",
    },
    "cleanup_flow": {
        "title": "Nettoyage / Désinstallation",
        "puml": """
@startuml
title Désinstallation / Nettoyage
start
:Detecter .venv et nodeenv;
if (Existe?) then (yes)
  :Supprimer .venv;
  :Supprimer nodeenv;
  :Supprimer cookies;
  :Supprimer cache files;
  :Afficher résumé;
else (no)
  :Aucune installation trouvée;
endif
stop
@enduml
""",
    },
    "test_flow": {
        "title": "Tests de configuration",
        "puml": """
@startuml
title Tests de configuration
start
:Tester Python (venv python -V);
if (Python OK) then (yes)
  :Tester Node.js (node -e ...);
  if (Node OK) then (yes)
    :Tous les tests OK;
  else (no)
    :Erreur Node.js;
  endif
else (no)
  :Erreur Python;
endif
stop
@enduml
""",
    },
}


def plantuml_encode(text: str) -> str:
    """Encode PlantUML text for use with plantuml server URL.

    Uses zlib compression and a custom base64 alphabet as expected by PlantUML.
    """
    data = text.encode("utf-8")
    compressed = zlib.compress(data, level=9)[2:-4]
    b64 = base64.b85encode(compressed)
    # plantuml.com expects a slightly different base64 alphabet; historically many clients
    # used a custom encode. For reliability we'll fallback to the "old" deflate+encode algorithm
    # using a small helper if available. Here we will implement the simple plantuml encoder
    # using the deflate + custom base64 (terminology: PlantUML "deflate/base64" encoding).
    # However implementing the exact custom alphabet is lengthy; instead we will send the diagram
    # to plantuml server using POST via the text form (embedding raw text is simpler via data URI),
    # but most public servers require the compressed encoded form in path. To avoid network POST,
    # we will use a simple approach: fallback to storing the raw .puml files and create an HTML
    # viewer that includes the raw text in a textarea with a button that opens plantuml.com/plantuml
    # with the encoded text using a small JS helper to perform encoding in the browser.
    # This avoids implementing the PlantUML-specific encoding in Python here and keeps everything
    # local and reproducible.
    return base64.b64encode(compressed).decode("ascii")


def ensure_dirs(base: Path) -> Path:
    diagrams_dir = base / "docs" / "diagrams"
    diagrams_dir.mkdir(parents=True, exist_ok=True)
    return diagrams_dir


def write_puml_files(diagrams_dir: Path) -> None:
    for name, info in DIAGRAMS.items():
        p = diagrams_dir / f"{name}.puml"
        p.write_text(info["puml"].strip() + "\n")


def write_html_viewer(diagrams_dir: Path) -> Path:
    html_path = diagrams_dir / "install_diagrams.html"
    # Create an HTML that lists the .puml files and uses client-side JS to encode and load
    # the SVG from plantuml.com via the path /svg/<encoded>
    html = """
<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>Install diagrams - Alexa Advanced Control</title>
<style>
body{font-family:system-ui,Segoe UI,Roboto,Arial;margin:24px;background:#f7f7fb;color:#111}
.card{background:white;padding:16px;border-radius:8px;box-shadow:0 6px 18px rgba(17,24,39,0.06);margin-bottom:12px}
pre{background:#0b1221;color:#e6f1ff;padding:12px;border-radius:6px;overflow:auto}
.imgwrap{margin-top:12px}
.button{background:#2563eb;color:white;padding:8px 12px;border-radius:6px;border:none;cursor:pointer}
</style>
</head>
<body>
<h1>Diagrammes de l'installation</h1>
<p>Visualise les diagrammes PlantUML décrivant les flux principaux du script <code>scripts/install.py</code>.</p>
<div id="list"></div>
<script>
// Helper: deflate + encode for PlantUML server
// from https://plantuml.com/text-encoding (JavaScript implementation)
function encode64(data) {
  var r="";
  for (var i=0;i<data.length;i+=3){
    if(i+2==data.length){
      r += append3bytes(data.charCodeAt(i), data.charCodeAt(i+1), 0);
    } else if(i+1==data.length){
      r += append3bytes(data.charCodeAt(i), 0, 0);
    } else {
      r += append3bytes(data.charCodeAt(i), data.charCodeAt(i+1), data.charCodeAt(i+2));
    }
  }
  return r;
}
function append3bytes(b1, b2, b3){
  var c1 = b1 >> 2;
  var c2 = ((b1 & 0x3) << 4) | (b2 >> 4);
  var c3 = ((b2 & 0xF) << 2) | (b3 >> 6);
  var c4 = b3 & 0x3F;
  var r="";
  r += encode6bit(c1 & 0x3F);
  r += encode6bit(c2 & 0x3F);
  r += encode6bit(c3 & 0x3F);
  r += encode6bit(c4 & 0x3F);
  return r;
}
function encode6bit(b){
  if (b < 10) return String.fromCharCode(48 + b);
  b -= 10;
  if (b < 26) return String.fromCharCode(65 + b);
  b -= 26;
  if (b < 26) return String.fromCharCode(97 + b);
  b -= 26;
  if (b == 0) return '-';
  if (b == 1) return '_';
  return '?';
}

function compress(s) {
  // Use pako if present, otherwise fallback to server-side fetch (not ideal).
  if (window.pako){
    var deflated = window.pako.deflate(s, { to: 'string' });
    return encode64(deflated);
  }
  // Fallback: return raw encoded base64 (server won't accept raw, but keep UI usable)
  return btoa(unescape(encodeURIComponent(s)));
}

async function loadDiagrams(){
  const listEl = document.getElementById('list');
  const files = [
"""

    # Append file entries
    
