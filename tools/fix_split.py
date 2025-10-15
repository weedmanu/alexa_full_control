from pathlib import Path

p=Path('cli/context.py')
s=p.read_text(encoding='utf-8')
old='self._sync_service = SyncService(self.auth, self.config, self.state_ma\nchine)'
if old in s:
    s=s.replace(old,'self._sync_service = SyncService(self.auth, self.config, self.state_machine)')
    p.write_text(s,encoding='utf-8')
    print('fixed')
else:
    print('pattern not found')
