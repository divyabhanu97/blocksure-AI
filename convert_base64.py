import base64
from PIL import Image
from io import BytesIO
def ConvertoImage(img_data,imagename):
    try:
        im = Image.open(BytesIO(base64.b64decode(img_data)))
        im.save(imagename+'.png', 'PNG')
    except Exception as e:
        print(str(e))
def ConvertoVideo(video_data,videoname):

    try:

        fh = open(videoname+'.mp4', "wb")

        fh.write(base64.b64decode(video_data))

        fh.close()

        # im.save(videoname+'.mp4', 'MP4')

    except Exception as e:

        print(str(e))


