import requests
import telegram
from settings import LOG_LEVEL, BOT_TOKEN, REVIEWS_URL
import argparse
import logging


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, LOG_LEVEL.upper(), None),
    filename='bot.log',
)


def review_list(dvmn_token: str):
    url = REVIEWS_URL
    headers = {"Authorization": f"Token {dvmn_token}", }
    reviews = {}
    while True:
        res = requests.get(url, headers=headers, )
        res.raise_for_status()
        results = res.json()['results']
        logging.debug(res.json())
        if res.status_code != requests.codes.ok:
            raise Exception('Неизвестный статус ответа.'
                            f'Ответ сервера: {res.json()}')

        for result in results:
            if result['lesson_title'] not in reviews:
                reviews[result['lesson_title']] = {
                    'url': result['lesson_url'],
                    'finished': False
                }
            reviews[result['lesson_title']][result['submitted_at']] = \
                result['is_negative']
            reviews[result['lesson_title']]['finished'] = \
                reviews[result['lesson_title']]['finished'] \
                or not result['is_negative']

        url = res.json()['next']
        if not url:
            break
    return reviews


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
    logging.info(f'Получен вызов с параметрами: {args}')

    text = ''
    reviews = review_list(args.token)
    text += '\nЗавершённые работы:'
    for review in reviews:
        if reviews[review]['finished']:
            text += f'\n\t {review}'
    text += '\nНезавершённые работы:'
    for review in reviews:
        if not reviews[review]['finished']:
            text += f'\n\t {review}'
    bot = telegram.Bot(token=f'{BOT_TOKEN}')
    bot.send_message(text=text, chat_id=chat_id)
