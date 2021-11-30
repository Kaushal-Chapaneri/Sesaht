"""
filename : db_operations.py

This script holds the code of storing and fetching data in mongo DB.
"""

import pymongo

from utils import load_config

config = load_config()

client = pymongo.MongoClient(config["HOST"])

mongo_db_name = config["DB_NAME"]
db = client[mongo_db_name]
corpus_result = db["corpus_result"]


def store_in_db(data):
    """
    Function to store data in DB
    
    Args:
		  data: dict of results generated
    """
    x = corpus_result.insert_one(data)

def fetch_from_db():
    """
    Function to fetch all record from DB
    """
    return corpus_result.find({})

