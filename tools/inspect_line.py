p='c:/Users/weedm/Downloads/alexa_full_control/cli/context.py'
ln=402
with open(p,'r',encoding='utf-8') as f:
    for i,line in enumerate(f, start=1):
        if ln-2 <= i <= ln+2:
            print(f"{i}: {repr(line)}")
