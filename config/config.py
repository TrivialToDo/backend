CSRF_TRUSTED_ORIGINS = ["http://127.0.0.1:5173"]
FRONTEND_URL = ""
wechat_url = "http://wechat:3000"

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'backend',
#         'USER': 'django',
#         'PASSWORD': 'pauJPjkX3lU7hE6xL6kV',
#         'HOST': 'mysql',
#         'PORT': 3306,
#         'OPTIONS': {'charset': 'utf8mb4'},
#     }
# }

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'database' / 'db.sqlite3'
    }
}