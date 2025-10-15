from pathlib import Path

p = Path('cli/context.py')
s = p.read_text(encoding='utf-8')

# Replace common broken splits of 'state_machine' introduced by earlier edits
s = s.replace('state_ma\nchine', 'state_machine')
s = s.replace('state_mac\nhine', 'state_machine')
s = s.replace('self.state_\nmachine', 'self.state_machine')

p.write_text(s, encoding='utf-8')
print('done')
