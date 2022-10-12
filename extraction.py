import cv2
import numpy as np
import matplotlib.pylab as plt
import math
from difflib import SequenceMatcher
import flask
from flask import request, jsonify
from flask_cors import CORS

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

from array import array
import os
from PIL import Image
import sys
import time
import re
from convert_base64 import ConvertoImage
import requests
import cv2
import os
from flask import Flask  
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from azure.cognitiveservices.vision.customvision.training.models import ImageFileCreateBatch, ImageFileCreateEntry, Region
from msrest.authentication import ApiKeyCredentials
import time, uuid
from datetime import datetime

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
from flask import request, jsonify
from flask_cors import CORS
from convert_base64 import ConvertoVideo
from dateutil import parser


app = flask.Flask(__name__)
CORS(app)

'''
Authenticate
Authenticates your credentials and creates a client.
'''
subscription_key = "ae2136da0d6143d3a3fa1d083abe21cd"
endpoint = "https://healthcardsk.cognitiveservices.azure.com/"

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

computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

@app.route('/pan', methods=['POST'])
def pan_extraction():
    content = request.json
    ConvertoImage(content['base64data'],'image1')
    read_image_path = "./image1.png"
    read_image = open(read_image_path, "rb")

    read_response = computervision_client.read_in_stream(read_image,  raw=True)

    res = []
    bbox = []
    # Get the operation location (URL with an ID at the end) from the response
    read_operation_location = read_response.headers["Operation-Location"]
    # Grab the ID from the URL
    operation_id = read_operation_location.split("/")[-1]

    # Call the "GET" API and wait for it to retrieve the results 
    while True:
        read_result = computervision_client.get_read_result(operation_id)
        if read_result.status not in ['notStarted', 'running']:
            break
        time.sleep(1)

    # Print the detected text, line by line
    if read_result.status == OperationStatusCodes.succeeded:
        for text_result in read_result.analyze_result.read_results:
            for line in text_result.lines:
                bbox.append(line.bounding_box)
                res.append(line)
    
    details = {
        "Name" : "",
        "Father_Name" : "",
        "Date_Of_Birth" : "",
        "Permanent_Account_Number" : ""
    }

    acc_bb = 0
    img = plt.imread(read_image_path)
    for i in range(len(res)):
        if "Permanent Account Number" in res[i].text:
            acc_bb = bbox[i]
            details["Permanent_Account_Number"] = res[i+1].text
            break
    if acc_bb !=0 :
        if acc_bb[1] > img.shape[0]/2:
            details["Name"] = res[3].text
            details["Father_Name"] = res[4].text
            details["Date_Of_Birth"] = res[5].text
            details["Permanent_Account_Number"] = res[7].text
        else:
            for i in range(len(res)):
                if "/ Name" in res[i].text:
                    for j in range(len(res)):
                        if bbox[i][1] != bbox[j][1] and 0 < (bbox[j][1] - bbox[i][1]) <= (img.shape[0])/12 and  0 <= abs(bbox[j][0] - bbox[i][0]) <(img.shape[1])/50:
                            details["Name"] =res[j].text
                            break
                if "/ Father's Name" in res[i].text:
                    for j in range(len(res)):
                        if bbox[i][1] != bbox[j][1] and 0 < (bbox[j][1] - bbox[i][1]) <= (img.shape[0])/12 and  0 <= abs(bbox[j][0] - bbox[i][0]) <(img.shape[1])/50:
                            details["Father_Name"] =res[j].text
                            break
                if "Date of Birth" in res[i].text:
                    for j in range(len(res)):
                        if bbox[i][1] != bbox[j][1] and 0 < (bbox[j][1] - bbox[i][1]) <= (img.shape[0])/12 and  0 <= abs(bbox[j][0] - bbox[i][0]) <(img.shape[1])/50:
                            details["Date_Of_Birth"] =res[j].text
                            break

    return details

@app.route('/aadhar', methods=['POST'])
def aadhar_extraction():
    content = request.json
    ConvertoImage(content['base64data'],'image2')
    read_image_path = "./image2.png"
    read_image = open(read_image_path, "rb")

    read_response = computervision_client.read_in_stream(read_image,  raw=True)

    result = []
    bbox = []
    text = ""
    # Get the operation location (URL with an ID at the end) from the response
    read_operation_location = read_response.headers["Operation-Location"]
    # Grab the ID from the URL
    operation_id = read_operation_location.split("/")[-1]

    # Call the "GET" API and wait for it to retrieve the results 
    while True:
        read_result = computervision_client.get_read_result(operation_id)
        if read_result.status not in ['notStarted', 'running']:
            break
        time.sleep(1)

    # Print the detected text, line by line
    if read_result.status == OperationStatusCodes.succeeded:
        for text_result in read_result.analyze_result.read_results:
            for line in text_result.lines:
                text += line.text
                text +=" "
                bbox.append(line.bounding_box)
                result.append(line)
    aadhar_details = {
        "Name" : "",
        "Date_Of_Birth" : "",
        "Gender" : "",
        "Aadhar_Number" : ""
    }

    if "female" in text.lower():
        sex = "female"
    else:
        sex = "Male"
        
    res = text.split()
    aadhar_number=''
    allow = False
    for word in res:
        if "male" in word.lower():
            allow = True
        if allow:
            if len(word) == 4 and word.isdigit():
                aadhar_number=aadhar_number  + word + ' '
    if len(aadhar_number)>=14:
                aadhar_number = aadhar_number
    else:
        aadhar_number = ""
    aadhar_details["Name"] =result[1].text    
    aadhar_details["Date_Of_Birth"] = str(re.findall(r"[\d]{1,4}[/-][\d]{1,4}[/-][\d]{1,4}", text)).replace("]", "").replace("[","").replace("'", "")
    aadhar_details["Gender"] = sex
    aadhar_details["Aadhar_Number"] = aadhar_number
    return aadhar_details

@app.route('/vkyc',methods=['POST'])
def verify():
    content = request.json
    # print(content)
    ConvertoVideo(content['base64data'],'image1')
    cam_url = r"image1.mp4"
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
            return {"status":"VERIFIED!"}
            print("ver")
        else:
            return {"status":"MISMATCH"}
    else:
        return {"status":"No aadhar card found!"}

def data_extraction(read_image):
    read_response = computervision_client.read_in_stream(read_image,  raw=True)

    result = []
    bbox = []
    text = ""
    # Get the operation location (URL with an ID at the end) from the response
    read_operation_location = read_response.headers["Operation-Location"]
    # Grab the ID from the URL
    operation_id = read_operation_location.split("/")[-1]

    # Call the "GET" API and wait for it to retrieve the results 
    while True:
        read_result = computervision_client.get_read_result(operation_id)
        if read_result.status not in ['notStarted', 'running']:
            break
        time.sleep(1)

    # Print the detected text, line by line
    if read_result.status == OperationStatusCodes.succeeded:
        for text_result in read_result.analyze_result.read_results:
            for line in text_result.lines:
                text += line.text
                text +=" "
                bbox.append(line.bounding_box)
                result.append(line)
    return result, text

@app.route('/drivinglicence', methods=['POST'])
def licence_extraction():
    content = request.json
    ConvertoImage(content['frontbase64data'],'image2')
    ConvertoImage(content['backbase64data'],'image3')
    read_image_path1 = "./image2.png"
    read_image_path2 = "./image3.png"
    read_image1 = open(read_image_path1, "rb")
    read_image2 = open(read_image_path2, "rb")
    frontresult=data_extraction(read_image1)
    backresult=data_extraction(read_image2)
    print(frontresult[1],backresult[1])
    for index, item in enumerate(frontresult[0], start=0):   # Python indexes start at zero
        print(index,frontresult[0][index].text)
    for index, item in enumerate(backresult[0], start=0):   # Python indexes start at zero
        print(index,backresult[0][index].text)
    driving_licence_details = {
        "Name" : "",
        "Date_Of_Birth" : "",
        "Reference_Number" : "",
        "Date of Issue": "",
        "Validity" : "",
        "Non Transport": ""
    }

    driving_licence_details["Name"] =frontresult[0][3].text 
    
    driving_licence_details["Reference_Number"] =frontresult[0][2].text
    if(re.search(r'\d{2}-\d{2}-\d{4}', backresult[0][13].text)):
        match_str = re.search(r'\d{2}-\d{2}-\d{4}', backresult[0][13].text)
        res = datetime.strptime(match_str.group(), '%d-%m-%Y').date()
        driving_licence_details["Date of Issue"] = str(res)
        driving_licence_details["Date_Of_Birth"] = backresult[0][15].text
    else:
        driving_licence_details["Date of Issue"] = backresult[0][14].text
        driving_licence_details["Date_Of_Birth"] = backresult[0][16].text
    driving_licence_details["Validity"] = backresult[0][4].text
    driving_licence_details["Non Transport"] = backresult[0][1].text + " " + backresult[0][2].text
    print(driving_licence_details)
    return driving_licence_details

@app.route('/',methods=['GET'])
def hello():
    return "hello world"
if __name__ =='__main__': 
    # licence_extraction() 
    app.run(debug = True,port='5006',host='0.0.0.0') 