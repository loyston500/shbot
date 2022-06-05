from __future__ import annotations
from typing import *
from io import BytesIO

from .base import Context as BaseContext, File, Files

__all__: List[str] = ['Context', 'File']

class Context(BaseContext):
    def __init__(self, message):
        self.message = message
        self.client_name = 'debug'
        
    async def send(self, content: str = None, files: Files = None) -> None:
        print(f"[DEBUG SEND] content = {repr(content)}, files = {[repr(file) for file in files]}")
        
    def get_attachments(self) -> Dict:
        return {'myfile': b'some content'}
        raise NotImplementedError
        
    async def fetch_attachment_content(self, attch) -> bytes:
        return b'some content'
        raise NotImplementedError
