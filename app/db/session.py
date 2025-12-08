import mysql.connector
from app.core.config import settings

mydb = mysql.connector.connect(
  host=settings.SQL_HOST,
  user=settings.SQL_USER,
  password=settings.SQL_PASSWORD,
  database=settings.SQL_DATABASE
)
mycursor = mydb.cursor()