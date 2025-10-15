import ast, sys
p = r'c:\Users\weedm\Downloads\alexa_full_control\cli\context.py'
try:
    s = open(p, 'r', encoding='utf-8').read()
    ast.parse(s)
    print('OK')
except SyntaxError as e:
    print('SyntaxError', e)
except Exception as e:
    print('Error', type(e), e)
