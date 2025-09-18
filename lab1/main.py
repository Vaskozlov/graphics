import os
import PIL
import tkinter as tk
import numpy as np
from PIL import ImageTk
import matplotlib.pyplot as plt

class Application(tk.Tk):
    def __init__(self, width: int, height: int, title: str, images_path: tuple):
        super().__init__()
        
        self.title(title)
        self.geometry(f'{width}x{height}')
        
        self.image_index = 0
        self.images_path = images_path
        
        # reading raw images
        self.raw_images = [PIL.Image.open(path) for path in images_path]
        
        # resizing images, so than they can fit on the screen
        self.raw_images = [self.resize_image(image, (600, 400)) for image in self.raw_images]

        # converting images to np.array, so we can easily compute sum of colors by channels
        self.images_data = [np.array(image.convert('RGBA')) for image in self.raw_images]
        
        # converting images to tkinter format
        self.tk_images = [ImageTk.PhotoImage(image) for image in self.raw_images]
    
        self.draw_buttons()
        
        self.label = tk.Label(self, image=self.tk_images[self.image_index])
        self.label.pack(anchor='ne')
        
    def resize_image(self, image: PIL.Image, preferred_size: tuple) -> PIL.Image:
        w, h = image.size
        
        # first we try to resize image to the destination width
        preferred_width = np.round(preferred_size[0])
        preferred_height = np.round(h * preferred_width / w)
        
        # if resulted height is too big we resize image to destination height
        if preferred_height > preferred_size[1]:
            preferred_height = preferred_size[1]
            preferred_width = np.round(w * preferred_height / h)
        
        return image.resize((int(preferred_width), int(preferred_height)))
        
    def draw_buttons(self) -> None:
        tk.Button(
            self,
            width=25,
            text="Show sum of colors by channels",
            command= lambda : self.show_color_bars()
        ).pack(anchor='nw', pady=5)
        
        for i in range(len(self.tk_images)):
            tk.Button(
                self,
                width=25,
                text=self.images_path[i],
                command= lambda i=i : self.draw_image(i)
            ).pack(anchor='nw', pady=5)
            
    def draw_image(self, index) -> None:
        self.image_index = index
        self.label.configure(image=self.tk_images[index])
        
    def show_color_bars(self) -> None:
        img = self.images_data[self.image_index]
        
        # img is a multi-dimensional array, last index corresponds to the image's color channel
        pixels_sum = [np.sum(img[:, :, i]) for i in range(3)]
        
        bar_names = ['red', 'green', 'blue']
        bar_colors = ['red', 'green', 'blue']
        
        x_label = f'r: {pixels_sum[0]}, g: {pixels_sum[1]}, b: {pixels_sum[2]}'
        print(x_label)
        
        plt.close('all') # close all windows, so one image does not get stuck (optional)
        plt.bar(bar_names, pixels_sum, color=bar_colors)
        
        plt.xlabel(x_label)
        plt.ylabel('Pixels of colors by channels')
        
        plt.show()
            
if __name__ == "__main__":
    if not os.path.exists("./images/forest.png"):
        print('Program must be launched from ./lab1 directory')
        exit(1)
    
    application = Application(
        width=800,
        height=600,
        title='Lab1 application',
        images_path=["images/forest.png", "images/forest2.jpg", "images/image.png"]
    )
    
    application.mainloop()