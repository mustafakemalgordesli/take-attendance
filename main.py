# pip freeze > requirements.txt
# pip install -r requirements.txt
# uvicorn main:app --reload

import uuid
from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile
from fastapi.staticfiles import StaticFiles
import os

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
    print(id)
    try: 
        file_path = f"{os.getcwd()}/static/{uuid.uuid4()}{file.filename}"
        print(file_path)
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        return {"message": "File saved successfully"}
    except Exception as e:
        return {"message": e.args}


