#!/usr/bin/env python3
"""
Runner debug pour visualize_install_diagrams.py — appelle le script et imprime où il écrit.
"""
import runpy
from pathlib import Path

ns = runpy.run_path('scripts/visualize_install_diagrams.py')
# Appeler ensure_dirs/write_puml_files s'ils existent dans le namespace
base = Path('scripts/visualize_install_diagrams.py').resolve().parent.parent
print('base', base)
if 'ensure_dirs' in ns:
    d = ns['ensure_dirs'](base)
    print('ensure_dirs returned:', d)
if 'write_puml_files' in ns:
    ns['write_puml_files'](d)
    print('write_puml_files invoked')
if 'write_html_viewer' in ns:
    h = ns['write_html_viewer'](d)
    print('write_html_viewer returned:', h)
print('Done')
