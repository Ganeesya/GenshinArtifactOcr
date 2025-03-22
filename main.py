import tkinter as tk
from tkinter import ttk
import keyboard
import time
import datetime
import os
import json
from PIL import Image, ImageTk, ImageDraw, ImageFont
import window_capture
import calculation
import json

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Genshin Impact Screen Capture")
        self.geometry("700x800")

        # Shortcut Frame
        self.shortcut_frame = ttk.Frame(self)
        self.shortcut_frame.pack(pady=5)

        self.shortcut_label = ttk.Label(self.shortcut_frame, text="Shortcut:")
        self.shortcut_label.pack(side=tk.LEFT, padx=5)

        self.shortcut_entry = ttk.Entry(self.shortcut_frame)
        self.shortcut_entry.pack(side=tk.LEFT, padx=5)

        # Load settings
        self.settings_file = "settings.json"
        self.settings = self.load_settings()
        default_shortcut = self.settings.get("shortcut", "ctrl+shift+s")

        self.shortcut_entry.insert(0, default_shortcut)  # Default shortcut

        self.save_button = ttk.Button(self.shortcut_frame, text="Save Shortcut", command=self.save_shortcut)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.capture_button = ttk.Button(self, text="Capture", command=self.capture_screen)
        self.capture_button.pack(pady=10)

        self.ocr_frame = ttk.Frame(self)
        self.ocr_frame.pack(pady=10)

        self.thumbnail_frame = ttk.Frame(self.ocr_frame)
        self.thumbnail_frame.pack(side=tk.LEFT)

        self.db_frame = ttk.Frame(self.ocr_frame)
        self.db_frame.pack(side=tk.RIGHT)

        self.thumbnails = []
        self.db = []
        self.update_thumbnails()

        self.register_shortcut()

    def load_settings(self):
        try:
            with open(self.settings_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_settings(self):
        shortcut = self.shortcut_entry.get()
        self.settings["shortcut"] = shortcut
        with open(self.settings_file, "w") as f:
            json.dump(self.settings, f)

    def save_shortcut(self):
        self.save_settings()
        self.register_shortcut()

    def register_shortcut(self):
        try:
            keyboard.unhook_all()
        except Exception as e:
            print(f"Error registering shortcut: {e}")
        shortcut = self.shortcut_entry.get()
        keyboard.add_hotkey(shortcut, self.capture_screen)
        print(f"Shortcut registered: {shortcut}")

    def capture_screen(self):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        # Replace 'Your Window Name' with the actual window name
        try:
            window_capture_instance = window_capture.WindowCapture("原神")
            image_path = window_capture_instance.capture(filename)

            # Calculate artifact score
            calculator = calculation.Calculation()
            artifact_data = calculator.get_artifact_data(image_path)
            if "error" not in artifact_data:
                future_stats = calculator.calculate_future_stats(artifact_data)
                score_list_text = calculator.getScoreList(future_stats, artifact_data)

                # Open the captured image
                img = Image.open(image_path)
                # Use a drawing context
                draw = ImageDraw.Draw(img)
                # Choose a font
                try:
                    font = ImageFont.truetype("arial.ttf", size=20)  # Adjust font path and size as needed
                except IOError:
                    font = ImageFont.load_default()

                # Calculate the position to place the text
                x = img.width
                y = 10
                line_height = font.font.getsize("Sample")[0][1]  # Get the height of a line of text

                # Draw the text on the image, handling newlines
                for line in score_list_text.splitlines():
                    draw.text((x, y), line, font=font, fill=(255, 255, 255))  # White color
                    y += line_height  # Move to the next line

            else:
                print(f"Error artifact_data: {artifact_data['error']}")

            self.update_thumbnails()
        except Exception as e:
            print(f"Error: {e}, type: {type(e)}")
            import traceback
            traceback.print_exc()

    def update_thumbnails(self):
        # Clear previous thumbnails
        for widget in self.thumbnail_frame.winfo_children():
            widget.destroy()
        for widget in self.db_frame.winfo_children():
            widget.destroy()

        # Get recent screenshots
        files = [f for f in os.listdir() if f.startswith("screenshot_") and f.endswith(".png")]
        files.sort(key=lambda f: os.path.getmtime(f), reverse=True)
        recent_files = files[:1]

        # Load ocr settings
        try:
            with open("ocrSetting/ocr1.json", "r") as f:
                ocr_settings = json.load(f)
        except FileNotFoundError:
            print("Error: ocrSetting/ocr1.json not found")
            return

        # Create thumbnails
        self.thumbnails = []
        self.db = []
        for file in recent_files:
            try:
                img = Image.open(file)
                # Calculate bounding box
                x1 = min(ocr_settings["ArtifactName_x1"], ocr_settings["MainType_x1"], ocr_settings["MainValue_x1"], ocr_settings["Sub_x1"], ocr_settings["Level_x1"])
                y1 = min(ocr_settings["ArtifactName_y1"], ocr_settings["MainType_y1"], ocr_settings["MainValue_y1"], ocr_settings["Sub_y1"], ocr_settings["Level_y1"])
                x2 = max(ocr_settings["ArtifactName_x2"], ocr_settings["MainType_x2"], ocr_settings["MainValue_x2"], ocr_settings["Sub_x2"], ocr_settings["Level_x2"])
                y2 = max(ocr_settings["ArtifactName_y2"], ocr_settings["MainType_y2"], ocr_settings["MainValue_y2"], ocr_settings["Sub_y2"], ocr_settings["Level_y2"])

                # Crop the image
                img = img.crop((x1, y1, x2, y2))
                img.thumbnail((200, 200))  # Resize after cropping
                photo = ImageTk.PhotoImage(img)
                self.thumbnails.append(photo)

                # Create a frame to hold the thumbnail and text
                frame = ttk.Frame(self.thumbnail_frame, borderwidth=2, relief="solid")
                frame.pack(side=tk.LEFT, padx=5, pady=5)

                # Create a label for the thumbnail
                thumbnail_label = ttk.Label(frame, image=photo)
                thumbnail_label.pack(side=tk.LEFT)

                # Get artifact data and score
                calculator = calculation.Calculation()
                artifact_data = calculator.get_artifact_data(file)  # Use the filename as the image path
                if "error" not in artifact_data:
                    future_stats = calculator.calculate_future_stats(artifact_data)
                    score_list_text = calculator.getScoreList(future_stats, artifact_data)
                else:
                    score_list_text = f"Error: {artifact_data.get('error', 'Unknown')}"

                # Create a label for the score text
                score_label = ttk.Label(frame, text=score_list_text, font=("Courier New", 8), anchor=tk.W)
                score_label.pack(side=tk.LEFT)

                # Find similar artifacts
                similar_artifacts = self.find_similar_artifacts(artifact_data)

                # Create a frame for similar artifacts
                similar_frame = ttk.Frame(self.db_frame,borderwidth=2)
                similar_frame.pack(side=tk.TOP, fill=tk.X)

                for i, artifact in enumerate(similar_artifacts):
                    artifact_text = calculator.getScoreList(artifact['Score'], artifact)
                    
                    similar_box = ttk.Frame(self.db_frame)

                    try:
                        dbImge = Image.open(artifact["thumbnail"])
                        dbImge.thumbnail((200, 200))
                        dbPhoto = ImageTk.PhotoImage(dbImge)
                        artifact_label = ttk.Label(similar_box, text=artifact_text, font=("Courier New", 8), anchor=tk.W)
                        artifact_label.pack(side=tk.RIGHT)
                        artifact_img_label = ttk.Label(similar_box, image=dbPhoto)
                        artifact_img_label.image = dbPhoto
                        artifact_img_label.pack(side=tk.LEFT)
                        
                    except:
                        artifact_label = ttk.Label(similar_box, text=artifact_text, font=("Courier New", 8), anchor=tk.W)
                    if i == 0:
                        similar_box.pack(side=tk.TOP)
                    else:
                        similar_box.pack(side=tk.BOTTOM)

            except Exception as e:
                print(f"Error creating thumbnail for {file}: {e}")

    def find_similar_artifacts(self, artifact_data):
        artifact_data_dir = os.path.join("artifactDB", "artifact_data")
        artifacts = []
        if not os.path.exists(artifact_data_dir):
            return artifacts
        for filename in os.listdir(artifact_data_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(artifact_data_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    artifact = json.load(f)
                    
                    if artifact_data["Position"] == "空の杯":
                        if artifact["Main"]["Type"] == artifact_data["Main"]["Type"] and artifact["Position"] == artifact_data["Position"]:
                            artifact["thumbnail"] = filepath.replace("artifact_data", "artifact_thumbnails").replace(".json", ".png")
                            artifacts.append(artifact)
                    elif artifact_data["Position"] == "時の砂":
                        if artifact["Main"]["Type"] == artifact_data["Main"]["Type"] and artifact["ArtifactName"] == artifact_data["ArtifactName"]:
                            artifact["thumbnail"] = filepath.replace("artifact_data", "artifact_thumbnails").replace(".json", ".png")
                            artifacts.append(artifact)
                    else:
                        if artifact["ArtifactName"] == artifact_data["ArtifactName"]:
                            artifact["thumbnail"] = filepath.replace("artifact_data", "artifact_thumbnails").replace(".json", ".png")
                            artifacts.append(artifact)
        # Sort by score
        artifacts.sort(key=lambda x: x["Score"]["攻撃力"]["score"] + x["Score"]["防御力"]["score"] + x["Score"]["HP"]["score"] + x["Score"]["元素熟知"]["score"] + x["Score"]["元素チャージ効率"]["score"], reverse=True)
        return artifacts[:3]

if __name__ == "__main__":
    app = App()
    app.mainloop()
