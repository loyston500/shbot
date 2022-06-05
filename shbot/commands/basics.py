from ..impls.command import commands
from ..impls.argparser import ArgumentParser

@commands.command()
async def echo(ctx, std, args, pipe=None):
    if pipe is not None:
        std + b''.join(pipe.get_stds())
    else:
        std + ' '.join(args)

@commands.command(argparser=ArgumentParser(description="puts text within a codeblock")
    .add_argument('text', metavar='TEXT', type=str, nargs='?', help='text')
    .add_argument("--language", "-l", metavar="LANG", type=str, help="highlight language")
    
)
async def cb(ctx, std, args, pipe=None):
    lang = args.language or ''
    
    if pipe is not None:
        text = bytes(pipe)
    else:
        text = args.text
        
    std + '```' + lang + '\n' + text + '```'
    
