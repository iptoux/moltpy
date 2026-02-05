from src.core.memory.Notes import MoltpyNotes

class MoltpyMemory:
    _instance = None

    def __init__(self) -> None:
        self.short_term_memory: dict = {
            "conversation": [],
            "notes":  MoltpyNotes.get_instance(),
        }
        self.long_term_memory: dict = {}

    @classmethod
    def get_instance(cls) -> "MoltpyMemory":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def get_notes(self) -> MoltpyNotes:
        return self.short_term_memory["notes"].note_get_all()