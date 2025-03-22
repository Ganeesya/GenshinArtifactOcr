import os
import json
import unittest
from PIL import Image
import Levenshtein
from genshinArtifactOcr import GenshinArtifactOcr

class TestOCR(unittest.TestCase):

    def test_ocr(self):
        # Set the path to the test data directory
        test_data_dir = "testData"
        png_dir = os.path.join(test_data_dir, "png")
        text_dir = os.path.join(test_data_dir, "text")

        # Iterate through all png files in the png directory
        for filename in os.listdir(png_dir):
            if filename.endswith(".png"):
                # Get the base name of the file
                base_name = os.path.splitext(filename)[0]

                # Create the path to the png file
                png_path = os.path.join(png_dir, filename)

                # Create the path to the corresponding text file
                text_path = os.path.join(text_dir, base_name + ".txt")

                # Check if the text file exists
                if os.path.exists(text_path):
                    # Read the expected OCR result from the text file
                    with open(text_path, "r", encoding="utf-8") as f:
                        expected_text = f.read()

                    # Perform OCR on the png file
                    try:
                        img = Image.open(png_path)

                        # Initialize GenshinArtifactOcr
                        ocr = GenshinArtifactOcr()

                        # Perform OCR and get the result
                        ocr_result = ocr.ocr_artifact_data(png_path)

                        print(ocr_result)

                    except Exception as e:
                        print(f"Error during OCR: {e}")
                        self.fail(f"Error during OCR: {e}")
                        continue


                    # Compare the actual OCR result with the expected result
                    # self.assertEqual(actual_json, json.loads(expected_text), f"OCR failed for {filename}")
                else:
                    self.fail(f"Missing text file for {filename}")

if __name__ == "__main__":
    unittest.main()
