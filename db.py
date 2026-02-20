from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Boolean, ForeignKey

from settings import settings


engine = create_engine(settings["DB_STRING"])
meta = MetaData()

tasks = Table(
    "tasksA",
    meta,
    Column("id", Integer, primary_key=True),
    Column("id_subtask", ForeignKey("tasksA.id")),
    Column("text", String, nullable=False),
    Column("is_done", Boolean, nullable=False, default=False),
)

group = Table(
    "Group",
    meta,
    Column("id", Integer, primary_key=True),
    Column("Name", String, nullable=True),
    Column("GroupTask", ForeignKey("Group.id")),
    Column("id_task", ForeignKey("tasksA.id")),
)


def init_db():
    
    with engine.connect():
        meta.drop_all(engine)
        meta.create_all(engine)
