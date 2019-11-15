# Do not use auto-formatting tools to format this file!
from checkpoint_test_base import R
from Lutil.checkpoints import InlineCheckpoint


class Foo:
    pass


def strange_statement_1(a, b):
    f = Foo()
    f.c = "reset"

    with InlineCheckpoint       (watch=('a'        , "b"), produce       =    [     "f.c"  ])    :
        R()
        f.c = a+b

    return f.c


def strange_statement_2(a, b):
    f = Foo()
    f.c = "reset"

    with InlineCheckpoint(watch=('a',"b"),produce=["f.c"]):
        R()
        f.c = a+b

    return f.c


def strange_statement_3(a, b):
    f = Foo()
    f.c = "reset"

    with InlineCheckpoint(
        watch=('a',
        "b"),

        produce=["f.c"
        ]

                 ):
        R()
        f.c = a+b

    return f.c
