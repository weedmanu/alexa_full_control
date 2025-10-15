import runpy
from pathlib import Path
ns = runpy.run_path('scripts/visualize_install_diagrams.py')
base = Path('scripts/visualize_install_diagrams.py').resolve().parent.parent
print('base=', base)
diagrams_dir = base / 'docs' / 'diagrams'
print('diagrams_dir=', diagrams_dir)
for name in ['system_checks.puml','installation_flow.puml','cleanup_flow.puml','test_flow.puml']:
    p = diagrams_dir / name
    print(name, 'exists?', p.exists())
