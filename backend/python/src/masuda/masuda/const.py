from django.conf import settings
import environ


env = environ.Env()
env.read_env(settings.ENV_PATH)

# BASE_PATH = getattr(settings, "BASE_PATH", None)
# print( BASE_PATH)
HATENA = {
    'ID' : env('HATENA_ID'),
    'PASSWORD' : env('HATENA_PASSWORD'),
    'ANOND_URL' : 'https://anond.hatelabo.jp',
    'LOGIN_URL' : 'https://hatelabo.jp/login',
    'BOOKMARK_API_URL' : 'https://bookmark.hatenaapis.com/count/entries',
    'PAGE_SIZE' : 25
}

PROGRESS_WAIT_MINUTES = 20
ABBREVIATION_LENGTH = 100
USE_SPACE_MASUDA = env('USE_SPACE_MASUDA')