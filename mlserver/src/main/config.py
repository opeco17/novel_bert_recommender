import os

from dotenv import load_dotenv


base_path = os.path.dirname(os.path.abspath(__file__))
abs_path_of = lambda path: os.path.normpath(os.path.join(base_path, path))
load_dotenv(abs_path_of('config.env'))


class Config(object):
    JSON_AS_ASCII = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'you-will-never-guess') 
    LIGHTGBM_MODEL_PATH = abs_path_of('model/lightgbm_model.pkl')
    FEATURE_NAMES_PATH = abs_path_of('model/feature_names.json')
