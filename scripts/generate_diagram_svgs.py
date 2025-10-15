#!/usr/bin/env python3
"""
Génère des SVG à partir des .puml dans docs/diagrams/ en interrogeant plantuml.com.
Usage:
  python scripts/generate_diagram_svgs.py
"""
from pathlib import Path
import zlib
import urllib.request

PLANTUML_SERVER = 'https://www.plantuml.com/plantuml/svg/'
BASE = Path(__file__).resolve().parent.parent
DIAGRAMS_DIR = BASE / 'docs' / 'diagrams'
# Process all .puml files in DIAGRAMS_DIR so new diagrams are picked up automatically
NAMES = None

ALPHABET = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_'


def encode_plantuml(data: bytes) -> str:
    # encode bytes into PlantUML custom base64
    out = []
    def append3bytes(b1, b2, b3):
        c1 = b1 >> 2
        c2 = ((b1 & 0x3) << 4) | (b2 >> 4)
        c3 = ((b2 & 0xF) << 2) | (b3 >> 6)
        c4 = b3 & 0x3F
        out.append(ALPHABET[c1 & 0x3F])
        out.append(ALPHABET[c2 & 0x3F])
        out.append(ALPHABET[c3 & 0x3F])
        out.append(ALPHABET[c4 & 0x3F])
    for i in range(0, len(data), 3):
        b1 = data[i]
        b2 = data[i+1] if i+1 < len(data) else 0
        b3 = data[i+2] if i+2 < len(data) else 0
        append3bytes(b1, b2, b3)
    return ''.join(out)


def deflate_and_encode(text: str) -> str:
    data = text.encode('utf-8')
    compressed = zlib.compress(data, 9)[2:-4]
    return encode_plantuml(compressed)


def fetch_svg(encoded: str) -> bytes:
    url = PLANTUML_SERVER + encoded
    with urllib.request.urlopen(url, timeout=30) as resp:
        return resp.read()


def main():
    DIAGRAMS_DIR.mkdir(parents=True, exist_ok=True)
    # discover all .puml files
    puml_files = sorted(DIAGRAMS_DIR.glob('*.puml'))
    if not puml_files:
        print(f"No .puml files found in {DIAGRAMS_DIR}")
        return
    for puml in puml_files:
        svg = puml.with_suffix('.svg')
        name = puml.stem
        print(f"Processing {puml}")
        # Read PUML with robust encoding fallback (utf-8, then cp1252)
        try:
            text = puml.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            try:
                text = puml.read_text(encoding='cp1252')
                print(f"  (read with cp1252 fallback)")
            except Exception:
                # final fallback to latin-1 with replacement
                text = puml.read_bytes().decode('latin-1', errors='replace')
                print("  (read with latin-1 fallback, invalid chars replaced)")
        try:
            enc = deflate_and_encode(text)
            data = fetch_svg(enc)
            svg.write_bytes(data)
            print(f"Wrote {svg}")
        except Exception as e:
            print(f"Failed {name}: {e}")

if __name__ == '__main__':
    main()
