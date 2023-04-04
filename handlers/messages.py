import aiogram.utils.exceptions
from utils.image_processing import make_points_count_img

from handlers.init import *


async def delete_last_messages(msg: Message, count: int = 3):
    """Удаляет последние N сообщений до команды."""

    for i in range(0, count):
        try:
            await bot.delete_message(chat_id=msg.from_user.id,
                                     message_id=msg.message_id - i)
        except aiogram.utils.exceptions.MessageToDeleteNotFound:
            pass


async def start_cmd_handler(msg: Message, state: FSMContext):
    await state.finish()

    # Create user
    execute(
        ('INSERT OR IGNORE INTO users '
         '(user_id, username, created) '
         'VALUES (%s, "%s", %s);') %
        (msg.from_user.id, msg.from_user.username,
         now_unix_time())
    )

    answer = ('Привет, *%s*!👋\n\n'
              'Я - бот для записи ежедневных задач '
              'и получения очков (*поинтов*) за них.\n\n'
              '🤔 Зачем это нужно?\n'
              'Всё просто - жить проще, '
              'разбивая задачи на более мелкие.\n\n'
              '🎯 Есть два типа поинтов:\n'
              '*• Общие* - это поинты за всё время использования бота.\n'
              '*• Ежедневные* - это поинты, обнуляемые каждый день.\n\n'
              '🚑 */help* - список команд') % msg.from_user.first_name

    await msg.answer_sticker(sticker='CAACAgIAAxkBAAMKZCqF8NxyEdlQYjNX0uQ-kMCKBRsAAvINAAK7fWBIH8H7_ft7nyovBA')
    await msg.answer(text=answer, parse_mode='markdown')


async def help_cmd_handler(msg: Message, state: FSMContext):
    await delete_last_messages(msg)
    await state.finish()

    answer = ('🚑 Помощь по командам бота.\n\n'
              '*/task* - добавить задачу. Вы '
              'можете прикрепить фото к тексту, '
              'и оно добавиться к задаче. Также, '
              'вы можете просто отправить текст и фото '
              'в чат.\n\n'
              '*/tasks* - Просмотреть все незавершённые задачи.\n\n'
              '*/last_task* - Просмотреть последнюю незавершённую '
              'задачу.\n\n'
              '*/points* - Просмотреть статистику поинтов.\n\n'
              '*/all_tasks* - Просмотреть все ваши задачи за всё время.')
    await msg.answer_sticker(sticker='CAACAgIAAxkBAAMaZCqHb_yZ420qmb6L4K7b-dCpWYAAAicjAAIyIHlKbAUWKHL95xwvBA')
    await msg.answer(answer, parse_mode='markdown')


def make_complete_task_reply_markup(user_id: int, task_id: int = None):
    if task_id is None:
        task_id = 'ORDER BY id DESC LIMIT 1;'
    else:
        task_id = 'AND id=%s;' % task_id

    last_task_id = execute(
        ('SELECT id FROM tasks '
         'WHERE user_id=%s AND completed=0 %s') % (user_id, task_id),
        fetchone=True
    )[0]

    reply_markup = InlineKeyboardMarkup()
    reply_markup.add(InlineKeyboardButton(text='✅ Я выполнил',
                                          callback_data='complete_task_%s' % last_task_id))
    reply_markup.add(InlineKeyboardButton(text='🗑 Удалить',
                                          callback_data='delete_task_%s' % last_task_id))
    return reply_markup


async def create_task_cmd_handler(msg: Message, state: FSMContext):
    await TasksStatesGroup.set_task_description.set()

    answer = ('Отправь мне текст задачи '
              '(до 50 символов) 🧐')
    await msg.answer_sticker(sticker='CAACAgIAAxkBAAPYZCqR6zZzKVUz33Sf5pgBrblebycAAmcgAAKapIFK0HYDHhsRZbQvBA')
    await msg.answer(text=answer, reply_markup=cancel_reply_markup)


async def set_task_description_handler(msg: Message, state: FSMContext):
    await delete_last_messages(msg)

    msg_text = msg.text if msg.text else msg.caption
    if len(msg_text) <= 50:
        photo_id = '"%s"' % msg.photo[-1].file_id if msg.photo else 'NULL'
        execute(
            ('INSERT INTO tasks '
             '(user_id, description, created, photo_id) '
             'VALUES (%s, "%s", %s, %s);') %
            (msg.from_user.id, msg.html_text.replace("'", '"'),
             now_unix_time(), photo_id)
        )

        answer = ('🥳 <b>Задача добавлена</b>\n\n'
                  '💬 Вот её текст: <b>%s</b>\n\n') % msg.html_text.replace("'", '"')

        await msg.answer_sticker(sticker='CAACAgIAAxkBAAMZZCqHXXVGPzg4eHzg__GbcJ8OkzYAAvwdAAJ9b4BKNkCjrR9OPS4vBA')
        if msg.photo:
            await msg.answer_photo(photo=msg.photo[-1].file_id,
                                   caption=answer, parse_mode='HTML',
                                   reply_markup=make_complete_task_reply_markup(msg.from_user.id))
        else:
            await msg.answer(text=answer, parse_mode='HTML',
                             reply_markup=make_complete_task_reply_markup(msg.from_user.id))
        await state.finish()
    else:
        answer = ('⚠ Слишком длинный текст задачи.\n'
                  'Постарайтесь сократить его, или '
                  'разбить на более мелкие задачи.')
        await msg.answer_sticker(sticker='CAACAgIAAxkBAAMZZCqHXXVGPzg4eHzg__GbcJ8OkzYAAvwdAAJ9b4BKNkCjrR9OPS4vBA')
        await msg.answer(text=answer)


async def points_cmd_handler(msg: Message):
    await delete_last_messages(msg)

    today_points = execute(
        ('SELECT COUNT(*) FROM tasks '
         'WHERE created>=%s AND user_id=%s AND completed=1') %
        (int(now_unix_time() - (24 * 60 * 60)),
         msg.from_user.id),
        fetchone=True, commit=False
    )[0]

    all_points = execute(
        ('SELECT COUNT(*) FROM tasks '
         'WHERE user_id=%s AND completed=1') % msg.from_user.id,
        fetchone=True
    )[0]

    make_points_count_img(all_points)
    img = open('./source/service/result.jpg', 'rb')

    answer = ('📊 Вот твои поинты:\n\n'
              '🎯 Общие: *%s*\n'
              '🎯 За посл. 24ч: *%s*\n\n') % (all_points, today_points)
    await msg.answer_sticker(sticker='CAACAgIAAxkBAANjZCqMNIQ8xtCzPTUtGVYfb9Qu9dcAAkUgAAKkVHlKVlptX9K1_6svBA')
    await msg.answer_photo(photo=img, caption=answer, parse_mode='markdown')


async def last_task_cmd_handler(msg: Message):
    await delete_last_messages(msg)
    task = execute(
        ('SELECT description, photo_id, created FROM tasks '
         'WHERE user_id=%s AND completed=0 ORDER BY id DESC LIMIT 1;') % msg.from_user.id,
        fetchone=True, commit=False
    )
    if task:
        description, photo_id, created = task
        answer = ('🎯 Последняя задача\n\n'
                  '📅 <b>%s</b>\n\n'
                  '💬 <b>%s</b>') % (get_datetime(created), description)

        await msg.answer_sticker(sticker='CAACAgIAAxkBAAMZZCqHXXVGPzg4eHzg__GbcJ8OkzYAAvwdAAJ9b4BKNkCjrR9OPS4vBA')
        if photo_id:
            await msg.answer_photo(photo=photo_id,
                                   caption=answer, parse_mode='HTML',
                                   reply_markup=make_complete_task_reply_markup(msg.from_user.id))
        else:
            await msg.answer(text=answer, parse_mode='HTML',
                             reply_markup=make_complete_task_reply_markup(msg.from_user.id))
    else:
        answer = ('🎯 У тебя ещё не было '
                  'задач.\n\n'
                  '*/task* - создать задачу')
        await msg.answer_sticker(sticker='CAACAgIAAxkBAAPZZCqSFyGl0u-fVKfTdusdxYJXSkwAAk4eAAJDXYFKd2hQtAuylkMvBA')
        await msg.answer(text=answer, parse_mode='markdown')


async def view_task_cmd_handler(msg: Message):
    await delete_last_messages(msg)
    task_id = int(msg.text.split('/task', maxsplit=1)[1])
    task = execute(
        ('SELECT description, photo_id, created FROM tasks '
         'WHERE user_id=%s AND id=%s;') %
        (msg.from_user.id, task_id),
        fetchone=True, commit=False
    )
    if task:
        description, photo_id, created = task
        answer = ('🎯 Задача\n\n'
                  '📅 <b>%s</b>\n\n'
                  '💬 <b>%s</b>') % (get_datetime(created), description)

        await msg.answer_sticker(sticker='CAACAgIAAxkBAAMZZCqHXXVGPzg4eHzg__GbcJ8OkzYAAvwdAAJ9b4BKNkCjrR9OPS4vBA')
        if photo_id:
            try:
                await msg.answer_photo(photo=photo_id,
                                       caption=answer, parse_mode='HTML',
                                       reply_markup=make_complete_task_reply_markup(msg.from_user.id,
                                                                                    task_id))
            except aiogram.utils.exceptions.BadRequest:
                await msg.answer(text=answer + '\n\n⚠ Ошибка загрузки фото', parse_mode='HTML',
                                 reply_markup=make_complete_task_reply_markup(msg.from_user.id,
                                                                              task_id))
        else:
            await msg.answer(text=answer, parse_mode='HTML',
                             reply_markup=make_complete_task_reply_markup(msg.from_user.id,
                                                                          task_id))
    else:
        answer = ('🎯 Задачи не существует.\n\n'
                  '*/task* - создать задачу')
        await msg.answer_sticker(sticker='CAACAgIAAxkBAAPZZCqSFyGl0u-fVKfTdusdxYJXSkwAAk4eAAJDXYFKd2hQtAuylkMvBA')
        await msg.answer(text=answer, parse_mode='markdown')


async def tasks_cmd_handler(msg: Message):
    await delete_last_messages(msg)

    tasks = execute(
        ('SELECT id, description, photo_id, created '
         'FROM tasks '
         'WHERE user_id=%s AND completed=0') % msg.from_user.id,
        fetchall=True
    )
    if tasks:
        answer = '📊 Вот твои незавершённые задачи:\n\n'
        for task in tasks:
            photo = '\n├ 🖼 *Прикреплено фото*' if task[2] else ''
            answer += ('🎯 *%s* %s\n'
                       '├ 📅 %s\n'
                       '└ 👨‍💻 /task%s - управлять задачей\n\n') % \
                      (task[1], photo, get_datetime(task[3]), task[0])
    else:
        answer = ('🎯 У тебя ещё не было '
                  'задач.\n\n'
                  '*/task* - создать задачу')
    await msg.answer_sticker(sticker='CAACAgIAAxkBAAPaZCqSNnyA798hs29WSek7vnUbp4AAAtMeAAKO4IFKD58PHMtIpDwvBA')
    await msg.answer(text=answer, parse_mode='markdown')


async def get_all_tasks_cmd_handler(msg: Message):
    answer = '😴 Генерирую файл с вашими задачами'
    await msg.answer(text=answer)

    f_path = 'source/service/all_tasks.txt'

    with open(f_path, 'w') as f:
        lines = []
        tasks = execute(
            ('SELECT description, created, completed '
             'FROM tasks WHERE user_id=%s') % msg.from_user.id,
            fetchall=True
        )
        for task in tasks:
            completed = '├ ✅ Завершено\n' if task[2] == 1 else '├ ❌ Не завершено\n'
            line = ('🎯 %s\n%s'
                    '└ 📅%s\n\n') % \
                   (task[0], completed,
                    get_datetime(task[1]))

            lines.append(line)

        f.writelines(lines)

    f = open(f_path, 'rb')
    answer = ('💾 Вот все ваши задачи '
              'за всё время '
              'использования бота.')
    await msg.answer_document(document=f, caption=answer, parse_mode='markdown')


async def get_sticker_id_handler(msg: Message):
    await msg.answer_sticker(sticker=msg.sticker.file_id)
    print(msg.sticker.file_id)
