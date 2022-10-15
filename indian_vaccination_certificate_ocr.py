import cv2
import numpy as np
import matplotlib.pylab as plt
import math
from difflib import SequenceMatcher

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

from array import array
import os
from PIL import Image
import sys
import time
import flask

subscription_key = "ae2136da0d6143d3a3fa1d083abe21cd"
endpoint = "https://healthcardsk.cognitiveservices.azure.com/"

computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

app = flask.Flask(__name__)

@app.route('/vaccine', methods=['POST'])
def certificate_data_extraction():

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

    img = plt.imread(read_image_path)
    def findtext(tag):
        for i in range(len(res)):
            if tag in res[i].text:
                bb = bbox[i]
                for j in range(len(res)):
                    if bb[0] != bbox[j][0] and 0 <= abs(bb[1] - bbox[j][1]) < img.shape[0]/60:
                        return res[j].text
                        break

    text = ""
    for i in range(len(res)):
        text += res[i].text

    details = {}
    if "Ministry of Health & Family WelfareGovernment of India" in text and "Together, India will defeatCOVID-19" in text:
        details["Beneficiary_Name"] = findtext("Beneficiary Name") 
        details["Age"] = findtext("Age")
        details["Gender"] = findtext("Gender") 
        details["ID_Verified"] = findtext("ID Verified")
        details["Beneficiary_Reference_ID"] = findtext("Beneficiary Reference ID") 
        if "Provisional Certificate for COVID-19 Vaccination - 1st Dose" in text:
            print("1dose")
            details["Vaccine_Name"] = findtext("Vaccine Name")
            details["Date_of_Dose"] = findtext("Date of Dose")
            details["Next_due_date"] = findtext("Next due date")
            details["Vaccinated_by"] = findtext("Vaccinated by")
            details["Vaccination_at"] = findtext("Vaccination at")
        elif "Final Certificate for COVID-19 Vaccination" in text:
            print("2dose")
            details["Vaccine_Name"] = findtext("Vaccine Name")
            details["Date_of_Dose_1"] = findtext("Date of 1")
            details["Date_of_Dose_2"] = findtext("Date of 2")
            details["Vaccinated_by"] = findtext("Vaccinated by")
            details["Vaccination_at"] = findtext("Vaccination at")
        else:
            print("wrg")
    else:
        print("wrg certificate")

    return details

if __name__ =='__main__':  
    app.run(debug = True,port='5004',host='0.0.0.0')