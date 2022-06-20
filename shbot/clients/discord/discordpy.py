from telnetlib import SE
from typing import *
from io import BytesIO
from typing_extensions import Self
from click import command

import discord

from shbot.impls.command import CommandOutput
from ..base import Context as BaseContext, File, Files

__all__: List[str] = ['Context', 'File']

class Context(BaseContext):
    def __init__(self, message):
        self.message = message
        self.client_name = 'discord'
        
    async def send(self, content: str = None, files: Files = None) -> None:
        if files is not None:
            files = [discord.File(filename=file.filename, fp=BytesIO(file.fp)) for file in files]
        await self.message.channel.send(content, files=files)
        
    def get_attachments(self) -> Dict:
        return {atch.filename: atch for atch in self.message.attachments}
        
    async def fetch_attachment_content(self, attch) -> bytes:
        return await attch.read()

    def __eq__(self, item: object) -> bool:
        return item == self.client_name

    

    
