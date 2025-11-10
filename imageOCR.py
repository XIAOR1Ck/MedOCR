import cv2
import numpy as np
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"/usr/bin/tesseract-ocr"


def processImage(imgBytes):
    npArray = np.frombuffer(imgBytes, np.uint8)
    img = cv2.imdecode(npArray, cv2.IMREAD_COLOR)
    grayImg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(grayImg)
    print(text)
