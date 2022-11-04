from pathlib import Path


BASE_DIR = Path(__file__).parent
AUTH_KEY = BASE_DIR / 'res' / 'acc_key.json'
CONFIG = BASE_DIR / 'res' / 'config.json'

EXCEL_UPDATE_INTERVAL = 300

MENUCODE_DDS_LIST = 0
MENUCODE_PAYMENT_TYPES = 1

MENU_HEIGHT = 10

BUTTONS_CALLBACK_SEP = '$'

DATETIME_FORMAT = '%d.%m.%Y'
