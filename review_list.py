import requests
import telegram
from settings import LOG_LEVEL, LOG_FILE, TG_BOT_TOKEN, REVIEWS_URL
import argparse
import logging


def review_list(dvmn_token: str):
    url = REVIEWS_URL
    headers = {"Authorization": f"Token {dvmn_token}", }
    reviews = {}
    while True:
        res = requests.get(url, headers=headers, )
        res.raise_for_status()
        if res.status_code != requests.codes.ok:
            raise Exception('Неизвестный статус ответа.'
                            f'Ответ сервера: {res.json()}')
        res_json = res.json()
        logging.debug(res_json)
        results = res_json['results']
        for result in results:
            lesson = result['lesson_title']
            finished = not result['is_negative']
            if lesson not in reviews:
                reviews[lesson] = finished
            else:
                reviews[lesson] = reviews[lesson] or finished
        url = res_json['next']
        if not url:
            break
    return reviews


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=getattr(logging, LOG_LEVEL.upper(), None),
        filename=LOG_FILE,
    )

    parser = argparse.ArgumentParser(
        description='Для запуска необходио передать ключ Девман API и ID '
                    'чата для отправки полученных ответов')
    parser.add_argument('dvmn_token', type=str,
                        help='Devman API key (token)')
    parser.add_argument('tg_chat_id', type=int,
                        help='User telegram chat id to send final answer')
    args = parser.parse_args()
    tg_chat_id = args.tg_chat_id
    logging.info(f'Получен вызов с параметрами: {args}')

    text_finished = 'Завершённые работы:'
    text_unfinished = 'Незавершённые работы:'
    reviews = review_list(args.dvmn_token)
    for lesson, finished in reviews.items():
        if finished:
            text_finished += f'\n\t {lesson}'
        else:
            text_unfinished += f'\n\t {lesson}'
    tg_bot = telegram.Bot(token=f'{TG_BOT_TOKEN}')
    tg_bot.send_message(
        text=text_finished+'\n'+text_unfinished,
        chat_id=tg_chat_id,
    )
