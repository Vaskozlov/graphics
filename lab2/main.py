import os
import PIL
import tkinter as tk
import numpy as np
from tkinter import filedialog, messagebox
from PIL import ImageTk
from PIL import ImageFilter
import matplotlib.pyplot as plt

class Application(tk.Tk):
    def __init__(self, width: int, height: int, title: str, images_path: tuple):
        super().__init__()
        
        self.title(title)
        self.geometry(f'{width}x{height}')
        
        self.image_index = 0
        self.images_path = images_path
        
        self.grayscale = False
        self.inverted = False
        self.blurred = False
        self.brightness = 0.0
        self.contrast = 1.0
        
        # reading raw images
        self.raw_images = [PIL.Image.open(path) for path in images_path]
        
        # resizing images, so than they can fit on the screen
        self.raw_images = [self.resize_image(image, (480, 320)) for image in self.raw_images]
        self.modified_images = [im.copy() for im in self.raw_images]

        # converting images to np.array, so we can easily compute mean of colors by channels
        self.images_data = [np.array(image.convert('RGBA')) for image in self.raw_images]
        
        # converting images to tkinter format
        self.tk_images = [ImageTk.PhotoImage(image) for image in self.raw_images]
        self.tk_images_proc = [ImageTk.PhotoImage(image) for image in self.modified_images]
    
        self.draw_buttons()
        
        self.label = tk.Label(self, image=self.tk_images[self.image_index])
        self.label.place(x=10, y=200)
        
        self.label_proc = tk.Label(self, image=self.tk_images_proc[self.image_index])
        self.label_proc.place(x=500, y=200)
        
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
        y_value = 5
        y_change = 30
        x_position = 10
        
        tk.Button(
            self,
            width=25,
            text="Show hist",
            command= lambda : self.show_histogram()
        ).place(x=x_position, y=y_value)
        
        y_value += y_change
        
        for i in range(len(self.tk_images)):
            tk.Button(
                self,
                width=25,
                text=self.images_path[i],
                command= lambda i=i : self.draw_image(i)
            ).place(x=x_position, y=y_value)
            
            y_value += y_change
        
        tk.Button(
                self,
                width=25,
                text="Download",
                command = self.download_image
            ).place(x=x_position, y=y_value)
        
        
        y_value = 5
        y_change = 30
        x_position = 200
        
        tk.Button(
                self,
                width=25,
                text="Увеличить контраст",
                command = lambda i=i : self.adjust_contrast(0.5)
            ).place(x=x_position, y=y_value)
        
        y_value += y_change
        
        tk.Button(
                self,
                width=25,
                text="Уменьшить контраст",
                command = lambda i=i : self.adjust_contrast(-0.5)
            ).place(x=x_position, y=y_value)
        
        y_value += y_change
        
        tk.Button(
                self,
                width=25,
                text="Увеличить яркость",
                command = lambda i=i : self.adjust_brightness(10)
            ).place(x=x_position, y=y_value)
        
        y_value += y_change
        
        tk.Button(
                self,
                width=25,
                text="Уменьшить яркость",
                command = lambda i=i : self.adjust_brightness(-10)
            ).place(x=x_position, y=y_value)
        
        y_value += y_change
        
        tk.Button(
                self,
                width=25,
                text="Инвертировать",
                command = lambda i=i : self.invert_colors()
            ).place(x=x_position, y=y_value)
        
        y_value += y_change
        
        tk.Button(
                self,
                width=25,
                text="Размытие",
                command = lambda i=i : self.apply_blur()
            ).place(x=x_position, y=y_value)
        
        y_value += y_change
            
    def draw_image(self, index) -> None:
        self.image_index = index
        self.label.configure(image=self.tk_images[index])
        self.label_proc.configure(image=self.tk_images_proc[index])
        self.label_proc.image = self.tk_images_proc[index]
        
    def show_color_bars(self) -> None:
        img = self.images_data[self.image_index]
        
        # img is a multi-dimensional array, last index corresponds to the image's color channel
        pixels_mean = [np.mean(img[:, :, i]) for i in range(3)]
        
        bar_names = ['red', 'green', 'blue']
        bar_colors = ['red', 'green', 'blue']
        
        x_label = f'r: {pixels_mean[0]:.2f}, g: {pixels_mean[1]:.2f}, b: {pixels_mean[2]:.2f}'
        print(x_label)
        
        plt.close('all') # close all windows, so one image does not get stuck (optional)
        plt.bar(bar_names, pixels_mean, color=bar_colors)
        
        plt.xlabel(x_label)
        plt.ylabel('Mean per-channel color')
        
        plt.show()
            
        
    def adjust_brightness_contrast(self, image, brightness, contrast):
        img_array = np.array(image, dtype=np.float32)
        
        img_array[:, :, :3] = (img_array[:, :, :3] - 127.5) * contrast + 127.5
        img_array[:, :, :3] += brightness
        img_array[:, :, :3] = np.clip(img_array[:, :, :3], 0, 255)
        
        return PIL.Image.fromarray(img_array.astype(np.uint8))
    
    def apply_invert(self, image):
        img_array = np.array(image)
        img_array = 255 - img_array
        
        return PIL.Image.fromarray(img_array.astype(np.uint8))
    
    def apply_processing(self):
        processed_image = self.raw_images[self.image_index].copy()
        
        if self.grayscale:
            processed_image = processed_image.convert('L').convert('RGBA')
        
        if self.inverted:
            processed_image = self.apply_invert(processed_image)
        
        if self.blurred:
            processed_image = processed_image.convert('RGBA').filter(PIL.ImageFilter.BLUR)
        
        if self.brightness != 0 or self.contrast != 1.0:
            processed_image = self.adjust_brightness_contrast(
                processed_image.convert('RGBA'), self.brightness, self.contrast
            )
        
        self.modified_images[self.image_index] = processed_image
        self.tk_images_proc[self.image_index] = ImageTk.PhotoImage(processed_image)
        
        self.draw_image(self.image_index)
    
    def convert_grayscale(self):
        self.grayscale = not self.grayscale
        self.apply_processing()
    
    def invert_colors(self):
        self.inverted = not self.inverted
        self.apply_processing()
        
    def apply_blur(self):
        self.blurred = not self.blurred
        self.apply_processing()
        
    def adjust_brightness(self, value):
        """Изменение яркости"""
        self.brightness += value
        self.apply_processing()
    
    def adjust_contrast(self, value):
        """Изменение контраста"""
        self.contrast += value
        self.contrast = max(0.1, self.contrast)  # Минимальный контраст 0.1
        self.apply_processing()
        
    def show_histogram(self):
        """Show RGB histogram"""
        if hasattr(self, 'modified_images') and self.modified_images[self.image_index]:
            img_array = np.array(self.modified_images[self.image_index].convert("RGB"))
            
            # Create histogram window
            hist_window = tk.Toplevel(self)
            hist_window.title("Гистограмма цветовых каналов")
            hist_window.geometry("600x400")
            
            fig, ax = plt.subplots(figsize=(6, 4))
            
            colors = ['red', 'green', 'blue']
            channels = ['R', 'G', 'B']
            
            for i, color in enumerate(colors):
                hist_data = img_array[:, :, i].flatten()
                ax.hist(hist_data, bins=64, range=(0, 255), 
                       color=color, alpha=0.7, label=channels[i])
            
            ax.set_xlim(0, 255)
            ax.set_xlabel('Уровень насыщенности')
            ax.set_ylabel('Частота')
            ax.set_title('Гистограмма цветовых каналов')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # Embed in tkinter
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            canvas = FigureCanvasTkAgg(fig, hist_window)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
    def download_image(self):
        """Скачивание обработанного изображения"""
        
        file_path = tk.filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        
        processed_image = self.modified_images[self.image_index]
        
        if file_path:
            try:
                processed_image.save(file_path)
            except Exception as e:
                tk.messagebox.showerror("Ошибка", f"Не удалось сохранить изображение: {str(e)}")
    
if __name__ == "__main__":
    # if not os.path.exists("./images/forest.png"):
    #     print('Program must be launched from ./lab1 directory')
    #     exit(1)
    
    application = Application(
        width=900,
        height=600,
        title='Lab1 application',
        images_path=["lab2/images/forest.png", "lab2/images/forest2.jpg", "lab2/images/image.png"]
    )
    
    application.mainloop()