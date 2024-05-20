from fastapi import APIRouter
from fastapi import File, UploadFile
import uuid
import os
from preprocess import Preprocess
from datetime import datetime
import sqlite3
import numpy as np
import io
import cv2
from pydantic import BaseModel
from typing import List

def adapt_array(arr):
    """
    http://stackoverflow.com/a/31312102/190597 (SoulNibbler)
    """
    out = io.BytesIO()
    np.save(out, arr)
    out.seek(0)
    return sqlite3.Binary(out.read())

def convert_array(text):
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)

student_router = APIRouter()

from db import connection
 
prep = Preprocess()
      
@student_router.post("/student/uploadfile/{no}")
def create_upload_file(no,  file: UploadFile):
    try:     
        file_name = str(uuid.uuid4()) + file.filename
        file_path = f"{os.getcwd()}/static/{file_name}"
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        face, coor = prep.getFace(f"./static/{file_name}")
        print(face, coor)
        if face != None:
            (x1, y1, x2, y2) =coor[0]
            img = cv2.imread(f"./static/{file_name}")
            cropped_image = img[y1:y2, x1:x2]
            crop_name = f"cropped_{file_name}.jpg"
            cv2.imwrite(f'./static/{crop_name}', cropped_image)
            cursor = connection.cursor()
            sql = """INSERT INTO students (no, imageUrl, croppedUrl)
                VALUES(?, ?, ?);
            """
            cursor.execute(sql, (no, file_name, crop_name))
            connection.commit()
            return {"success": True}
        return {"success": False}
    except Exception as e:
        return {"message": e.args, "success": False}
    
  
class Item(BaseModel):
    id: int
    no: str
    imageUrl: str
    
@student_router.get("/student")
def get_all_student() -> List[Item]:
    try: 
        cursor = connection.cursor()
        sql = """SELECT id, no, imageUrl FROM students"""
        cursor.execute(sql)
        students = cursor.fetchall()
        res = []
        for student in students:
            res.append(Item(
            id=student[0],
            no=student[1],
            imageUrl=student[2]
        ))
        return res
    except Exception as e:
        return []
  
 
    
@student_router.post("/student/multiple")
def create_multiple(file: UploadFile) -> List[Item]:
    try:     
        file_name = str(uuid.uuid4()) + file.filename
        file_path = f"{os.getcwd()}/static/{file_name}"
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        face, coor = prep.getFace(f"./static/{file_name}")
        if face != None:
            time = datetime.now().strftime("%B %d, %Y %I:%M%p")
            cursor = connection.cursor()
            sql = """INSERT INTO multiples (imageUrl, date)
                VALUES(?, ?);
            """
            cursor.execute(sql, (file_name, time))
            connection.commit()
            cursor = connection.cursor()
            sql = """SELECT id, no, imageUrl, croppedUrl FROM students"""
            cursor.execute(sql)
            students = cursor.fetchall()
            print(len(students))
            student_vectors = []
            for student in students:
                img = cv2.imread(f"./static/{student[3]}")
                vector = prep.embedding(img)
                student_vectors.append({
                    "vector": vector,
                    "student": student
                })
            img = cv2.imread(f"./static/{file_name}")
            res = []
            print(len(face))
            for i in range(len(face)):
                print(i)
                (x1, y1, x2, y2) = coor[i]
                cropped_image = img[y1:y2, x1:x2]
                vector = prep.embedding(cropped_image)
                for student in student_vectors:
                    sim = prep.euclid_distance(student["vector"], vector)
                    print(sim, student["student"])
                    if sim > 0 and sim < 1:
                        std = student["student"]
                        print(std)
                        res.append(Item(id=std[0], no=std[1], imageUrl=std[2]))
                        break
            return res
        return []
    except Exception as e:
        print(e)
        return []
    
