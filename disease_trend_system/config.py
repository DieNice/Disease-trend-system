import os

from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
hostname_db = os.getenv("HOSTNAME_DB")
username_db = os.getenv("USERNAME_DB")
password_db = os.getenv("PASSWORD_DB")
port = 3306
name_db = os.getenv("NAME_DB")

admin_name = os.getenv("ADMIN_NAME")
admin_username = os.getenv("ADMIN_USERNAME")
admin_password = os.getenv("ADMIN_PASSWORD")
admin_email = os.getenv("ADMIN_EMAIL")
