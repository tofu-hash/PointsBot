from handlers.init import *


async def complete_task_handler(msg: CallbackQuery, state: FSMContext):
    await msg.answer()
    await state.finish()

    task_id = int(msg.data.split('complete_task_')[1])
    task_description = execute(
        ('SELECT description FROM tasks '
         'WHERE id=%s') % task_id,
        fetchone=True, commit=False
    )[0]

    execute(
        ('UPDATE tasks SET completed=1, completed_in=%s '
         'WHERE id=%s') % (now_unix_time(), task_id)
    )

    today_points = execute(
        ('SELECT COUNT(*) FROM tasks '
         'WHERE created>=%s AND user_id=%s AND completed=1') %
        (int(now_unix_time() - (24 * 60 * 60)),
         msg.from_user.id),
        fetchone=True, commit=False
    )[0]

    answer = ('🥳 Ты завершил задачу и получил *1* поинт.\n\n'
              '💬 Задача: _«%s»_\n\n'
              '🎯 Твои поинты за последние 24 часа: *%s*') % \
             (task_description, today_points)
    if not msg.message.caption:
        await msg.message.edit_text(text=answer, parse_mode='markdown')
    else:
        await msg.message.edit_caption(caption=answer, parse_mode='markdown')


async def delete_task_handler(msg: CallbackQuery):
    await msg.answer()

    task_id = int(msg.data.split('delete_task_')[1])

    task_description, task_completed = execute(
        ('SELECT description, completed FROM tasks '
         'WHERE id=%s') % task_id,
        fetchone=True, commit=False
    )

    today_points = execute(
        ('SELECT COUNT(*) FROM tasks '
         'WHERE created>=%s AND user_id=%s AND completed=1') %
        (int(now_unix_time() - (24 * 60 * 60)),
         msg.from_user.id),
        fetchone=True, commit=False
    )[0]

    execute(
        ('DELETE FROM tasks '
         'WHERE id=%s') % task_id
    )

    answer = ('🗑 Задача _«%s»_ была удалена.\n\n'
              '🎯 Снято поинтов: %s\n\n'
              '🎯 Твои поинты за последние 24 часа: *%s*') % \
             (task_description, task_completed, today_points)
    await msg.message.edit_text(text=answer, parse_mode='markdown')


async def cancel_handler(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.finish()
    if cq.message.text:
        first_line = cq.message.text.split('\n')[0]
        answer = '{}\n\n❌ Действие отменено'.format(first_line)
        await cq.message.edit_text(text=answer)
    else:
        first_line = cq.message.caption.split('\n')[0]
        answer = '{}\n\n❌ Действие отменено'.format(first_line)
        await cq.message.edit_caption(caption=answer)
