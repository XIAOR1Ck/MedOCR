import re

import cv2
import numpy as np
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"/usr/bin/tesseract-ocr"


class OCRProcessor:
    def __init__(self):
        self.setup_tesseract_config()

    def setup_tesseract_config(self):
        # Configure Tesseract for medicine text recognition
        self.custom_config = r"--oem 3 --psm 6"

    def preprocess_image(self, image_Bytes):
        # Preprocess image for better OCR accuracy

        npArray = np.frombuffer(image_Bytes, np.uint8)
        img = cv2.imdecode(npArray, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError(f"Could not load image {image_Bytes}")

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Noise removal
        denoised = cv2.medianBlur(gray, 5)

        # Thresholding
        _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        return thresh

    def extract_text(self, image_path):
        # Extract text from medicine image
        try:
            processed_image = self.preprocess_image(image_path)
            text = pytesseract.image_to_string(
                processed_image, config=self.custom_config
            )

            cleaned_text = self.clean_ocr_text(text)

            return {
                "success": True,
                "raw_text": text,
                "cleaned_text": cleaned_text,
                "error": None,
            }

        except Exception as e:
            return {
                "success": False,
                "raw_text": "",
                "cleaned_text": "",
                "error": str(e),
            }

    def clean_ocr_text(self, text):
        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)
        return text.strip()
