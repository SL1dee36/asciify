import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import tkinter as tk
import cv2
import os


class VideoTrimmer:
    def __init__(self, master):
        self.master = master
        master.title("Video Trimmer")

        # --- Input fields ---
        ctk.CTkLabel(master, text="Input Video File:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.input_file_entry = ctk.CTkEntry(master)
        self.input_file_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(master, text="Browse", command=self.browse_input_file).grid(row=0, column=2, padx=5, pady=5)

        ctk.CTkLabel(master, text="Start Time (seconds):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.start_time_entry = ctk.CTkEntry(master)
        self.start_time_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(master, text="End Time (seconds):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.end_time_entry = ctk.CTkEntry(master)
        self.end_time_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(master, text="Output Video File:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.output_file_entry = ctk.CTkEntry(master)
        self.output_file_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(master, text="Browse", command=self.browse_output_file).grid(row=3, column=2, padx=5, pady=5)

        # --- Trim Button ---
        ctk.CTkButton(master, text="Trim Video", command=self.trim_video).grid(row=4, column=1, padx=5, pady=10)

        # --- Configure grid weights ---
        master.grid_columnconfigure(1, weight=1)


    def browse_input_file(self):
        file_path = tk.filedialog.askopenfilename(initialdir=os.getcwd(), title="Select Input Video", 
                                                filetypes=(("Video Files", "*.mp4;*.avi;*.mkv"), ("All Files", "*.*")))
        self.input_file_entry.delete(0, tk.END)
        self.input_file_entry.insert(0, file_path)

    def browse_output_file(self):
        file_path = tk.filedialog.asksaveasfilename(initialdir=os.getcwd(), title="Select Output Video",
                                                 defaultextension=".mp4", filetypes=(("MP4 Files", "*.mp4"), ("All Files", "*.*")))
        self.output_file_entry.delete(0, tk.END)
        self.output_file_entry.insert(0, file_path)

    def trim_video(self):
        input_file = self.input_file_entry.get()
        start_time = float(self.start_time_entry.get())
        end_time = float(self.end_time_entry.get())
        output_file = self.output_file_entry.get()

        if not input_file or not start_time or not end_time or not output_file:
            CTkMessagebox(title="Error", message="Please fill in all fields.", icon="cancel")
            return

        cap = cv2.VideoCapture(input_file)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        start_frame = int(start_time * fps)
        end_frame = int(end_time * fps)

        if start_frame < 0 or start_frame >= frame_count or end_frame < 0 or end_frame >= frame_count or start_frame >= end_frame:
            CTkMessagebox(title="Error", message="Invalid start or end time.", icon="cancel")
            return

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_file, fourcc, fps, (int(cap.get(3)), int(cap.get(4))))

        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

        while cap.isOpened() and int(cap.get(cv2.CAP_PROP_POS_FRAMES)) < end_frame:
            ret, frame = cap.read()
            if ret:
                out.write(frame)
            else:
                break

        cap.release()
        out.release()

        CTkMessagebox(message="CTkMessagebox is successfully installed.",
                  icon="check", option_1="Thanks")

root = ctk.CTk()
app = VideoTrimmer(root)
root.mainloop() 
