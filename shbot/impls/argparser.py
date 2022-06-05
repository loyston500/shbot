from __future__ import annotations
from typing import *

import argparse

__all__: List[str] = ['ArgumentParser']

class ArgumentParserParseError(Exception): pass
class ArgumentParserHelpCallError(Exception): pass

class ArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super(ArgumentParser, self).__init__(*args, **kwargs)

    def error(self, error_message):
        raise ArgumentParserParseError(error_message)

    def add_argument(self, *args, **kwargs):
        super().add_argument(*args, **kwargs)
        return self

    def parse_args(self, *_args, **kwargs):
        try:
            args = super().parse_args(*_args, **kwargs)
        except SystemExit:
            args = None

        return args
    
    def print_help(self):
        raise ArgumentParserHelpCallError(self.format_help())




