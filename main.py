from enum import Enum, auto
from typing import Union, List, NamedTuple

import pprint

import random

class EspressoInvalidSyntax(Exception):
    pass

class StackFrame(NamedTuple):
    func_chain : List[str]
    func_params: List[Union[int, str, 'StackFrame']]

class Stack:
    def __init__(self):
        self.stack = []

    @property
    def length(self):
        return len(self.stack)

    def peek(self):
        if len(self.stack) == 0:
            return None
        return self.stack[self.length - 1]

    def push(self, f):
        self.stack.append(f)
        
    def pop(self):
        if len(self.stack) == 0:
            return None
        return self.stack.pop()

    def __iter__(self):
        return iter(self.stack)

class TokenType(Enum):
    LPAREN = auto()
    RPAREN = auto()
    DOT = auto()

    INTEGER = auto()
    STRING = auto()
    IDENTIFIER = auto()

class Token(NamedTuple):
    type: TokenType
    value: str
    position: int

class Lexer:
    def __init__(self):
        self.input = None
        self.cursor = -1

    def lex(self, input_string):
        self.input = input_string.strip().replace("\n", " ")

        tokens = []

        while self.advance() is not None:
            if self.cur() == ".":
                tokens.append(Token(TokenType.DOT, ".", self.cursor))
            elif self.cur() == ",":
                pass
            elif self.cur() == "(":
                tokens.append(Token(TokenType.LPAREN, "(", self.cursor))
            elif self.cur() == ")":
                tokens.append(Token(TokenType.RPAREN, ")", self.cursor))
            elif self.cur() == "\"":
                n = self.find_next_index("\"")
                if n is None:
                    raise EspressoInvalidSyntax(f"Unterminated string literal at position {self.cursor}")
                tokens.append(Token(TokenType.STRING, self.input[self.cursor + 1:n], self.cursor))
                self.cursor = n 
            elif self.cur() == " ":
                continue
            elif self.cur().isdigit():
                start = self.cursor
                end = self.cursor
                while end < len(self.input) and self.input[end].isdigit():
                    end+=1
                tokens.append(Token(TokenType.INTEGER, self.input[start:end], start))
                self.cursor = end - 1
            elif self.cur().isalpha():
                start = self.cursor
                end = self.cursor
                while end < len(self.input) and self.input[end].isalpha():
                    end+=1
                tokens.append(Token(TokenType.IDENTIFIER, self.input[start:end], start))
                self.cursor = end - 1
            else:
                raise EspressoInvalidSyntax(f"Invalid character encountered at position {self.cursor}: {self.cur()}")

        return tokens

    def cur(self):
        return self.input[self.cursor]

    def find_next_index(self, char):
        for i in range(self.cursor + 1, len(self.input)):
            if self.input[i] == char:
                return i
        return None

    def retreat(self):
        if self.cursor == 0:
            return None

        self.cursor -= 1
        return self.cursor

    def advance(self):
        if self.cursor == (len(self.input) - 1):
            return None

        self.cursor += 1
        return self.cursor

class Parser:
    def __init__(self):
        self.call_stack = Stack()
        self.tokens = None
    
    def next_token(self, i):
        if i + 1 >= len(self.tokens):
            return None
        return self.tokens[i+1]
    
    def parse_call_chain(self, at: int) -> tuple[List[Token], int]:
        assert self.tokens[at].type == TokenType.IDENTIFIER
        call_chain_tokens = [self.tokens[at]]
        offset = 0

        i = 0
        while (i < len(self.tokens) - 1) and (self.tokens[i].type != TokenType.LPAREN):
            cur, nxt = self.tokens[i], self.next_token(i)

            if cur.type == TokenType.DOT:
                if nxt is None or nxt.type != TokenType.IDENTIFIER:
                    raise EspressoInvalidSyntax("Invalid syntax at col {}".format(cur.position))

                offset += 2
                call_chain_tokens.append(nxt)
            i+=1

        return call_chain_tokens, offset

    def get_closing_paren_index(self, tokens, idx):
        stack = Stack()

        for i in range(idx, len(tokens)):
            if tokens[i].type == TokenType.RPAREN:
                if stack.length == 1:
                    return i
                else:
                    stack.pop()
            elif tokens[i].type == TokenType.LPAREN:
                stack.push(True)

        return None

    def parse_func_params(self, at: int) -> List[Token]:
        assert self.tokens[at].type == TokenType.IDENTIFIER
        offset =  0

        if self.tokens[at+1].type != TokenType.LPAREN:
            return [], offset

        closing_paren_index = self.get_closing_paren_index(self.tokens, at+1)
        if not closing_paren_index:
            raise EspressoInvalidSyntax("( Was never closed at {}".format(self.tokens[at+1].position))

        func_param_tokens = self.tokens[at+2:closing_paren_index]
        return self.parse(func_param_tokens), closing_paren_index - at
        

    def parse(self, tokens: List[Token]) -> Stack:
        self.tokens = tokens
        stack = Stack() 

        i = 0 
        while i < len(tokens):
            cur, nxt = tokens[i], self.next_token(i)

            if cur.type == TokenType.IDENTIFIER:
                call_chain_tokens, offset = self.parse_call_chain(i)
                call_chain = [tkn.value for tkn in call_chain_tokens]
                i += offset

                arguments, offset = self.parse_func_params(i)

                i += offset
                stack.push(StackFrame(call_chain, arguments))

                i += offset
            elif cur.type in {TokenType.STRING, TokenType.INTEGER}:
                stack.push(cur.value if cur.type == TokenType.STRING else int(cur.value))

            i+=1

        return stack
