p='c:/Users/weedm/Downloads/alexa_full_control/cli/context.py'
with open(p,encoding='utf-8') as f:
    for i,line in enumerate(f, start=1):
        if 388 <= i <= 406:
            print(f"{i:4}: {line.rstrip()}")
