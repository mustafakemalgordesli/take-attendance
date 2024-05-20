import os
import cv2
import numpy as np
from keras_facenet import FaceNet

class Preprocess:
    def __init__(self):
        self.model = FaceNet()
        self.face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")        

    def embedding(self,img):
        """ embed face with facenet model """
        img = np.array([img])
        embedding = self.model.embeddings(img)
        return embedding[0]

    def getFace(self, img):
        img = cv2.imread(img)
        face_list = []
        face_coor = []
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        height, width = gray.shape
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        if len(faces)!=0:
            for (x, y, w, h) in faces:
                x1 = x
                y1 = y
                x2 = x+w
                y2 = y+h
                face_image = img[max(0, y1):min(height, y2), max(0, x1):min(width, x2)]  
                face_image = cv2.resize(face_image, (160, 160))  
                face_list.append(face_image)
                face_coor.append((x1,y1,x2,y2))
            return (face_list,face_coor)
        else:
            return (None,None)

    def euclid_distance(self, input_embed, db_embed):
        """ calculate euclidan distance between two embeded vector """
        return np.linalg.norm(db_embed-input_embed)