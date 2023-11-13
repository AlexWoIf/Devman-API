import logging
import requests
from time import sleep
import telegram
from settings import LOG_LEVEL, BOT_TOKEN, POLLING_URL
import argparse


CONNECTION_ERROR_DELAY = 90
MAX_TIMEOUT_COUNT = 3

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, LOG_LEVEL.upper(), None),
    filename='bot.log',
)


def devman_polling(token):
    params = {}
    headers = {"Authorization": f"Token {token}", }
    timeout_count = 0
    while True:
        logging.info(f"Запрашиваем наличие изменений. {params}")
        try:
            res = requests.get(
                POLLING_URL,
                headers=headers,
                params=params, )
            res.raise_for_status()
        except requests.exceptions.ReadTimeout:
            timeout_count += 1
            logging.warning(f"Сервер не ответил {timeout_count} раз подряд")
            continue
        except requests.exceptions.ConnectionError:
            logging.warning("CONNECTION ERROR. Делаем паузу "
                            f"{CONNECTION_ERROR_DELAY} секунд")
            sleep(CONNECTION_ERROR_DELAY)
            continue

        timeout_count = 0
        logging.debug(res.json())

        match res.json()['status']:
            case 'timeout':
                params['timestamp'] = res.json()['timestamp_to_request']
                continue
            case 'found':
                logging.info('Получен ответ об изменении статуса', res.json())
                return res.json()
            case _:
                raise Exception('Неизвестный статус ответа.'
                                f'Ответ сервера: {res.json()}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Для запуска необходио передать ключ Девман API и ID '
                    'чата для отправки полученных ответов')
    parser.add_argument('token', type=str,
                        help='Devman API key (token)')
    parser.add_argument('chat_id', type=int,
                        help='User telegram chat id to send final answer')
    args = parser.parse_args()
    chat_id = args.chat_id

    changes = devman_polling(args.token)

    message = "Статус некоторых проверок изменился! " \
              "Детали из ответа сервера:\n"
    for attempt in changes["new_attempts"]:
        message += f'Название урока: {attempt["lesson_title"]}\n'
        message += f'Ссылка на урок: {attempt["lesson_url"]}\n'
        message += f'Задание {"не" if attempt["is_negative"] else ""} принято'

    bot = telegram.Bot(token=f'{BOT_TOKEN}')
    bot.send_message(text=message, chat_id=chat_id)
