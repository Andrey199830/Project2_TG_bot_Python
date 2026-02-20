from dataclasses import dataclass


@dataclass
class Group:
    id: int
    task_id: int
    GroupTask: int
    Name: str = ""
    
    