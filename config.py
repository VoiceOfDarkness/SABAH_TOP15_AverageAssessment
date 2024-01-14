import os

from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient

load_dotenv()

username = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")
token = os.getenv("TELEGRAM_TOKEN")

cluster = MongoClient(
    f"mongodb+srv://{username}:{password}@database.iirfppa.mongodb.net/?retryWrites=true&w=majority"
)

db = cluster["TOP15"]
collection = db["telegrambot"]

