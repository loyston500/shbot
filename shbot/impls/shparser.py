#! /usr/bin/env python

from __future__ import annotations
from typing import *
from enum import Enum

__all__: List[str] = ["Parser", "Token", "TokenType"]


OPERATORS = ["|", ">", "1>", "2>", "<", "<<", "&"]
EOLS = [";"]


class TokenType(Enum):
    STRING: str = "STRING"
    OP: str = "OP"
    #EOL: str = "EOL"


class InstrType(Enum):
    EVAL: str = 'EVAL'
    PIPE: str = '|'
    OUT: str = '>'
    OUT1: str = '1>'
    OUT2: str = '2>'
    IN: str = '<'

class Instr:
    __slots__ = ('instr_type', 'args')
    
    def __init__(self, instr_type: InstrType, *args: str):
        self.instr_type = instr_type
        self.args = list(args)
        
    def add_argument(self, arg: str) -> Instr:
        self.args.append(arg)
        return self
        
    def __repr__(self):
        return f"Instr<type={self.instr_type} args={self.args}>"

Instrs = List[Instr]

class Token:
    __slots__ = ('string', 'token_type')
    
    def __init__(self, string: str, token_type: TokenType):
        self.string = string
        self.token_type = token_type

    def __repr__(self):
        return f"<string={repr(self.string)}, type={self.token_type}>"

    def __str__(self):
        return self.string

class ParserError(Exception): pass
class ParserEOFError(ParserError): pass
class ParserBadCharError(ParserError): pass

class Parser:
    def mlc(self, c: str) -> bool:
        """match lower case"""
        return ord(c) >= 97 and ord(c) <= 122

    def muc(self, c: str) -> bool:
        """match upper case"""
        return ord(c) >= 65 and ord(c) <= 90

    def mnum(self, c: str) -> bool:
        """match numbers"""
        return ord(c) >= 48 and ord(c) <= 57

    def mident(self, c: str) -> bool:
        """match identifier"""
        return self.mlc(c) or self.muc(c) or self.mnum(c)

    def midentsym(self, c: str) -> bool:
        """match identifier along with symbols"""
        return self.mident(c) or self.msym(c)

    def mws(self, c: str) -> bool:
        """match whitespaces"""
        return c in " \n\t"

    def msym(self, c: str) -> bool:
        """match allowed symbols"""
        return c in "./,:+=-_"

    def mop(self, c: str) -> bool:
        """match operators"""
        return c in OPERATORS

    def repvars(self, string: str, variables) -> str:
        pass

    def tokenize(self, string: str, variables={}) -> List[Token]:
        tokens = []
        temp: List[str] = []
        i = 0
        while i < len(string):
            c = string[i]

            if c in EOLS:
                if temp: tokens.append(Token("".join(temp), TokenType.STRING))
                temp.clear()

                tokens.append(Token(c, TokenType.OP))

            elif c == "$":
                vtemp = []
                i += 1
                while i < len(string):
                    if self.mident(string[i]):
                        vtemp.append(string[i])
                    else:
                        break
                    i += 1
                i -= 1
                vtemp_str = "".join(vtemp)

                if vtemp_str in variables:
                    temp.extend(variables[vtemp_str])

            elif c in ("1", "2"):
                j = i + 1
                if j < len(string):
                    if string[j] == ">":

                        if temp: tokens.append(Token("".join(temp), TokenType.STRING))
                        temp.clear()

                        tokens.append(Token(c + ">", TokenType.OP))
                        i = j
                    else:
                        temp.append(c)
                else:
                    temp.append(c)

            elif c in (">", "|", "&"):
                if temp: tokens.append(Token("".join(temp), TokenType.STRING))
                temp.clear()

                tokens.append(Token(c, TokenType.OP))

            elif c == "<":
                if temp: tokens.append(Token("".join(temp), TokenType.STRING))
                temp.clear()

                j = i + 1
                if j < len(string):
                    if string[j] == "<":
                        tokens.append(Token("<<", TokenType.OP))
                        i = j
                    else:
                        tokens.append(Token("<", TokenType.OP))

            elif c == "'":
                n = string.find("'", i + 1)

                if n == -1:
                    raise ParserEOFError(f"EOF while scanning for the string literal")

                temp.append(string[i + 1 : n])
                i = n

            elif c == '"':
                n = string.find('"', i + 1)

                if n == -1:
                    raise ParserEOFError(f"EOF while scanning for the string literal")

                content = string[i + 1 : n]
                new_content: List[str] = []
                j = 0
                while j < len(content):
                    if content[j] == "$":
                        vtemp = []
                        j += 1
                        while j < len(content):
                            if self.mident(content[j]):
                                vtemp.append(content[j])
                            else:
                                break
                            j += 1
                        j -= 1
                        vtemp_str = "".join(vtemp)
                        if vtemp_str in variables:
                            new_content.extend(variables[vtemp_str])
                    else:
                        new_content.append(content[j])
                    j += 1

                temp.append("".join(new_content))
                i = n

            elif self.midentsym(c):
                while i < len(string):
                    if self.midentsym(string[i]):
                        temp.append(string[i])
                    else:
                        break
                    i += 1
                i -= 1

            elif self.mws(c):
                if temp: tokens.append(Token("".join(temp), TokenType.STRING))
                temp.clear()

            else:
                raise ParserBadCharError(f"Illegal/Bad char {c}")

            i += 1

        if temp: tokens.append(Token("".join(temp), TokenType.STRING))

        if tokens and ((tokens[-1].token_type == TokenType.OP and tokens[-1].string != ';') or (tokens[-1].token_type == TokenType.STRING)):
            tokens.append(Token(';', TokenType.OP))

        return tokens

    def parse(self, tokens: List[Token]) -> Instrs:
        instrs: Instrs = []
        i = 0
        instr: Instr = Instr(InstrType.EVAL)
        while i < len(tokens):
            if tokens[i].token_type == TokenType.OP:
                m = tokens[i].string

                if m == '<':
                    i += 1
                    if i < len(tokens):
                        instrs.append(Instr(InstrType.IN, tokens[i].string))

                    else:
                        raise Exception('EOL ')
                else:
                    instrs.append(instr)
                    if m == '|':
                        instr = Instr(InstrType.PIPE)
                    elif m == '>':
                        instr = Instr(InstrType.OUT)
                    elif m == '1>':
                        instr = Instr(InstrType.OUT1)
                    elif m == '2>':
                        instr = Instr(InstrType.OUT2)
                    elif m == ';':
                        instr = Instr(InstrType.EVAL)

            elif tokens[i].token_type == TokenType.STRING:
                instr.add_argument(tokens[i].string)

            i += 1

        return instrs


def test() -> None:
    parser = Parser()
    print(parser.parse(parser.tokenize("""./shparser.py -t 'foo|bar > baz;' < ffff < fff ; lol lolo lol""")))

if __name__ == "__main__":
    import argparse

    parser: Any  = argparse.ArgumentParser(description="sh parsing tools for shbot")
    parser.add_argument(
        "--tokenize", "-t", metavar="STRING", type=str, help="tokenize the given string"
    )
    parser.add_argument("--variables", '-v', nargs='+', help="variables to be passed to the tokenizer")
    parser.add_argument("--test", action='store', nargs='*', help="run the test function")

    args = parser.parse_args()

    if args.tokenize is not None:
        if args.variables is not None:
            variables = {n: v for n, v in zip(args.variables[::2], args.variables[1::2])}
        else:
            variables = {}

        parser = Parser()
        tokens = parser.tokenize(args.tokenize, variables=variables)
        print(tokens)
        ast = parser.parse(tokens)
        print(ast)

    elif args.test is not None:
        test()
