import time
import os
import json
import pytesseract
from PIL import Image
import Levenshtein

class GenshinArtifactOcr:

    def __init__(self, config_path="ocrSetting/ocr1.json", artifact_names_path="artifactNameToPositonMap.json"):
        self.config_path = config_path
        self.artifact_names_path = artifact_names_path
        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)
        with open(self.artifact_names_path, "r", encoding="utf-8") as f:
            self.artifact_names = [line.strip() for line in f]
        with open(artifact_names_path, "r", encoding="utf-8") as f:
            self.artifact_name_map = json.load(f)
        self.artifact_names = list(self.artifact_name_map.keys())

    def levenshtein_distance(self, s1, s2):
        return Levenshtein.distance(s1, s2)

    def get_closest_stat_type(self, stat_type, stat_types):
        if not stat_types:
            return stat_type
        closest_stat_type = min(stat_types, key=lambda x: self.levenshtein_distance(stat_type, x))
        return closest_stat_type

    def ocr_artifact_data(self, image_path):
        try:
            # Open the image using PIL
            img = Image.open(image_path)
            stat_types = ["攻撃力", "防御力", "HP", "元素熟知", "元素チャージ効率", "会心率", "会心ダメージ"
                          , "物理元素ダメージ", "炎元素ダメージ", "水元素ダメージ", "草元素ダメージ", "雷元素ダメージ", "風元素ダメージ", "氷元素ダメージ", "岩元素ダメージ", "与える治療効果"]

            ocr_result = {}

            # Perform OCR on ArtifactName region
            if "ArtifactName_x1" in self.config:
                x1, y1, x2, y2 = self.config["ArtifactName_x1"], self.config["ArtifactName_y1"], self.config["ArtifactName_x2"], self.config["ArtifactName_y2"]
                artifact_name_img = img.crop((x1, y1, x2, y2))
                ocr_text = pytesseract.image_to_string(artifact_name_img, lang='jpn', config='--psm 6')
                artifact_name = ocr_text.strip()

                # Find the closest match
                if self.artifact_names:
                    closest_name = min(self.artifact_names, key=lambda x: self.levenshtein_distance(artifact_name, x))
                    ocr_result["ArtifactName"] = closest_name
                    ocr_result["Position"] = self.artifact_name_map[closest_name]
                else:
                    ocr_result["ArtifactName"] = artifact_name
                    #return {"error": f"No artifact names found in {self.artifact_names_path}"}
                ocr_result["RawArtifactName"] = artifact_name

            # Perform OCR on MainType region
            if "MainType_x1" in self.config:
                x1, y1, x2, y2 = self.config["MainType_x1"], self.config["MainType_y1"], self.config["MainType_x2"], self.config["MainType_y2"]
                main_type_img = img.crop((x1, y1, x2, y2))
                main_type = pytesseract.image_to_string(main_type_img, lang='jpn', config='--psm 6').strip()
                closest_main_type = self.get_closest_stat_type(main_type, stat_types)
                ocr_result["Main"] = {"Type": closest_main_type}
                ocr_result["RawMainType"] = main_type

            # Perform OCR on MainValue region
            if "MainValue_x1" in self.config:
                x1, y1, x2, y2 = self.config["MainValue_x1"], self.config["MainValue_y1"], self.config["MainValue_x2"], self.config["MainValue_y2"]
                main_value_img = img.crop((x1, y1, x2, y2))
                main_value = pytesseract.image_to_string(main_value_img, lang='jpn', config='--psm 6').strip()
                is_percent = "%" in main_value
                ocr_result["Main"]["Value"] = main_value.replace("%", "")
                ocr_result["Main"]["Persent"] = is_percent
                ocr_result["RawMainValue"] = main_value

           # Perform OCR on Sub region
            if "Sub_x1" in self.config:
                x1, y1, x2, y2 = self.config["Sub_x1"], self.config["Sub_y1"], self.config["Sub_x2"], self.config["Sub_y2"]
                sub_img = img.crop((x1, y1, x2, y2))
                sub_text = pytesseract.image_to_string(sub_img, lang='jpn', config='--psm 6')
                sub_stats = []
                for line in sub_text.splitlines():
                    line = line.strip()
                    if line:
                        parts = line.split('+')
                        if len(parts) == 2:
                            stat_type = parts[0].replace("・", "").strip()
                            stat_value = parts[1].replace("%", "").strip()
                            is_percent = "%" in parts[1]
                            closest_stat_type = self.get_closest_stat_type(stat_type, stat_types)
                            sub_stats.append({"Type": closest_stat_type, "Value": stat_value, "Persent": is_percent})
                ocr_result["Sub"] = sub_stats
                ocr_result["RawSub"] = sub_text

            # Perform OCR on Level region
            if "Level_x1" in self.config:
                x1, y1, x2, y2 = self.config["Level_x1"], self.config["Level_y1"], self.config["Level_x2"], self.config["Level_y2"]
                level_img = img.crop((x1, y1, x2, y2))
                level = pytesseract.image_to_string(level_img, lang='jpn', config='--psm 6').strip()
                level = level.replace("+", "").replace("o", "0").replace("O", "0")
                try:
                    level = int(level)
                except ValueError:
                    level = 0
                ocr_result["Level"] = level
                ocr_result["RawLevel"] = level

            from calculation import Calculation
            calculator = Calculation()
            # score = calculator.calculate_artifact_score(ocr_result)
            score = calculator.calculate_future_stats(ocr_result)

            ocr_result["Score"] = score
            
            # Check if artifact already exists in DB
            def artifact_exists(ocr_result):
                artifact_data_dir = os.path.join("artifactDB", "artifact_data")
                if not os.path.exists(artifact_data_dir):
                    return False
                for filename in os.listdir(artifact_data_dir):
                    if filename.endswith(".json"):
                        filepath = os.path.join(artifact_data_dir, filename)
                        with open(filepath, "r", encoding="utf-8") as f:
                            existing_artifact = json.load(f)
                            if (existing_artifact["ArtifactName"] == ocr_result["ArtifactName"] and
                                existing_artifact["Main"] == ocr_result["Main"] and
                                existing_artifact["Sub"] == ocr_result["Sub"]):
                                return True
                return False

            # Save artifact info and thumbnail if level is 20 and it doesn't already exist
            if ocr_result["Level"] == 20:
                if not artifact_exists(ocr_result):
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
                    x1 = min(self.config["ArtifactName_x1"], self.config["MainType_x1"], self.config["MainValue_x1"], self.config["Sub_x1"], self.config["Level_x1"])
                    y1 = min(self.config["ArtifactName_y1"], self.config["MainType_y1"], self.config["MainValue_y1"], self.config["Sub_y1"], self.config["Level_y1"])
                    x2 = max(self.config["ArtifactName_x2"], self.config["MainType_x2"], self.config["MainValue_x2"], self.config["Sub_x2"], self.config["Level_x2"])
                    y2 = max(self.config["ArtifactName_y2"], self.config["MainType_y2"], self.config["MainValue_y2"], self.config["Sub_y2"], self.config["Level_y2"])
                    thumbnail_img = img.crop((x1, y1, x2, y2))
                    thumbnail_img.save(thumbnail_filepath)

        except Exception as e:
            return {"error": str(e)}
        
        return ocr_result

if __name__ == '__main__':
    ocr = GenshinArtifactOcr()
    image_path = "testData/png/screenshot_20250315_192052.png"  # Replace with a sample image path
    result = ocr.ocr_artifact_data(image_path)
    print(json.dumps(result, ensure_ascii=False))
