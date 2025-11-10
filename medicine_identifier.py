from typing import Any, Dict

from medicine_extractor import MedicineExtractor
from medicine_matcher import MedicineMatcher
from ocr_processor import OCRProcessor


class MedicineIdentifier:
    def __init__(self, csv_database_path: str):
        self.ocr_processor = OCRProcessor()
        self.medicine_extractor = MedicineExtractor()
        self.medicine_matcher = MedicineMatcher(csv_database_path)

    def identify_medicine(self, image_Bytes, top_matches: int = 5) -> Dict[str, Any]:
        # OCR Processing
        ocr_result = self.ocr_processor.extract_text(image_Bytes)

        if not ocr_result["success"]:
            return {
                "success": False,
                "error": f"OCR failed: {ocr_result['error']}",
                "matches": [],
            }

        # Medicine Extraction
        extracted_info = self.medicine_extractor.extract_medicine_info(
            ocr_result["cleaned_text"]
        )

        # Medicine Matching
        matches = self.medicine_matcher.find_matches(extracted_info, top_n=top_matches)

        # Prepare results
        result = {
            "success": True,
            "ocr_text": ocr_result["cleaned_text"],
            "extracted_info": extracted_info,
            "matches": [],
        }

        for match_data, score in matches:
            result["matches"].append(
                {
                    "setid": match_data["SETID"],
                    "description": match_data["RXSTRING"],
                    "type": match_data["RXTTY"],
                    "confidence_score": score,
                    "rxcui": match_data.get("RXCUI", ""),
                }
            )

        return result
