from db import mycursor, mydb  

def create_tables():
    mycursor.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        question TEXT NOT NULL,
        question_type VARCHAR(50) NOT NULL,
        answer TEXT,
        answer_explanation TEXT
    )
    """)
    mydb.commit()

def create_user_details_table():
    mycursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        blood_group VARCHAR(5),
        birth_date varchar(20),
        gender VARCHAR(10)
    )
    """)
    mydb.commit()