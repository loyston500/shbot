from __future__ import annotations
from typing import *

from .argparser import ArgumentParserHelpCallError, ArgumentParserParseError

import argparse

__all__ = ['CommandOutput', 'Stdout', 'Stderr', 'CommandError', 'CommandNotFoundError', 'CommandNotImplementedError']

class CommandError(Exception): pass

class CommandNotFoundError(CommandError): pass

class CommandNotImplementedError(CommandError): pass

class Std:
    def __init__(self, content: bytes):
        self.content = content

class Stdout(Std):
    def __repr__(self):
        return f"out<{repr(self.content)}>"

class Stderr(Std):
    def __repr__(self):
        return f"err<{repr(self.content)}>"


class CommandOutput:
    def __init__(self, stds: List[Std]=None, code=0):
        self.stds = stds if stds is not None else []
        self.code = code

    def stdout_write(self, content):
        if not isinstance(content, bytes):
            content = str(content).encode()

        self.stds.append(Stdout(content))

    def stderr_write(self, content):
        if not isinstance(content, bytes):
            content = str(content).encode()

        self.stds.append(Stderr(content))

    def set_code(self, code):
        self.code = code

    def __add__(self, content):
        self.stdout_write(content)
        return self

    def __sub__(self, content):
        self.stderr_write(content)
        return self

    def __matmul__(self, code):
        self.set_code(code)
        return self
    
    def __bytes__(self):
        return b''.join(self.get_stds())

    def __repr__(self):
        return f"<stds={self.stds} code={self.code}>"

    def clear(self):
        self.stds.clear()
        self.code = 0

    def get_outs(self):
        for std in self.stds:
            if isinstance(std, Stdout):
                yield std.content

    def get_errs(self):
        for std in self.stds:
            if isinstance(std, Stderr):
                yield std.content

    def get_stds(self):
        for std in self.stds:
            yield std.content
            
    def clear_stds(self):
        self.clear()
        
    def clear_outs(self):
        self.stds = [std for std in self.stds if not isinstance(std, Stdout)]
        
    def clear_errs(self):
        self.stds = [std for std in self.stds if not isinstance(std, Stderr)]


class Command:
    def __init__(self, coro, help=None, name=None):
        self._coro = coro
        self._help = help
        self.name = name

    def get_coro(self):
        return self._coro

    def get_help(self):
        return self._help

    def __repr__(self):
        return f"command<{self.name}>"

    def __call__(self, *args, **kwargs):
        return self.get_coro()(*args, **kwargs)

class Commands:
    def __init__(self, commands=None):
        self._commands = commands if commands is not None else {}

    def command(self, name=None, argparser=None):
        def factory(coro):

            if argparser is not None:
                argparser.prog = coro.__name__
                async def wrap(ctx, out, args, *_args, **kwargs):
                    try:
                        args = argparser.parse_args(args)

                    except ArgumentParserParseError as err:
                        out @ 1 - err.args[0]
                        argparser.error_message = None
                    except ArgumentParserHelpCallError as err:
                        out + argparser.format_help()
                        argparser.help = None
                    else:    
                        await coro(ctx, out, args, *_args, **kwargs)
                        out

                _help = argparser.format_help()
            else:
                async def wrap(ctx, out, *args, **kwargs):
                    await coro(ctx, out, *args, **kwargs)

                _help = coro.__doc__

            wrap.__name__ = coro.__name__
            wrap.__doc__ = coro.__doc__

            nonlocal name
            name = name or coro.__name__
            self._commands[name] = Command(wrap, help=_help)

            return wrap
        return factory

    def get(self, name):
        return self._commands.get(name)

commands = Commands()
