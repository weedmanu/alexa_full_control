import ast

p = r'c:\Users\weedm\Downloads\alexa_full_control\cli\context.py'
try:
    with open(p, encoding='utf-8') as fh:
        s = fh.read()
    ast.parse(s)
    print('OK')
except SyntaxError as e:
    print('SyntaxError', e)
except Exception as e:
    print('Error', type(e), e)
