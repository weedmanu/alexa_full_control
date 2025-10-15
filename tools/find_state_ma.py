from pathlib import Path
s=Path('cli/context.py').read_text(encoding='utf-8')
for i,l in enumerate(s.splitlines(),start=1):
    if 'state_ma' in l:
        print(i,repr(l))
