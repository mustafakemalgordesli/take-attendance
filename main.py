# pip freeze > requirements.txt
# pip install -r requirements.txt
# uvicorn main:app --reload
# sudo docker build -t my-fastapi-app .
# sudo docker run -d -p 2087:2087 my-fastapi-app
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
# from enum import Enum, IntEnum
import random
import string

from routes.student import student_router
from db import connection

load_dotenv()



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
            imageUrl VARCHAR(255),
            croppedUrl VARCHAR(255)
        ); 
    """
    # CREATE TABLE IF NOT EXISTS students (
    #         id INTEGER NOT NULL PRIMARY KEY,
    #         no VARCHAR(255) NOT NULL,
    #         name VARCHAR(255),
    #         class_id INTEGER NOT NULL,
    #         FOREIGN KEY (class_id)
    #         REFERENCES classes (class_id) 
    #         ON UPDATE CASCADE
    #         ON DELETE CASCADE
    #     ); 
    
    cursor.execute(students_table)
    
    multiple_table = """ 
    CREATE TABLE IF NOT EXISTS multiples (
            id INTEGER NOT NULL PRIMARY KEY,
            imageUrl VARCHAR(255),
            date  TEXT
        ); 
    """
    
    cursor.execute(multiple_table)


app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(student_router)

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
    


