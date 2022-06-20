from ..impls.command import commands, CommandNotImplementedError
from ..impls.argparser import ArgumentParser

@commands.command()
async def echo(ctx, out, args, pipe=None):
    if pipe is not None:
        out << b''.join(pipe.get_stds())
    else:
        out << ' '.join(args)

@commands.command(argparser=ArgumentParser(description="puts text within a codeblock")
    .add_argument('text', metavar='TEXT', type=str, nargs='?', help='text')
    .add_argument("--language", "-l", metavar="LANG", type=str, help="highlight language")
    
)
async def cb(ctx, out, args, pipe=None):
    lang = args.language or ''
    
    if pipe is not None:
        text = bytes(pipe)
    else:
        text = args.text
        
    out << '```' << lang << '\n' << text << '```'

