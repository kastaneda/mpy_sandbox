
def foo(arg):
    print(arg)

foo(1)
foo('bar')
foo([1, 2, 3])

class foobar:
    def __init__(self, arg):
        print(arg)

x1 = foobar(1)
x2 = foobar('bar')
x3 = foobar([1, 2, 3])
