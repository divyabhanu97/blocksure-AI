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

app = flask.Flask(__name__)

'''
Authenticate
Authenticates your credentials and creates a client.
'''
subscription_key = "ae2136da0d6143d3a3fa1d083abe21cd"
endpoint = "https://healthcardsk.cognitiveservices.azure.com/"

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
                        if bbox[i][1] != bbox[j][1] and 0 < (bbox[j][1] - bbox[i][1]) <= (img.shape[0])/15 and  0 <= abs(bbox[j][0] - bbox[i][0]) <(img.shape[0])/69:
                            details["Name"] =res[j].text
                            break
                if "/ Father's Name" in res[i].text:
                    for j in range(len(res)):
                        if bbox[i][1] != bbox[j][1] and 0 < (bbox[j][1] - bbox[i][1]) <= (img.shape[0])/15 and  0 <= abs(bbox[j][0] - bbox[i][0]) <(img.shape[0])/69:
                            details["Father_Name"] =res[j].text
                            break
                if "Date of Birth" in res[i].text:
                    for j in range(len(res)):
                        if bbox[i][1] != bbox[j][1] and 0 < (bbox[j][1] - bbox[i][1]) <= (img.shape[0])/15 and  0 <= abs(bbox[j][0] - bbox[i][0]) <(img.shape[0])/69:
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

if __name__ =='__main__':  
    app.run(debug = True,port='5004',host='0.0.0.0') 