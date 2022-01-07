import base64
from PIL import Image
from io import BytesIO
def ConvertoImage(img_data,imagename):
    try:
        im = Image.open(BytesIO(base64.b64decode(img_data)))
        im.save(imagename+'.png', 'PNG')
    except Exception as e:
        print(str(e))
