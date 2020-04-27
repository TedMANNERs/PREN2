import configparser
import os

script_dir = os.path.dirname(__file__)
rel_path = "config.ini"
abs_file_path = os.path.join(script_dir, rel_path)
parser = configparser.ConfigParser()

if not parser.read(abs_file_path):
    raise Exception(f"Reading from File: 'config.ini' seems to return and empty object")

else:
    parser.read(abs_file_path)
