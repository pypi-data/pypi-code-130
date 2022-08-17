from pydantic import BaseModel


class Server(BaseModel):
    name: str
    source_path: str
    host: str = None
    port: int = 22
    includes: str = ""
