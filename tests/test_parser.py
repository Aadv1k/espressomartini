from espresso.Parser import Parser, StackFrame, Stack
from espresso.Lexer import Lexer

import pytest

parser = Parser()
lexer = Lexer()

def test_should_resolve_flat_call_stack():
    stack = parser.parse(lexer.lex("32, 33, 34, \"foo\""))

    assert stack.pop() == "foo"

    assert stack.pop() == 34
    assert stack.pop() == 33
    assert stack.pop() == 32

def test_should_resolve_nested_stack():
    stack = parser.parse(lexer.lex("foo(bar(), 123)"))

    top = stack.pop()
    assert isinstance(top, StackFrame)
    assert top.func_params.length == 2
