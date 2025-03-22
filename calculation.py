import os
import json
import Levenshtein
from genshinArtifactOcr import GenshinArtifactOcr

class Calculation:

    def __init__(self):
        self.artifact_ocr = GenshinArtifactOcr()

    def get_substat_type(self, sub):
        stat_type = sub["Type"]
        if sub.get("Persent"):
            if stat_type == "攻撃力":
                return "攻撃力%"
            elif stat_type == "防御力":
                return "防御力%"
            elif stat_type == "HP":
                return "HP%"
        return stat_type

    def calculate_artifact_score(self, artifact_data):
        # Calculate artifact score based on substats
        attack_score = 0
        defense_score = 0
        hp_score = 0
        elemental_mastery_score = 0
        energy_recharge_score = 0

        for sub in artifact_data.get("Sub") or []:
            stat_type = self.get_substat_type(sub)

            attack_score += self.calculate_substat_score(stat_type, float(sub["Value"]), "攻撃力")
            defense_score += self.calculate_substat_score(stat_type, float(sub["Value"]), "防御力")
            hp_score += self.calculate_substat_score(stat_type, float(sub["Value"]), "HP")
            elemental_mastery_score += self.calculate_substat_score(stat_type, float(sub["Value"]), "元素熟知")
            energy_recharge_score += self.calculate_substat_score(stat_type, float(sub["Value"]), "元素チャージ効率")

        return {
            "攻撃力": attack_score,
            "防御力": defense_score,
            "HP": hp_score,
            "元素熟知": elemental_mastery_score,
            "元素チャージ効率": energy_recharge_score
        }
    
    def calculate_substat_score(self, stat_type, stat_value, rate_type):
        # Calculate score for a single substat based on the rate type
        if rate_type == "攻撃力":
            if stat_type == "攻撃力%":
                return float(stat_value) * 1
            elif stat_type == "会心ダメージ":
                return float(stat_value) * 1
            elif stat_type == "会心率":
                return float(stat_value) * 2
            else:
                return 0
        elif rate_type == "防御力":
            if stat_type == "防御力%":
                return float(stat_value) * 1
            elif stat_type == "会心ダメージ":
                return float(stat_value) * 1
            elif stat_type == "会心率":
                return float(stat_value) * 2
            else:
                return 0
        elif rate_type == "HP":
            if stat_type == "HP%":
                return float(stat_value) * 1
            elif stat_type == "会心ダメージ":
                return float(stat_value) * 1
            elif stat_type == "会心率":
                return float(stat_value) * 2
            else:
                return 0
        elif rate_type == "元素熟知":
            if stat_type == "元素熟知":
                return float(stat_value) * 0.25
            elif stat_type == "会心ダメージ":
                return float(stat_value) * 1
            elif stat_type == "会心率":
                return float(stat_value) * 2
            else:
                return 0
        elif rate_type == "元素チャージ効率":
            if stat_type == "元素チャージ効率":
                return float(stat_value) * 1
            elif stat_type == "会心ダメージ":
                return float(stat_value) * 1
            elif stat_type == "会心率":
                return float(stat_value) * 2
            else:
                return 0
        else:
            return 0

    def calculate_future_stats(self, artifact_data):
        # Calculate average and max stats when leveling to 20
        level = int(artifact_data.get("Level", 0))
        scores = self.calculate_artifact_score(artifact_data)
        
        # Define the possible upgrade values for each substat
        substat_values = {
            "会心率": [2.7, 3.1, 3.5, 3.9],
            "会心ダメージ": [5.4, 6.2, 7.0, 7.8],
            "攻撃力%": [4.1, 4.7, 5.3, 5.8],
            "元素チャージ効率": [4.5, 5.2, 5.8, 6.5],
            "HP%": [4.1, 4.7, 5.3, 5.8],
            "防御力%": [5.1, 5.8, 6.6, 7.3],
            "元素熟知": [16, 19, 21, 23],
            "攻撃力": [14, 16, 18, 19],
            "HP": [209, 239, 269, 299],
            "防御力": [16, 19, 21, 23]
        }

        score_type = ["攻撃力", "防御力", "HP", "元素熟知", "元素チャージ効率"]
        
        # Calculate the average and maximum possible score increase
        potential_rolls = (20 - level) // 4 if level < 20 else 0

        future_stats = {}
        for stat_type in score_type:
            average_increase = 0
            max_increase = 0

            wild_ave_add = 0
            wild_max_add = 0
            wild_ave_count = 0
            
            if len(artifact_data.get("Sub", [])) < 4:
                willSubStat = [
                    key for key in substat_values
                    if key not in [sub["Type"] for sub in artifact_data.get("Sub", [])] and key != artifact_data.get("Main", {}).get("Type")
                ]
                
                # willSubStatの平均と最大値を計算して、average_increaseとmax_increaseに加算する
                for sub_type in willSubStat:
                    sub_values = substat_values[sub_type]
                    for sub_value in sub_values:
                        wild_ave_add += self.calculate_substat_score(sub_type, sub_value, stat_type)
                        wild_max_add = max( wild_max_add, self.calculate_substat_score(sub_type, sub_value, stat_type) )
                        wild_ave_count += 1


            for _ in range(potential_rolls):
                max_add = wild_max_add
                ave_add = wild_ave_add
                average_addCount = wild_ave_count
                for sub in artifact_data.get("Sub", []):
                    sub_values = substat_values[sub["Type"]]
                    for sub_value in sub_values:
                        ave_add += self.calculate_substat_score(sub["Type"], sub_value, stat_type)
                        max_add = max( max_add, self.calculate_substat_score(sub["Type"], sub_value, stat_type) )
                        average_addCount += 1
                average_increase += ave_add / average_addCount
                max_increase += max_add

        
            future_stats[stat_type] = {
                "score": scores[stat_type],
                "average": scores[stat_type] + average_increase if stat_type in scores else average_increase,
                "max": scores[stat_type] + max_increase if stat_type in scores else max_increase
            }
        return future_stats
    
    def getScoreList(self, future_stat, artifact_data):
        show_score_type = {
              "攻撃力":"ATK",
              "防御力":"DEF",
              "HP":"HP ",
              "元素熟知":"ELE",
              "元素チャージ効率":"CHG"
            }
        main_type = artifact_data["Main"]["Type"]
        main_type_raw = artifact_data["RawMainType"]
        if int( artifact_data.get("Level", 0)) == 20:
            ret = f"{main_type} : {main_type_raw}\n"
            ret += f"   : score\n"
            for score_type, score in future_stat.items():
                scoreValue = score["score"]
                ret += f"{show_score_type[score_type]}: {scoreValue:5.1f}\n"
            return ret
        else:
            ret = f"{main_type} : {main_type_raw}\n"
            ret += f"   : score\t: ave\t: max\n"
            for score_type, score in future_stat.items():
                scoreValue = score["score"]
                scoreAve = score["average"]
                scoreMax = score["max"]
                ret += f"{show_score_type[score_type]}: {scoreValue:5.1f} : {scoreAve:5.1f} : {scoreMax:5.1f}\n"
            return ret

    def get_artifact_data(self, image_path):
        artifact_data = self.artifact_ocr.ocr_artifact_data(image_path)
        return artifact_data
    
    def align_right_with_space(self, text, width):
        text_length = 0
        for char in text:
            if ord(char) > 255:  # 2バイト文字の判定
                text_length += 2
            else:
                text_length += 1
        
        if text_length >= width:
            return text  # 文字列が幅より長い場合はそのまま返す
        
        padding_length = width - text_length
        padding = " " * padding_length
        return padding + text

if __name__ == '__main__':
    calculator = Calculation()
    
    # Get all png files in the testData/png directory
    image_dir = "testData/png"
    image_files = [f for f in os.listdir(image_dir) if f.endswith(".png")]

    for image_file in image_files:
        image_path = os.path.join(image_dir, image_file)
        artifact_data = calculator.get_artifact_data(image_path)

        if "error" not in artifact_data:
            scores = calculator.calculate_future_stats(artifact_data)
            # scoresの内容をprintする
            print( calculator.getScoreList(scores, artifact_data) )
            # print(f"        : score :  ave   : max")
            # for score_type, score in scores.items():
            #     scoreValue = score["score"]
            #     scoreAve = score["average"]
            #     scoreMax = score["max"]
            #     print(f"{score_type} : {scoreValue:.1f} : {scoreAve:.1f} : {scoreMax:.1f}")

            print(f"File: {image_file}")
        else:
            print(f"Error artifact_data: {artifact_data['error']}")
