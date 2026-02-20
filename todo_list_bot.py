import asyncio
import logging
from aiogram import Bot, Dispatcher, types
import typing
from aiogram.filters.command import Command, CommandObject
from aiogram.filters.callback_data import CallbackData
from aiogram import F

from settings import settings
from task import Task
from Groups import Group
from task_repository import TaskRepository
from db import init_db

logging.basicConfig(level=logging.INFO)

bot = Bot("8036165061:AAGhF5UWjeDepiD-u7iGveTUqUIx5kSSTGY")
dispatcher = Dispatcher()

Number: int
tasks = []

_repository = TaskRepository()

def _task_dto_to_string(task: Task) -> str:
    status_char = "\u2705" if task.is_done else "\u274c"
    return f"{task.id}: {task.text} | {status_char}"
    

def _subtask_dto_to_string(task: Task) -> str:
    status_char = "\u2705" if task.is_done else "\u274c"
    return f"   {task.id}: {task.id_subtask} {task.text} | {status_char}"


def _group_dto_to_string(group: Group) -> str:
    return f"{group.id}: {group.Name}"


def Tasks_group(task: Task) -> str:
    return f"{task.text}"

@dispatcher.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello!")

@dispatcher.message(Command("help"))
async def cmd_start(message: types.Message):
    await message.answer("/start - команда приветствия\n"
    "/todo %[name]% - добавить задачу\n"
    "/add_subtask %[номер задачи] [имя подзадачи]% - добавить подзадачу\n"
    "/find %[text]% - поиск задач/подзадач по тексту\n"
    "/list - список задач и подзадач\n"
    "/done %[number1]%- завершить задачу/подзадачу\n"
    "/clear - удалить задачу\n"
    "/reopen %[номер задачи]%\n"
    "/add_group %[name]%  - добавить группу\n"
    "/grouplist - лист групп\n"
    "/add_to_group %[номер группы] [номер задачи]% - добавление задачи к группе\n"
    "/group %[номер группы]% - список задач в группе\n"
    )
    


@dispatcher.message(Command("todo"))
async def handle_message_command(message: types.Message, command: CommandObject):
    command_args: str=command.args
    Number = _repository.add_task(None, command_args)

    await message.reply(f"Добавлена задача {Number}")
  

@dispatcher.message(Command("add_subtask"))
async def handle_message_command(message: types.Message, command: CommandObject):
    command_args_number_subtask: int=command.args.split(" ")[0]
    command_args_text: str=command.args.split(" ")[1]
    Number = _repository.add_task(command_args_number_subtask, command_args_text)

    await message.reply(f"Добавлена подзадача к родителю {command_args_number_subtask}")


@dispatcher.message(Command("list"))
async def get_list(message: types.Message):
    
    tasks = _repository.get_list()
    subtasks = _repository.get_sublist()

    Result = []

    if not tasks:
        text = "У вас нет задач!"
    else:
            for TASK in tasks:
                Result.append(_task_dto_to_string(TASK))
                Task_id = TASK.id
                for SUBTASK in subtasks:
                    Subtask_id= SUBTASK.id_subtask
                    if (Subtask_id==Task_id):
                        Result.append(_subtask_dto_to_string(SUBTASK))

            text = "\n".join(Result)

    await bot.send_message(message.chat.id, text)


@dispatcher.message(Command("find"))
async def find_list(message: types.Message, command: CommandObject):
    command_args1: str=command.args
    tasks = _repository.find_list(command_args1)
    if tasks:
            text = "\n".join([_task_dto_to_string(res) for res in tasks])
    else:
        text = "У вас нет задач с таким именем!"
    await bot.send_message(message.chat.id, text)


@dispatcher.message(Command("done"))
async def finish_task(message: types.Message, command: CommandObject):
    try:
        command_args: str=command.args
        
        task_ids = [int(id_) for id_ in command_args.split(" ")]
        _repository.finish_tasks(task_ids)
        text = f"Завершенные задачи: {task_ids}"
    except ValueError as e:
        text = "Неправильный номер задачи"

    await message.reply(text)

@dispatcher.message(Command("reopen"))
async def reopen_task(message: types.Message, command: CommandObject):
    try:
        command_args: str=command.args
        
        task_ids = [int(id_) for id_ in command_args.split(" ")]
        _repository.reopen_tasks(task_ids)
        text = f"Переоткрыли задачи: {task_ids}"
    except ValueError as e:
        text = "Неправильный номер задачи"

    await message.reply(text)



def _get_keyboard():
    buttons = [
        
            [types.InlineKeyboardButton(text="Удалить все!", callback_data="clear all")],
            [types.InlineKeyboardButton(text="Только завершенные", callback_data="clear completed")],
            [types.InlineKeyboardButton(text="Выберете, что необходимо удалить", callback_data="change")]
        
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard



@dispatcher.message(Command("clear"))
async def clear(message: types.Message):
    
    await message.reply("Вы хотите удалить ваши задачи?", reply_markup=_get_keyboard())


@dispatcher.callback_query(F.data.split(" ")[0] == "clear")
async def callbacks_num(callback: types.CallbackQuery):

    if callback.data.split(" ")[1] == "all":
        _repository.clear()
        
        await callback.message.edit_text(f"Задачи удалены!")
        
    
    if callback.data.split(" ")[1] == "completed":
        _repository.clear(is_done=True)
        
        await callback.message.answer("Задачи удалены!")
        

@dispatcher.callback_query((F.data == "change"))
async def callbacks_del(callback: types.CallbackQuery):
           
        await callback.message.reply("Введите команду /cl [строка]")
        
        
@dispatcher.message(Command("cl"))
async def clear(message: types.Message,  command: CommandObject):
         
        try:
            command_args: str=command.args
        
            task_ids = command_args
            _repository.clearChange(task_ids)

        except ValueError as e:
            text = "Неправильный номер задачи"

        await message.answer(f"Выбранные задачи удалены!")

@dispatcher.message(Command("add_group"))
async def handle_message_command(message: types.Message, command: CommandObject):
    command_args: str=command.args
    Number_groups = _repository.add_group(command_args, None, None)
                                    
    await message.reply(f"Добавлена группа {Number_groups}")


@dispatcher.message(Command("grouplist"))
async def get_list(message: types.Message):

    groups = _repository.get_group()
    Result = []

    if not groups:
        text = "У вас нет групп!"
    else:
            for GROUPS in groups:
                Result.append(_group_dto_to_string(GROUPS))
            
            text = "\n".join(Result)

    await bot.send_message(message.chat.id, text)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dispatcher.start_polling(bot)



@dispatcher.message(Command("add_to_group"))
async def handle_message_command(message: types.Message, command: CommandObject):
    command_args: str=command.args
    NumGroup = command_args.split(" ")[0]
    NumTask = command_args.split(" ")[1]
    _repository.add_group(None, NumGroup, NumTask)

    await message.reply(f"Задача {NumTask} Добавлена к группе {NumGroup}")


@dispatcher.message(Command("group"))
async def get_group_list(message: types.Message, command: CommandObject):
    
    command_args: str=command.args
    NumGroup = command_args.split(" ")[0]
    groups = _repository.get_group_task(NumGroup)

    Result = []

    if not groups:
        text = "У вас нет задач в данной группе!"
    else:
            for tasks in groups:
                #print(f"tasks={tasks}")
                Result.append(Tasks_group(tasks))
        
            text = "\n".join(Result)

    await bot.send_message(message.chat.id, text)



if __name__ == "__main__":
    init_db()
    asyncio.run(main())