from .server import start_server
import os
from config import config

os.environ['OPENAI_API_KEY'] = config['api_key']
os.environ['OPENAI_API_BASE'] = config['base_url']
os.environ['OPENAI_BASE_URL'] = config['base_url']