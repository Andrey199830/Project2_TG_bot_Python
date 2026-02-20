from db import tasks, group, engine
from task import Task
from Groups import Group

from typing import List

from sqlalchemy.sql.operators import ilike_op, like_op

class TaskRepository:
    def add_task(self, id_subtask: int, text: str):
        query = tasks.insert().values(id_subtask=id_subtask, text=text)

        with engine.connect() as conn:
            Number =  conn.execute(query).inserted_primary_key[0]  
            conn.commit()              
        
        return Number

   
    def get_list(self, is_done=None) -> List[Task]:
        query = tasks.select()

        if is_done != None:
            query = query.where(is_done=is_done)

        resultTask = []
        
        with engine.connect() as conn:
            resultTask = [
                Task(id = id, id_subtask=id_subtask , text=text, is_done=is_done)
                for id, id_subtask, text, is_done in conn.execute(query.where(tasks.c.id_subtask==None).order_by(tasks.c.id))
            ]
            
        return resultTask


    def get_sublist(self, is_done=None) -> List[Task]:
        query = tasks.select()

        if is_done != None:
            query = query.where(is_done=is_done)

        resultSubTask = []
        
        with engine.connect() as conn:   
            resultSubTask = [
                Task(id = id, id_subtask=id_subtask , text=text, is_done=is_done)
                for id, id_subtask, text, is_done in conn.execute(query.where(tasks.c.id_subtask!=None).order_by(tasks.c.id))
            ]

        return resultSubTask

    
    def find_list(self, findText: str) -> List[Task]:
        query = tasks.select()

        result = []
        with engine.connect() as conn:
            result = [
                Task(id=id,id_subtask=id_subtask, text=text, is_done=is_done)
                for id, id_subtask, text, is_done in conn.execute(query.filter(like_op(tasks.c.text, f'%{findText}%'))).all()
            ]

        return result
   
   
   
    def finish_tasks(self, ids: List[int]):

        with engine.connect() as conn:
            Finishresult = [
                    Task(id=id,id_subtask=id_subtask, text=text, is_done=is_done)
                    for id, id_subtask, text, is_done in conn.execute(tasks.select().where(tasks.c.id==ids[0]))
             ]

            for res in Finishresult:
                if (res.id_subtask != None):
                    query = tasks.update().where(tasks.c.id==ids[0]).values(is_done=True)
                    conn.execute(query)
                else:
                    query = tasks.update().where(tasks.c.id==ids[0]).values(is_done=True)
                    query1 = tasks.update().where(tasks.c.id_subtask==ids[0]).values(is_done=True)
                    conn.execute(query)
                    conn.execute(query1)
              
            conn.commit()

    
    
    def reopen_tasks(self, ids: List[int]):
        query = tasks.update().where(tasks.c.id.in_(ids)).values(is_done=False)
        with engine.connect() as conn:
            conn.execute(query)
            conn.commit()


    def clear(self, is_done=None):

        if is_done is not None:
                Done = []
                Done = [res.id for res in engine.connect().execute(tasks.select().where(tasks.c.is_done == True, tasks.c.id_subtask != None) )]
                for i in range(len(Done)):
                    self.clearChange(Done[i])

                Done = []
                Done = [res.id for res in engine.connect().execute(tasks.select().where(tasks.c.is_done == True, tasks.c.id_subtask == None) )]
                
                for i in range(len(Done)):
                    self.clearChange(Done[i])
       
        else:
            with engine.connect() as conn:
                query=group.delete().where(group.c.id_task != None)
                conn.execute(query)

                query = tasks.delete()
                conn.execute(query)

                conn.commit()

    def clearChange(self, id):

         with engine.connect() as conn:
            Finishresult = [
                    Task(id=id, id_subtask=id_subtask, text=text, is_done=is_done)
                    for id, id_subtask, text, is_done in conn.execute(tasks.select().where(tasks.c.id==id))
             ]

            for res in Finishresult:
                if (res.id_subtask != None):
                    query = tasks.delete().where(tasks.c.id==id)
                    conn.execute(query)
                else:
                    query=group.delete().where(group.c.id_task == id)
                    conn.execute(query)
                    
                    query = tasks.delete().where(tasks.c.id_subtask==id)
                    query1 = tasks.delete().where(tasks.c.id==id)

                    conn.execute(query)
                    conn.execute(query1)
            
            conn.commit()

    

    def add_group(self, Name: str, GroupTask: int, id_task: int):
        query = group.insert().values(Name=Name, GroupTask = GroupTask, id_task=id_task)
        
        with engine.connect() as conn:
            Number =  conn.execute(query).inserted_primary_key[0]  
            conn.commit()
            
        return Number


    def get_group(self) -> List[Group]:
        query = group.select()

        resultGroup = []
        
        with engine.connect() as conn:

            resultGroup  = [
                Group(id = id, Name=Name, GroupTask = GroupTask, task_id = task_id )
                for id, Name, GroupTask, task_id in conn.execute(query.where(group.c.GroupTask==None).order_by(group.c.id))
            ]
        return resultGroup
    

    def get_group_task(self, NumGroup:int) -> List[Task]:
        query = group.select()
        query1 = tasks.select()
    
        resultGroup = []
        resultTasks = []
        Res = []
        
        with engine.connect() as conn:
            resultGroup  = [
                Group(id = id, Name=Name, GroupTask = GroupTask, task_id = task_id )
                for id, Name, GroupTask, task_id in conn.execute(query.where(group.c.GroupTask==NumGroup))
            ]
            
            for resTasks in resultGroup:
        
                resultTasks=[]
                resultTasks=[
                    Task(id=id, id_subtask=id_subtask, text=text, is_done=is_done)
                    for id, id_subtask, text, is_done in conn.execute(query1.where(tasks.c.id==resTasks.task_id))                
                ]
                Res.append(resultTasks[0])

        return Res