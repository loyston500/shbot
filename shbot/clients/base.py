### This holds the implementation of the base client
from __future__ import annotations
from typing import *

__all__: List[str] = ['Context', 'Files', 'File']

class File:
    def __init__(self, filename: str, fp: bytes):
        self.filename = filename
        self.fp = fp
        
    def __repr__(self):
        return f"<filename={repr(self.filename)}, fp={str(len(self.fp)) + 'B' if len(self.fp) > 1000 else repr(self.fp)}>"
    
Files = Iterable[File]

class Context:
    
    def __init__(self, message):
        self.message = message
        self.client_name = 'base'
        
    async def send(self, content: str = None, files: Files = None) -> None:
        raise NotImplementedError
    
    def get_attachments(self) -> Dict:
        raise NotImplementedError
    
    async def fetch_attachment_content(self, name: str) -> bytes:
        raise NotImplementedError
