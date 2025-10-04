import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

mydb = mysql.connector.connect(
  host=os.getenv("SQL_HOST"),
  user=os.getenv("SQL_USER"),
  password=os.getenv("SQL_PASSWORD"),
  database=os.getenv("SQL_DATABASE")
)
mycursor = mydb.cursor()