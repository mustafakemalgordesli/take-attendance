# pip freeze > requirements.txt
# pip install -r requirements.txt
# uvicorn main:app --reload
from dotenv import load_dotenv
import uuid
from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile
from fastapi.staticfiles import StaticFiles
import os
from pydantic import BaseModel, EmailStr
from enum import Enum, IntEnum

load_dotenv()

from db import User, session

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
# # Including routers
# app.include_router(userview.router)
# # Start up event
# @app.on_event("startup")
# async def startup():
#     await database_instance.connect()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/uploadfile/{id}")
async def create_upload_file(id, file: UploadFile):
    try: 
        file_path = f"{os.getcwd()}/static/{uuid.uuid4()}{file.filename}"
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        return {"path": file_path, "success": True}
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
    


