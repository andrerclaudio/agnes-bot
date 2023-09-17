# pylint: disable=missing-module-docstring missing-function-docstring wrong-import-order unused-argument import-error useless-return
# pylint: disable=line-too-long too-many-locals invalid-name unused-import consider-using-f-string wildcard-import unused-wildcard-import

# Build-in modules
import configparser

config = configparser.ConfigParser()
config.read_file(open('/path/to/config-file/agnes-bot/config.ini', encoding='utf-8'))
TOKEN = config['DEFAULT']['token']
CHAT_ID = config['DEFAULT']['error_forward_id']
