from .buffer import Buffer
from .position import Position


class ParseException(Exception):

    def __init__(self, 
            message: str, 
            buffer: Buffer, 
            position: Position = None):
        
        self.message = message

        # Evaluate position
        if not position:
            position = buffer.copy_position()
        self.position = position

        # Check in range, get text from line
        if position.index > buffer.length or position.line > buffer.line_count:
            raise Exception("buffer position out-of-bounds")
        self.excerpt = buffer.line_text(position.line).strip()

        # Evaluate caret offset
        if position.column == -1:
            self.caret_position = len(self.excerpt)
        else:
            indentation = buffer.line_indentation(position.line)
            self.caret_position = position.column - indentation - 1

    def __str__(self) -> str:
        caret_indent = " " * self.caret_position
        return f"""{self.position} ({self.message})
    {self.excerpt}
    {caret_indent}^"""