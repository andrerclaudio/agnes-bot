# Build-in modules
import configparser

config = configparser.ConfigParser()
config.read_file(open('config.ini'))
TOKEN = config['DEFAULT']['token']
CHAT_ID = config['DEFAULT']['error_forward_id']