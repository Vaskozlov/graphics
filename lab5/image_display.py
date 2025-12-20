import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class ImageDisplayComponent:
    def __init__(self, parent_frame, resize_callback):
        self.labels = self.create_labels(parent_frame)
        self.images = {}
        self.view_images = {}
        self.prev_width = 0
        self.prev_height = 0
        self.resize_callback = resize_callback

    def create_labels(self, parent_frame):
        ttk.Label(parent_frame, text="Вид спереди:").grid(row=0, column=0, sticky='ew')
        label_front = ttk.Label(parent_frame)
        label_front.grid(row=1, column=0, sticky='nsew')

        ttk.Label(parent_frame, text="Вид сбоку (x+):").grid(row=0, column=1, sticky='ew')
        label_side1 = ttk.Label(parent_frame)
        label_side1.grid(row=1, column=1, sticky='nsew')

        ttk.Label(parent_frame, text="Вид сверху:").grid(row=2, column=0, sticky='ew')
        label_top = ttk.Label(parent_frame)
        label_top.grid(row=3, column=0, sticky='nsew')

        ttk.Label(parent_frame, text="Вид сбоку (x-):").grid(row=2, column=1, sticky='ew')
        label_side2 = ttk.Label(parent_frame)
        label_side2.grid(row=3, column=1, sticky='nsew')

        return {
            'front': label_front,
            'side1': label_side1,
            'top': label_top,
            'side2': label_side2
        }

    def update_images(self, images, view_images):
        self.images = images
        self.view_images = view_images
        self.prev_width = 0
        self.prev_height = 0
        self.resize_images()

    def resize_images(self):
        if not self.view_images:
            return

        front_width = self.labels['front'].winfo_width()
        front_height = self.labels['front'].winfo_height()
        if front_width <= 1 or front_height <= 1:
            return

        if front_width == self.prev_width and front_height == self.prev_height:
            return

        self.prev_width = front_width
        self.prev_height = front_height

        side_length = min(front_width, front_height)

        for view_name, pil_image in self.view_images.items():
            resized = pil_image.resize((side_length, side_length), Image.LANCZOS)
            photo = ImageTk.PhotoImage(resized)
            self.labels[view_name].config(image=photo)
            self.labels[view_name].image = photo

    def save_images(self):
        for view_name, img in self.images.items():
            img.save(f"{view_name}.png")

