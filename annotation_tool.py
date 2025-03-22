import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageGrab
import json
import os
import pytesseract

class AnnotationTool(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("OCR Annotation Tool")
        self.geometry("800x600")

        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.canvas.pack(pady=10, fill="both", expand=True)

        self.load_image_button = ttk.Button(self, text="Load Image", command=self.load_image)
        self.load_image_button.pack(pady=5)

        self.config_buttons_frame = ttk.Frame(self)
        self.config_buttons_frame.pack(pady=5)

        self.artifact_name_button = ttk.Button(self.config_buttons_frame, text="Artifact Name", command=lambda: self.set_config_mode("ArtifactName"))
        self.artifact_name_button.pack(side=tk.LEFT, padx=5)
        style = ttk.Style()
        style.configure("Red.TButton", foreground="red")
        self.artifact_name_button.configure(style="Red.TButton")
        self.artifact_name_label = ttk.Label(self.config_buttons_frame, text="")
        self.artifact_name_label.pack(side=tk.LEFT, padx=5)

        self.main_type_button = ttk.Button(self.config_buttons_frame, text="Main Type", command=lambda: self.set_config_mode("MainType"))
        self.main_type_button.pack(side=tk.LEFT, padx=5)
        style = ttk.Style()
        style.configure("Green.TButton", foreground="green")
        self.main_type_button.configure(style="Green.TButton")
        self.main_type_label = ttk.Label(self.config_buttons_frame, text="")
        self.main_type_label.pack(side=tk.LEFT, padx=5)

        self.main_value_button = ttk.Button(self.config_buttons_frame, text="Main Value", command=lambda: self.set_config_mode("MainValue"))
        self.main_value_button.pack(side=tk.LEFT, padx=5)
        style = ttk.Style()
        style.configure("Blue.TButton", foreground="blue")
        self.main_value_button.configure(style="Blue.TButton")
        self.main_value_label = ttk.Label(self.config_buttons_frame, text="")
        self.main_value_label.pack(side=tk.LEFT, padx=5)

        self.sub_stats_button = ttk.Button(self.config_buttons_frame, text="Sub Stats", command=lambda: self.set_config_mode("Sub"))
        self.sub_stats_button.pack(side=tk.LEFT, padx=5)
        style = ttk.Style()
        style.configure("Green.TButton", foreground="green")
        self.sub_stats_button.configure(style="Green.TButton")
        self.sub_stats_label = ttk.Label(self.config_buttons_frame, text="")
        self.sub_stats_label.pack(side=tk.LEFT, padx=5)

        self.level_button = ttk.Button(self.config_buttons_frame, text="Level", command=lambda: self.set_config_mode("Level"))
        self.level_button.pack(side=tk.LEFT, padx=5)
        style = ttk.Style()
        style.configure("Yellow.TButton", foreground="yellow")
        self.level_button.configure(style="Yellow.TButton")
        self.level_label = ttk.Label(self.config_buttons_frame, text="")
        self.level_label.pack(side=tk.LEFT, padx=5)

        self.save_config_button = ttk.Button(self, text="Save Configuration", command=self.save_configuration)
        self.save_config_button.pack(pady=5)

        self.config = {}
        self.image_path = None
        self.img = None
        self.photo = None
        self.rect_ids = {}
        self.start_x = None
        self.start_y = None
        self.config_mode = None

        self.canvas.bind("<ButtonPress-1>", self.start_rect)
        self.canvas.bind("<B1-Motion>", self.draw_rect)
        self.canvas.bind("<ButtonRelease-1>", self.end_rect)

    def draw_existing_rects(self):
        if self.image_path:
            if "ArtifactName_x1" in self.config and "ArtifactName_y1" in self.config and "ArtifactName_x2" in self.config and "ArtifactName_y2" in self.config:
                self.rect_ids["ArtifactName"] = self.canvas.create_rectangle(self.config["ArtifactName_x1"], self.config["ArtifactName_y1"], self.config["ArtifactName_x2"], self.config["ArtifactName_y2"], outline="red")
            if "MainType_x1" in self.config and "MainType_y1" in self.config and "MainType_x2" in self.config and "MainType_y2" in self.config:
                self.rect_ids["MainType"] = self.canvas.create_rectangle(self.config["MainType_x1"], self.config["MainType_y1"], self.config["MainType_x2"], self.config["MainType_y2"], outline="green")
            if "MainValue_x1" in self.config and "MainValue_y1" in self.config and "MainValue_x2" in self.config and "MainValue_y2" in self.config:
                self.rect_ids["MainValue"] = self.canvas.create_rectangle(self.config["MainValue_x1"], self.config["MainValue_y1"], self.config["MainValue_x2"], self.config["MainValue_y2"], outline="blue")
            if "Sub_x1" in self.config and "Sub_y1" in self.config and "Sub_x2" in self.config and "Sub_y2" in self.config:
                self.rect_ids["Sub"] = self.canvas.create_rectangle(self.config["Sub_x1"], self.config["Sub_y1"], self.config["Sub_x2"], self.config["Sub_y2"], outline="green")
            if "Level_x1" in self.config and "Level_y1" in self.config and "Level_x2" in self.config and "Level_y2" in self.config:
                self.rect_ids["Level"] = self.canvas.create_rectangle(self.config["Level_x1"], self.config["Level_y1"], self.config["Level_x2"], self.config["Level_y2"], outline="yellow")

    def load_image(self):
        self.image_path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
        if self.image_path:
            self.img = Image.open(self.image_path)
            self.photo = ImageTk.PhotoImage(self.img)
            self.canvas.config(width=self.img.width, height=self.img.height)
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
            self.canvas.image = self.photo  # Keep a reference!
            self.config["width"] = self.img.width
            self.config["height"] = self.img.height

    def set_config_mode(self, mode):
        self.config_mode = mode
        print(f"Configuring for: {mode}")

    def start_rect(self, event):
        if self.config_mode:
            # Record starting position
            self.start_x = event.x
            self.start_y = event.y

    def draw_rect(self, event):
        if self.config_mode and self.start_x and self.start_y:
            # Draw new rect
            if self.config_mode == "ArtifactName":
                outline_color = 'red'
            elif self.config_mode == "MainType":
                outline_color = 'green'
            elif self.config_mode == "MainValue":
                outline_color = 'blue'
            elif self.config_mode == "Sub":
                outline_color = 'green'
            elif self.config_mode == "Level":
                outline_color = 'yellow'
            else:
                outline_color = 'black'

            if self.config_mode in self.rect_ids:
                 self.canvas.delete(self.rect_ids[self.config_mode])

            self.rect_ids[self.config_mode] = self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y, outline=outline_color)

    def end_rect(self, event):
        if self.config_mode:
            # Get end position
            end_x = event.x
            end_y = event.y
            # Add coordinates to config
            self.config[f"{self.config_mode}_x1"] = self.start_x
            self.config[f"{self.config_mode}_y1"] = self.start_y
            self.config[f"{self.config_mode}_x2"] = end_x
            self.config[f"{self.config_mode}_y2"] = end_y

            # Perform OCR on the selected region
            text = self.perform_ocr(self.start_x, self.start_y, end_x, end_y)

            # Update label with OCR result
            if self.config_mode == "ArtifactName":
                self.artifact_name_label.config(text=text)
            elif self.config_mode == "MainType":
                self.main_type_label.config(text=text)
            elif self.config_mode == "MainValue":
                self.main_value_label.config(text=text)
            elif self.config_mode == "Sub":
                self.sub_stats_label.config(text=text)
            elif self.config_mode == "Level":
                self.level_label.config(text=text)

            # Reset config mode
            self.config_mode = None

    def perform_ocr(self, x1, y1, x2, y2):
        if not self.image_path:
            return "No image loaded"
        try:
            # Use ImageGrab to capture the screen region
            bbox = (self.canvas.winfo_rootx() + x1, self.canvas.winfo_rooty() + y1,
                    self.canvas.winfo_rootx() + x2, self.canvas.winfo_rooty() + y2)
            img = ImageGrab.grab(bbox=bbox)

            # Perform OCR using pytesseract
            text = pytesseract.image_to_string(img, lang='jpn', config='--psm 6')
            return text.strip()
        except Exception as e:
            return f"Error during OCR: {e}"

    def save_configuration(self):
        os.makedirs("ocrSetting", exist_ok=True)
        filepath = "ocrSetting/ocr1.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)
        print(f"Configuration saved to {filepath}")

if __name__ == "__main__":
    app = AnnotationTool()
    app.mainloop()
