from __future__ import annotations
from typing import *

from ..clients.base import Context, File
from .shparser import Instrs, InstrType
from .command import Command, CommandOutput, Commands, CommandNotFoundError
from io import BytesIO

__all__: List[str] = ['Interpreter']

class Interpreter:
    async def interpret(self, ctx: Context, commands: Commands, instrs: Instrs):
        out_files: List[File] = []
        in_files_cache: Dict[str, Any] = {}
        in_file: Optional[CommandOutput] = None
        pipe: Optional[CommandOutput] = None
        out: CommandOutput = CommandOutput()
        for instr in instrs:
            instr_type = instr.instr_type
            arg1, *args = instr.args


            if instr_type == InstrType.IN:
                filename = arg1

                names = ctx.get_attachments()

                if filename not in names:
                    raise Exception

                if filename in in_files_cache:
                    content = in_files_cache[filename]
                else:
                    content = await ctx.fetch_attachment_content(names[filename])
                    in_files_cache[filename] = content
                    in_file = CommandOutput()
                    in_file + content


            elif instr_type in (InstrType.OUT, InstrType.OUT1, InstrType.OUT2):
                filename = arg1

                if out is None:
                    raise Exception
                elif instr_type == InstrType.OUT:
                    fp = b''.join(out.get_stds())
                    out.clear_stds()
                elif instr_type == InstrType.OUT1:
                    fp = b''.join(out.get_outs())
                    out.clear_outs()
                elif instr_type == InstrType.OUT2:
                    fp = b''.join(out.get_errs())
                    out.clear_errs()

                out_files.append(File(filename=filename, fp=fp))

            else:
                command_name = arg1
                command = commands.get(command_name)

                if command is None:
                    raise CommandNotFoundError(f'command {repr(command_name)} not found')

                if instr_type == InstrType.PIPE:
                    pipe = out
                    out = CommandOutput()
                    await command(ctx, out, args, pipe=in_file or pipe)
                elif instr_type == InstrType.EVAL:
                    out.clear_stds()
                    await command(ctx, out, args, pipe=in_file)
                
                in_file = None

        content = b''.join(out.get_stds()).decode('utf-8', 'replace') or "** **"
        await ctx.send(content[:2000], files=out_files)





