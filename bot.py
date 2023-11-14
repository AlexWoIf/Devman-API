import logging
import requests
import subprocess
from telegram import Update
from telegram.ext import (
    Updater,
    CallbackContext,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    Filters,
)
from datetime import datetime
from settings import LOG_LEVEL, BOT_TOKEN, REVIEWS_URL


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, LOG_LEVEL.upper(), None),
    filename='bot.log',
)

STARTED = 1


def check_dvmn_token(dvmn_token: str):
    if not (len(dvmn_token) == 40):
        return False
    headers = {"Authorization": f"Token {dvmn_token}", }
    res = requests.get(REVIEWS_URL, headers=headers, )
    res.raise_for_status()
    if res.status_code == requests.codes.ok:
        return True
    return False


def request_dvmn_token(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='К сожалению, Вы не прислали мне Ваш ключ от Девман API '
             'или он некорректный 🤷‍♂️\n'
             'Без него я не смогу Вам ничем помочь\. Наберите:\n'
             '`/start <API-token>`',
        parse_mode='MarkdownV2',
    )


def start(update: Update, context: CallbackContext):
    if len(context.args):
        token = context.args[0]
        if check_dvmn_token(token):
            help(update, context)
            context.bot.delete_message(
                update.effective_chat.id,
                update.message.message_id,
            )
            context.user_data['token'] = token
        return STARTED
    request_dvmn_token(update, context)


def review_list(update, context):
    token = context.user_data.get('token', None)
    subprocess.Popen([
        'python', 'review_list.py', token, str(update.effective_chat.id),
    ])


def start_polling(update, context):
    token = context.user_data.get('token', None)
    proc = subprocess.Popen([
        'python', 'polling.py', token, str(update.effective_chat.id),
    ])
    context.user_data['polling'] = {
        "started_at": datetime.now(), "proc": proc,
    }


def polling(update, context):
    if len(context.args):
        subcommand = context.args[0]
    else:
        subcommand = 'start'

    polling = context.user_data.get('polling', None)
    if polling:
        stopped = polling["proc"].poll()
        if not stopped==None:
            polling = None

    logging.debug(polling)
    match subcommand:
        case 'start':
            if polling:
                start_time = f'{polling["started_at"]:%Y-%m-%d %H:%M:%S}'
            else:
                start_polling(update, context)
                start_time = f'{datetime.now():%Y-%m-%d %H:%M:%S}'
            text = f'Поллинг запущен: {start_time}'
        case 'status':
            if polling:
                start_time = f'{polling["started_at"]:%Y-%m-%d %H:%M:%S}'
                text = f'Поллинг запущен: {start_time}'
            else:
                text = 'Поллинг не был запущен, либо уже завершен'
        case 'stop':
            if polling:
                polling['proc'].kill()
                text = 'Процессу поллинга отправлен сигнал остановки'
            else:
                text = 'Поллинг не был запущен, либо уже завершен'
        case _:
            text = "Неизвестный операнд команды /polling"
    context.bot.send_message(
        update.effective_chat.id,
        text=text,
    )


def help(update, context):
    context.bot.send_message(
        update.effective_chat.id,
        text='Вы предоставили рабочий ключ от Девман API.\n'
             'Вот какие команды Вам сейчас доступны:\n'
             '/polling [start|status|stop] Запустить опрос Девман API пока не '
             'изменится статус одной из работ на сайте.\n'
             '/list  Получить список Ваших работ с сайта Девман\n'
             '/forget Используйте эту команду, если захотите '
             'использовать другой ключ Девман API.'
    )
    return


def forget(update, context):
    context.user_data.pop(['token'], None)
    context.bot.send_message(
                update.effective_chat.id,
                text='Мы удалили ваш ключ от API Девман\.'
                'Для продолжения работы снова используйте команду:\n'
                '`/start <API-key>`',
                parse_mode='MarkdownV2',
    )
    return ConversationHandler.END


# функция main
if __name__ == '__main__':
    updater = Updater(
                    token=f'{BOT_TOKEN}',
                    use_context=True,
    )
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[
                CommandHandler('start', start),
                MessageHandler(
                    Filters.text & (~Filters.command),
                    request_dvmn_token
                ),
        ],
        states={
            STARTED: [
                CommandHandler('list', review_list),
                CommandHandler('polling', polling),
                MessageHandler(Filters.text & (~Filters.command), help),
            ],
        },
        fallbacks=[CommandHandler('forget', forget), ]
    )
    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    # обработчик нажатия Ctrl+C
    updater.idle()
