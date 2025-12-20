import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter.colorchooser import askcolor

class ObjectManagerComponent:
    def __init__(self, parent_frame, regrid_callback):
        self.spheres = []
        self.lights = []
        self.parent_frame = parent_frame
        self.regrid_callback = regrid_callback

    def add_sphere(self):
        sphere_id = len(self.spheres) + 1
        sphere_params = {}
        frame = ttk.LabelFrame(self.parent_frame, text=f"Сфера {sphere_id}")

        row = 0
        ttk.Label(frame, text="Центр (x,y,z мм):").grid(row=row, column=0)
        sphere_params['x'] = ttk.Entry(frame, width=5)
        sphere_params['x'].grid(row=row, column=1)
        sphere_params['x'].insert(0, "-200" if sphere_id == 1 else "200" if sphere_id == 2 else "0")
        sphere_params['y'] = ttk.Entry(frame, width=5)
        sphere_params['y'].grid(row=row, column=2)
        sphere_params['y'].insert(0, "-500" if sphere_id == 1 else "500" if sphere_id == 2 else "0")
        sphere_params['z'] = ttk.Entry(frame, width=5)
        sphere_params['z'].grid(row=row, column=3)
        sphere_params['z'].insert(0, "-200" if sphere_id == 1 else "200" if sphere_id == 2 else "0")
        row += 1

        ttk.Label(frame, text="Радиус (мм):").grid(row=row, column=0)
        sphere_params['r'] = ttk.Entry(frame, width=10)
        sphere_params['r'].grid(row=row, column=1)
        sphere_params['r'].insert(0, "400" if sphere_id == 1 else "250" if sphere_id == 2 else "500")
        row += 1

        ttk.Label(frame, text="Цвет (R,G,B 0-1):").grid(row=row, column=0)
        sphere_params['cr'] = ttk.Entry(frame, width=5)
        sphere_params['cr'].grid(row=row, column=1)
        sphere_params['cr'].insert(0, "1" if sphere_id == 1 else "0" if sphere_id == 2 else "0")
        sphere_params['cg'] = ttk.Entry(frame, width=5)
        sphere_params['cg'].grid(row=row, column=2)
        sphere_params['cg'].insert(0, "0" if sphere_id == 1 else "1" if sphere_id == 2 else "0")
        sphere_params['cb'] = ttk.Entry(frame, width=5)
        sphere_params['cb'].grid(row=row, column=3)
        sphere_params['cb'].insert(0, "0" if sphere_id == 1 else "0" if sphere_id == 2 else "1")
        row += 1

        ttk.Label(frame, text="kd, ks, shininess:").grid(row=row, column=0)
        sphere_params['kd'] = ttk.Entry(frame, width=5)
        sphere_params['kd'].grid(row=row, column=1)
        sphere_params['kd'].insert(0, "0.8")
        sphere_params['ks'] = ttk.Entry(frame, width=5)
        sphere_params['ks'].grid(row=row, column=2)
        sphere_params['ks'].insert(0, "0.5")
        sphere_params['shin'] = ttk.Entry(frame, width=5)
        sphere_params['shin'].grid(row=row, column=3)
        sphere_params['shin'].insert(0, "32")
        row += 1

        ttk.Button(frame, text="Удалить", command=lambda: self.delete_sphere(sphere_params)).grid(row=row, column=0, columnspan=2)
        ttk.Button(frame, text="Выбрать", command=lambda: self.pick_color(sphere_params)).grid(row=row, column=2, columnspan=2)

        self.spheres.append(sphere_params)
        self.regrid_callback()

        return sphere_params

    def delete_sphere(self, params):
        frame = params['x'].master
        index = self.spheres.index(params)
        frame.grid_forget()
        frame.destroy()
        del self.spheres[index]
        self.regrid_callback()

    def add_light(self):
        light_id = len(self.lights) + 1
        light_params = {}
        frame = ttk.LabelFrame(self.parent_frame, text=f"Источник {light_id}")

        row = 0
        ttk.Label(frame, text="Положение (x,y,z мм):").grid(row=row, column=0)
        light_params['x'] = ttk.Entry(frame, width=5)
        light_params['x'].grid(row=row, column=1)
        light_params['x'].insert(0, "2000" if light_id == 1 else "-2000" if light_id == 2 else "0")
        light_params['y'] = ttk.Entry(frame, width=5)
        light_params['y'].grid(row=row, column=2)
        light_params['y'].insert(0, "2000" if light_id == 1 else "2000" if light_id == 2 else "1000")
        light_params['z'] = ttk.Entry(frame, width=5)
        light_params['z'].grid(row=row, column=3)
        light_params['z'].insert(0, "2000" if light_id == 1 else "0" if light_id == 2 else "1000")
        row += 1

        ttk.Label(frame, text="Цвет (R,G,B 0-1):").grid(row=row, column=0)
        light_params['cr'] = ttk.Entry(frame, width=5)
        light_params['cr'].grid(row=row, column=1)
        light_params['cr'].insert(0, "1")
        light_params['cg'] = ttk.Entry(frame, width=5)
        light_params['cg'].grid(row=row, column=2)
        light_params['cg'].insert(0, "1")
        light_params['cb'] = ttk.Entry(frame, width=5)
        light_params['cb'].grid(row=row, column=3)
        light_params['cb'].insert(0, "1")
        row += 1

        ttk.Label(frame, text="I0 (Вт/ср):").grid(row=row, column=0)
        light_params['i0'] = ttk.Entry(frame, width=10)
        light_params['i0'].grid(row=row, column=1)
        light_params['i0'].insert(0, "10000")
        row += 1

        ttk.Button(frame, text="Удалить", command=lambda: self.delete_light(light_params)).grid(row=row, column=0, columnspan=2)
        ttk.Button(frame, text="Выбрать", command=lambda: self.pick_color(light_params)).grid(row=row, column=2, columnspan=2)

        self.lights.append(light_params)
        self.regrid_callback()

        return light_params

    def delete_light(self, params):
        frame = params['x'].master
        index = self.lights.index(params)
        frame.grid_forget()
        frame.destroy()
        del self.lights[index]
        self.regrid_callback()

    def pick_color(self, params):
        color = askcolor(title="Выберите цвет")
        if color[1] is not None:
            r, g, b = color[0]
            params['cr'].delete(0, tk.END)
            params['cr'].insert(0, str(r / 255.0))
            params['cg'].delete(0, tk.END)
            params['cg'].insert(0, str(g / 255.0))
            params['cb'].delete(0, tk.END)
            params['cb'].insert(0, str(b / 255.0))

    def get_spheres(self):
        spheres_list = []
        for sphere in self.spheres:
            s = {
                'center': np.array([float(sphere['x'].get()), float(sphere['y'].get()), float(sphere['z'].get())]),
                'radius': float(sphere['r'].get()),
                'color': np.array([float(sphere['cr'].get()), float(sphere['cg'].get()), float(sphere['cb'].get())]),
                'kd': float(sphere['kd'].get()),
                'ks': float(sphere['ks'].get()),
                'shin': float(sphere['shin'].get())
            }
            spheres_list.append(s)
        return spheres_list

    def get_lights(self):
        lights_list = []
        for light in self.lights:
            l = {
                'pos': np.array([float(light['x'].get()), float(light['y'].get()), float(light['z'].get())]),
                'color': np.array([float(light['cr'].get()), float(light['cg'].get()), float(light['cb'].get())]),
                'i0': float(light['i0'].get())
            }
            lights_list.append(l)
        return lights_list
