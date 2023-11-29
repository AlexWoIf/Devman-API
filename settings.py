from environs import Env


env = Env()
env.read_env()

LOG_LEVEL = env.str('LOG_LEVEL', 'INFO')
LOG_FILE = env.str('LOG_FILE', 'bot.log')

TG_BOT_TOKEN = env.str('TG_BOT_TOKEN')
TG_API = env.str('TG_API', "https://api.telegram.org/bot")

REVIEWS_URL = 'https://dvmn.org/api/user_reviews/'
POLLING_URL = 'https://dvmn.org/api/long_polling/'
