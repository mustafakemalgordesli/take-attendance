# pip freeze > requirements.txt
# pip install -r requirements.txt
# uvicorn main:app --reload
# sudo docker build -t my-fastapi-app .
# sudo docker run -d -p 2087:2087 my-fastapi-app
from dotenv import load_dotenv
import uuid
from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile
from fastapi.staticfiles import StaticFiles
import os
from pydantic import BaseModel, EmailStr
# from enum import Enum, IntEnum
import sqlite3
import random
import string

load_dotenv()

connection = sqlite3.connect('take.db') 

# from db import User, session

app = FastAPI()

origins = ["*"]
# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    # cursor object
    cursor = connection.cursor()
    # Creating table
    class_table = """
    CREATE TABLE IF NOT EXISTS classes (
            id INTEGER NOT NULL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            code VARCHAR(12) NOT NULL UNIQUE
    ); 
    """
    cursor.execute(class_table)
    
    students_table = """ 
    CREATE TABLE IF NOT EXISTS students (
            id INTEGER NOT NULL PRIMARY KEY,
            no VARCHAR(255) NOT NULL,
            name VARCHAR(255),
            class_id INTEGER NOT NULL,
            FOREIGN KEY (class_id)
            REFERENCES classes (class_id) 
            ON UPDATE CASCADE
            ON DELETE CASCADE
        ); 
    """
    cursor.execute(students_table)


app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return {"Hello": "World"}


def generate_unique_code(length):
    characters = string.ascii_uppercase + string.digits
    code = ''.join(random.choices(characters, k=length))
    return code

class ClassModel(BaseModel):
    name: str

@app.post("/class")
async def add_class(new_class: ClassModel):
    try:
        cursor = connection.cursor()

        code = None
        
        while code is None:
            code = generate_unique_code(12)
            
            statement = '''SELECT * FROM classes WHERE code = ?'''
  
            cursor.execute(statement, (code,)) 

            output = cursor.fetchone() 
            
            if output is not None:
                code = None
        
        sql = """INSERT INTO classes (name, code)
            VALUES(?, ?);
        """
        cursor = connection.cursor()
        cursor.execute(sql, (new_class.name, code,))
        connection.commit()
        return { "success": True }
    except Exception as e:
        return {"message": e.args, "success": False}, 401
    
class StudentModel(BaseModel):
    no: str
    class_id: int
    name: str | None = None
     
@app.post("/student")
async def add_student(student: StudentModel):
    try:
        cursor = connection.cursor()
        sql = """INSERT INTO students (name)
            VALUES('?');
        """
        cursor = connection.cursor()
        res = cursor.execute(sql, student.no)
        print(res)
        return { "success": True }
    except Exception as e:
        return {"message": e.args, "success": False}

@app.post("/uploadfile/{id}")
async def create_upload_file(id, file: UploadFile):
    try: 
        file_name = str(uuid.uuid4()) + file.filename
        file_path = f"{os.getcwd()}/static/{file_name}"
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        return {"path": file_name, "success": True}
    except Exception as e:
        return {"message": e.args, "success": False}
    
    


# class RoleEnum(str, Enum):
#     student = 'student'
#     teacher = 'teacher'
# class RegisterModel(BaseModel):
#     email: EmailStr
#     password: str
#     role: RoleEnum

# @app.post("/auth/register")
# async def register(model: RegisterModel):
#     try:
#         print(model)
#         return { "success": True }
#     except Exception as e:
#         return {"message": e.args, "success": False}
    


