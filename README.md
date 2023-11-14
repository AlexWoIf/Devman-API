# Devman API bot

![screenshot](https://dvmn.org/media/lessons/cYwOt-Mx3ZY.jpg)

## Назначение

Телеграм бот для проверки статуса работ отправленных на проверку в рамках обучения на сайте  [Devman](https://dvmn.org). В случае изменения статуса проверки, бот присылает об этом уведомление в телеграм.

## Подготовка к запуску, настройка окружения

Для запуска Вам понадобится установленный Python версии 3.10

Скачайте код с GitHub. Затем установите зависимости командой

```sh
pip install -r requirements.txt
```

## Настройка параметров

Параметры можно внести в файл `settings.py` либо создать в той же папке файл `.env` и сохранить параметры в нем. Минимально необходимо задать токен бота полученный у [**BotFather**](https://telegram.me/BotFather)

## Запуск и использование бота

Бот можно исполоьзовать в режиме консольного запуска, либо режиме интерактивного диалога в чате телеграм.

### Режим консольного запуска

Можно запусть бота для получения списка работ командой:

```sh
python review_list.py <Devman API token> <ChatID>
```

Можно запустить наблюдение за изменением статуса проверки работ:

```sh
python polling.py <Devman API token> <ChatID>
```

### Режим диалогового бота

Запустите бота командой:

```sh
python bot.py <Devman API token> <ChatID>
```

После запуска добавьте себе в контакт лист телеграм бота, используя имя указанное при регистрации в **BotFather** и отправьте ему свой Devman API token командой:

`/start <Devman API token>`

После регистрации токена Вы сможете использовать команды `/list` и `/polling` для запуска соответствующих проверок.

Кроме этих команд доступна команда `/help` для получения справки о командах и команда `/forget` для удаления токена и возврата к началу работы с ботом.

## Существующий экземпляр бота

Вы можете ознакомиться с полностью работающим экземпляром бота [**Devman review checker**](https://telegram.me/dvmnAPIbot)

## Цели проекта

Код написан в учебных целях — это урок в рамках курса по Python и веб-разработке на сайте [Devman](https://dvmn.org).
