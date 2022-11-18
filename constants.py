from pathlib import Path


BASE_DIR = Path(__file__).parent
AUTH_KEY = BASE_DIR / 'res' / 'acc_key.json'
CONFIG = BASE_DIR / 'res' / 'config.json'
USERS = BASE_DIR / 'res' / 'users.json'

EXCEL_UPDATE_INTERVAL = 300

BUTTON_TYPE_CONTROL = 0
BUTTON_TYPE_INFO = 1

MENU_HEIGHT = 10

BUTTONS_CALLBACK_SEP = '$'

DATETIME_FORMAT = '%d.%m.%Y'
