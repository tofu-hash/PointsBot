from handlers.callback_query import *
from handlers.messages import *
from handlers.init import *

dp.register_message_handler(start_cmd_handler, commands=['start'], state='*')
dp.register_message_handler(help_cmd_handler, commands=['help'], state='*')
dp.register_message_handler(get_sticker_id_handler, content_types=['sticker'], state='*')
dp.register_message_handler(stats_cmd_handler, commands=['stats'], state='*')
dp.register_message_handler(last_task_cmd_handler, commands=['lasttask'], state='*')
dp.register_message_handler(tasks_cmd_handler, commands=['tasks'], state='*')

dp.register_message_handler(view_task_cmd_handler, lambda msg: '/task' in msg.text and len(msg.text) > 5, state='*')
dp.register_message_handler(create_task_cmd_handler, commands=['task'], state='*')
dp.register_message_handler(set_task_description_handler, content_types=['text', 'photo'],
                            state=TasksStatesGroup.set_task_description)

dp.register_callback_query_handler(complete_task_handler, lambda msg: 'complete_task_' in msg.data, state='*')
dp.register_callback_query_handler(delete_task_handler, lambda msg: 'delete_task_' in msg.data, state='*')
dp.register_callback_query_handler(cancel_handler, lambda msg: msg.data == 'cancel', state='*')

dp.register_message_handler(set_task_description_handler, content_types=['text', 'photo'])


async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            BotCommand('task', 'Добавить задачу'),
            BotCommand('lasttask', 'Последняя задача'),
            BotCommand('tasks', 'Просмотреть задачи'),
            BotCommand('stats', 'Статистика поинтов'),
            BotCommand('help', 'Помощь по командам бота'),
            BotCommand('start', 'Перезапуск бота')
        ]
    )


async def start(dispatcher) -> None:
    bot_name = dict(await dispatcher.bot.get_me()).get('username')
    await set_default_commands(dispatcher)
    print(f'#    start on @{bot_name}')


async def end(dispatcher) -> None:
    bot_name = dict(await dispatcher.bot.get_me()).get('username')
    print(f'#    end on @{bot_name}')


if __name__ == '__main__':
    executor.start_polling(dispatcher=dp,
                           on_startup=start,
                           on_shutdown=end)
