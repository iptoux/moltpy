from datetime import datetime, timezone
from src.core.Types import Note, NoteType

class MoltpyNotes:
    _instance = None

    def __init__(self) -> None:
        self.stm: list = []
        self.ltm: list = []

    @classmethod
    def get_instance(cls) -> "MoltpyNotes":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def note_add(self, note_type: NoteType, title: str, content: str) -> bool:
        for note in self.stm:
            if note.title == title or note.content == content:
                return False
        note = Note(type=note_type, title=title, content=content, created_at=datetime.now(timezone.utc))
        self.stm.append(note)
        return True
    
    def note_del_by_id(self, index):
        if 0 <= index < len(self.stm):
            del self.stm[index]

    def note_del_by_title(self, title):
        self.stm = [note for note in self.stm if note.title != title]

    def _note_del_all(self):
        self.stm = []

    def note_get_all(self):
        return self.stm
    
    def note_get_by_id(self, index):
        if 0 <= index < len(self.stm):
            return self.stm[index]
        return None
    
    def note_get_by_title(self, title):
        for note in self.stm:
            if note.title == title:
                return note
        return None
