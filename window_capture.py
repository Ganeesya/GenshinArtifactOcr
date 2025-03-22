import time
import win32gui
import win32con
import mss
import mss.tools
import pytesseract
from PIL import Image
import re
import Levenshtein

class WindowCapture:

    def levenshtein_distance(self, s1, s2):
        return Levenshtein.distance(s1, s2)

    def __init__(self, window_name):
        self.window_name = window_name
        self.hwnd = win32gui.FindWindow(None, self.window_name)
        if not self.hwnd:
            print('Window not found: {}'.format(window_name))
            return None

        # Get window size
        window_rect = win32gui.GetWindowRect(self.hwnd)
        self.x = window_rect[0]
        self.y = window_rect[1]
        self.width = window_rect[2] - self.x
        self.height = window_rect[3] - self.y

        # Define the monitor to capture
        self.monitor = {"top": self.y, "left": self.x, "width": self.width, "height": self.height}

        self.sct = mss.mss()

    def is_foreground(self):
        return win32gui.GetForegroundWindow() == self.hwnd

    def capture(self, output):
        # Wait for the window to be in the foreground
        while not self.is_foreground():
            time.sleep(0.1)

        # Grab the data
        sct_img = self.sct.grab(self.monitor)

        # Save to the picture file
        mss.tools.to_png(sct_img.rgb, sct_img.size, output=output)
        print(f"Screenshot saved as {output}")

        return output

    def ocr(self, image_path):
        try:
            # Load configuration from file
            config_path = "ocrSetting/ocr1.json"
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            # Open the image using PIL
            img = Image.open(image_path)

            ocr_result = {}

            # Perform OCR on ArtifactName region
            if "ArtifactName_x1" in config:
                x1, y1, x2, y2 = config["ArtifactName_x1"], config["ArtifactName_y1"], config["ArtifactName_x2"], config["ArtifactName_y2"]
                artifact_name_img = img.crop((x1, y1, x2, y2))
                ocr_text = pytesseract.image_to_string(artifact_name_img, lang='jpn', config='--psm 6')
                artifact_name = ocr_text.strip()

                # Load artifact names from artifactNameToPositonMap.json
                artifact_names_path = "artifactNameToPositonMap.json"
                with open(artifact_names_path, "r", encoding="utf-8") as f:
                    artifact_name_map = json.load(f)
                artifact_names = list(artifact_name_map.keys())

                # Find the closest match
                closest_name = min(artifact_names, key=lambda x: self.levenshtein_distance(artifact_name, x))

                # Get artifact position from artifactNameToPositonMap.json
                artifact_position = artifact_name_map.get(closest_name)

                ocr_result["ArtifactName"] = artifact_name
                ocr_result["closest_name"] = closest_name
                ocr_result["artifact_position"] = artifact_position

            # Perform OCR on MainType region
            if "MainType_x1" in config:
                x1, y1, x2, y2 = config["MainType_x1"], config["MainType_y1"], config["MainType_x2"], config["MainType_y2"]
                main_type_img = img.crop((x1, y1, x2, y2))
                ocr_text = pytesseract.image_to_string(main_type_img, lang='jpn', config='--psm 6')
                ocr_result["MainType"] = ocr_text.strip()

            # Perform OCR on MainValue region
            if "MainValue_x1" in config:
                x1, y1, x2, y2 = config["MainValue_x1"], config["MainValue_y1"], config["MainValue_x2"], config["MainValue_y2"]
                main_value_img = img.crop((x1, y1, x2, y2))
                ocr_text = pytesseract.image_to_string(main_value_img, lang='jpn', config='--psm 6')
                ocr_result["MainValue"] = ocr_text.strip()

            # Perform OCR on Level region
            if "Level_x1" in config:
                x1, y1, x2, y2 = config["Level_x1"], config["Level_y1"], config["Level_x2"], config["Level_y2"]
                level_img = img.crop((x1, y1, x2, y2))
                ocr_text = pytesseract.image_to_string(level_img, lang='jpn', config='--psm 6')
                ocr_result["Level"] = ocr_text.strip()

                # Save artifact info and thumbnail if level is 20
                if "+20" in ocr_text:
                    # Save artifact info to file
                    filename = f"{closest_name}_{time.strftime('%Y%m%d%H%M%S')}.json"
                    filepath = os.path.join("artifactDB", "artifact_data", filename)
                    os.makedirs(os.path.join("artifactDB", "artifact_data"), exist_ok=True)
                    with open(filepath, "w", encoding="utf-8") as f:
                        json.dump(ocr_result, f, ensure_ascii=False)

                    # Save artifact name thumbnail to file
                    thumbnail_filename = f"{closest_name}_{time.strftime('%Y%m%d%H%M%S')}.png"
                    thumbnail_filepath = os.path.join("artifactDB", "artifact_thumbnails", thumbnail_filename)
                    os.makedirs(os.path.join("artifactDB", "artifact_thumbnails"), exist_ok=True)
                    artifact_name_img.save(thumbnail_filepath)

            # Perform OCR on Sub region
            if "Sub_x1" in config:
                x1, y1, x2, y2 = config["Sub_x1"], config["Sub_y1"], config["Sub_x2"], config["Sub_y2"]
                sub_img = img.crop((x1, y1, x2, y2))
                ocr_text = pytesseract.image_to_string(sub_img, lang='jpn', config='--psm 6')
                ocr_result["Sub"] = ocr_text.strip()

            return json.dumps(ocr_result, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    def parse_ocr_result(self, text):
        try:
            artifact_name_match = re.search(r"聖遺物\s+\d+/\d+\s+(.+)", text)
            artifact_name = artifact_name_match.group(1).strip() if artifact_name_match else None

            level_match = re.search(r"\+20", text)
            level = 20 if level_match else 0

            main_type_match = re.search(r"HP\+(\d+)", text)
            main_type = "HP" if main_type_match else None
            main_value_match = re.search(r"HP\+(\d+)", text)
            main_value = int(main_value_match.group(1)) if main_value_match else None

            sub_stats = []
            sub_stat_matches = re.finditer(r"・(.*?)([\d\.]+)(%)?", text)
            for match in sub_stat_matches:
                stat_type = match.group(1).strip()
                stat_value = float(match.group(2))
                is_percent = bool(match.group(3))
                sub_stats.append({"Type": stat_type, "Value": stat_value, "Persent": is_percent})

            ocr_result = {
                "ArtifactName": artifact_name,
                "Level": level,
                "Main": {"Type": main_type, "Value": main_value},
                "Sub": sub_stats,
            }
            return ocr_result
        except Exception as e:
            print(f"Error parsing OCR result: {e}")
            return {"text": text}


if __name__ == '__main__':
    try:
        # Replace 'Your Window Name' with the actual window name
        window_capture = WindowCapture("原神")
        image_path = window_capture.capture()

        if image_path:
            try:
                extracted_text = window_capture.ocr(image_path)
                print("Extracted Text from Screenshot:")
                print(extracted_text)
                with open("ocr_result.json", "w", encoding="utf-8") as f:
                    f.write(extracted_text)
            except Exception as e:
                print(f"Error during OCR: {e}")
                with open("ocr_result.json", "w", encoding="utf-8") as f:
                    f.write(f"Error during OCR: {e}")

    except Exception as e:
        print(f"Error: {e}")
