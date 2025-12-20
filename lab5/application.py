import tkinter as tk
from tkinter import ttk
from screen_params import ScreenParamsComponent
from object_manager import ObjectManagerComponent
from renderer import RendererComponent
from image_display import ImageDisplayComponent

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Лабораторная работа 5: Визуализация распределения яркости на сферах с учетом тени и цвета")

        self.input_frame = ttk.Frame(self.root)
        self.input_frame.grid(row=0, column=0, rowspan=30, sticky='ns')

        self.screen_params_comp = ScreenParamsComponent(self.input_frame)

        ttk.Button(self.input_frame, text="Добавить сферу", command=self.add_sphere).grid(row=10, column=0, columnspan=4)
        ttk.Button(self.input_frame, text="Добавить источник", command=self.add_light).grid(row=11, column=0, columnspan=4)

        ttk.Button(self.input_frame, text="Рендерить", command=self.render).grid(row=12, column=0, columnspan=4)
        ttk.Button(self.input_frame, text="Сохранить изображения", command=self.save_images).grid(row=13, column=0, columnspan=4)

        self.canvas = tk.Canvas(self.input_frame)
        self.canvas.grid(row=14, column=0, columnspan=4, sticky='nsew')
        self.scrollbar = ttk.Scrollbar(self.input_frame, orient='vertical', command=self.canvas.yview)
        self.scrollbar.grid(row=14, column=4, sticky='ns')
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.input_frame.rowconfigure(14, weight=1)
        self.input_frame.columnconfigure(0, weight=1)

        self.inner_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor='nw')
        self.inner_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.object_manager = ObjectManagerComponent(self.inner_frame, self.regrid_all)

        self.image_frame = ttk.Frame(self.root)
        self.image_frame.grid(row=0, column=1, sticky='nsew')

        self.image_display = ImageDisplayComponent(self.image_frame, self.resize_images)

        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.image_frame.columnconfigure(0, weight=1)
        self.image_frame.columnconfigure(1, weight=1)
        self.image_frame.rowconfigure(1, weight=1)
        self.image_frame.rowconfigure(3, weight=1)

        self.add_sphere()
        self.add_sphere()
        self.add_light()
        self.add_light()

        self.root.bind("<Configure>", self.on_resize)

        self.root.geometry("1200x800")

        self.renderer = RendererComponent()

        self.root.mainloop()

    def add_sphere(self):
        self.object_manager.add_sphere()

    def add_light(self):
        self.object_manager.add_light()

    def regrid_all(self):
        row = 0
        for params in self.object_manager.spheres:
            frame = params['x'].master
            frame.grid(row=row, column=0, columnspan=4, sticky='ew')
            row += 1
        for params in self.object_manager.lights:
            frame = params['x'].master
            frame.grid(row=row, column=0, columnspan=4, sticky='ew')
            row += 1
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def get_params(self):
        try:
            screen_p = self.screen_params_comp.get_params()
            spheres = self.object_manager.get_spheres()
            lights = self.object_manager.get_lights()
            return screen_p, spheres, lights
        except ValueError as e:
            tk.messagebox.showerror("Ошибка", f"Некорректное значение: {e}")
            raise

    def render(self):
        screen_p, spheres, lights = self.get_params()
        images, view_images = self.renderer.render(screen_p, spheres, lights)
        self.image_display.update_images(images, view_images)

    def resize_images(self):
        self.image_display.resize_images()

    def on_resize(self, event):
        self.resize_images()

    def save_images(self):
        self.image_display.save_images()


if __name__ == "__main__":
    App()