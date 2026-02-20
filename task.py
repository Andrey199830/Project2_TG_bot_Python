from dataclasses import dataclass


@dataclass
class Task:
    id: int
    id_subtask: int
    text: str = ""
    is_done: bool = False
