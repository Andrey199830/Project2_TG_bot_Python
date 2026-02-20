import os
from dotenv import load_dotenv

load_dotenv()

settings = {
    "TELEGRAM_TOKEN": os.getenv("8036165061:AAGhF5UWjeDepiD-u7iGveTUqUIx5kSSTGY"),
    "DB_STRING": os.getenv("DB_STRING"),
}
