
def foo(*args):
    print(*args)

def bar(name, *args):
    for a in args:
        print(name, ':', a)

def baz(name, *args):
    print(name)
    print(args)

foo('aaa', 'bbb', 'ccc')
bar('aaa', 'bbb', 'ccc')
baz('aaa', 'bbb', 'ccc')
