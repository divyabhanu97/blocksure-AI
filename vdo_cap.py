import cv2
from pyzbar.pyzbar import decode

cap = cv2.VideoCapture(0)
cap.set(3,640)
cap.set(4,480)

while True:
    sucess, img = cap.read()
    img = cv2.flip(img,1)
    for barcode in decode(img):
        print(barcode.data)
        myData = barcode.data.decode('utf-8')
        print(myData)
    cv2.imshow('Result',img)
    cv2.waitKey(1)