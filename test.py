import base64



with open(r"C:\Users\M1061065\OneDrive - Mindtree Limited\Pictures\Camera Roll\WIN_20211228_17_00_40_Pro.mp4", "rb") as videoFile:
    text = base64.b64encode(videoFile.read())
    # print(text)
    file = open("textTest.txt", "wb") 
    file.write(text)
    file.close()

    fh = open("video.mp4", "wb")
    fh.write(base64.b64decode(text))
    fh.close()