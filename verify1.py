import cv2
import os
from flask import Flask  
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from azure.cognitiveservices.vision.customvision.training.models import ImageFileCreateBatch, ImageFileCreateEntry, Region
from msrest.authentication import ApiKeyCredentials
import time, uuid

import asyncio
import io
import glob
import sys
import requests
from urllib.parse import urlparse
from io import BytesIO
from PIL import Image, ImageDraw
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face.models import TrainingStatusType, Person

app = Flask(__name__)

# obj detection
ENDPOINT = "https://centralindia.api.cognitive.microsoft.com/"
training_key = "c5a175b7f450425ba8df3e4e22c2ec6b"
prediction_key = "e6ecd0955b824244a3d6483e5c7e1097"
prediction_resource_id = "/subscriptions/0d16ec4a-eebf-44fa-8f1d-7803493f8199/resourceGroups/blockchain-group/providers/Microsoft.CognitiveServices/accounts/custom_vision_sk"

credentials = ApiKeyCredentials(in_headers={"Training-key": training_key})
trainer = CustomVisionTrainingClient(ENDPOINT, credentials)
prediction_credentials = ApiKeyCredentials(in_headers={"Prediction-key": prediction_key})
predictor = CustomVisionPredictionClient(ENDPOINT, prediction_credentials)

publish_iteration_name = "Iteration3"
project_id = "c61fcd17-ee71-4e68-8ea4-a47b73cdc7f2"

#face matching
face_KEY = "471b6c10f789468c8424da69ac81c8dd"

face_ENDPOINT = "https://proof-verification-sk.cognitiveservices.azure.com/"

face_client = FaceClient(face_ENDPOINT, CognitiveServicesCredentials(face_KEY))

cam_url = r"C:\MediaFiles\VID_20220112_173659.mp4"


@app.route('/')
def verify():
    confidence = 0 
    aadhar_card_frame = "none"
    face_frame = "none"
    path = r"data"
    count = 0
    vidcap = cv2.VideoCapture(cam_url)
    success,image = vidcap.read()
    success = True
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    frame_count = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count/fps
    while success:
        vidcap.set(cv2.CAP_PROP_POS_MSEC,(count*1000))    # added this line 
        success,image = vidcap.read()
        image = Image.fromarray(image.astype('uint8'), 'RGB')
        image.save("data/frame"+str(count)+".jpg")     # save frame as JPEG file
        count = count + 0.5
        if(count > (duration-0.5)):
            success = False

    for image_path in os.listdir(path):

        input_path = os.path.join(path, image_path)
        with open(input_path, mode="rb") as test_data:
            results = predictor.detect_image(project_id, publish_iteration_name, test_data)

        for prediction in results.predictions:
            if((prediction.probability * 100) >= 50) and (prediction.probability * 100) >= confidence :
                confidence = prediction.probability * 100
                aadhar_card_frame = input_path
                break
                
        if aadhar_card_frame == "none":
            img = cv2.imread(input_path)
            gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            frame_gray = cv2.equalizeHist(gray_img)

            face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_alt.xml")
            eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')

            faces = face_cascade.detectMultiScale(frame_gray, 1.3, 3)
            if len(faces) == 1:
                for (x,y,w,h) in faces:
                    roi_gray = frame_gray[y:y+h, x:x+w]
                    roi_color = img[y:y+h, x:x+w]
                    eyes = eye_cascade.detectMultiScale(roi_gray)
                    if (len(eyes) == 2):
                        face_frame = input_path
        else:
            break

    if aadhar_card_frame != "none" and face_frame != "none":
        
        image = open(face_frame, 'rb')
        detected_faces1 = face_client.face.detect_with_stream(image, detection_model='detection_03')
        source_image1_id = detected_faces1[0].face_id
        
        image1 = open(aadhar_card_frame, 'rb')
        detected_faces2 = face_client.face.detect_with_stream(image1, detection_model='detection_03')
        source_image2_id = detected_faces2[0].face_id
        
        verify_result_same = face_client.face.verify_face_to_face(source_image1_id, source_image2_id)
        if verify_result_same.confidence > 0.25:
            return "VERIFIED!";
            print("ver")
        else:
            return "MISMATCH";
    else:
        return "No aadhar card found!";

    if face_frame == "none":
        return "No face found"

if __name__ =='__main__':  
    # verify()
    app.run(debug = True)  
    # verify()
