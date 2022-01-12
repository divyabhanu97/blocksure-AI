import base64



with open(r"C:\MediaFiles\Call with Akash Balachandar-20210912_172127-Meeting Recording.mp4", "rb") as videoFile:
    text = base64.b64encode(videoFile.read())
    # print(text)
    file = open("textTest.txt", "wb") 
    file.write(text)
    file.close()

    fh = open("video.mp4", "wb")
    fh.write(base64.b64decode(text))
    fh.close()