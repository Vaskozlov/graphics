#!/usr/bin/env python3

import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
from calc import *

class BrightnessApp:
    def __init__(self, root):
        self.root = root
        root.title("Яркость на сфере")

        main_frame = ttk.Frame(root)
        main_frame.pack(fill="both", expand=True, padx=4, pady=4)

        self.frame = ttk.Frame(main_frame)
        self.frame.pack(side="left", fill="y", padx=4, pady=4)

        self.fields = {}
        self._add_field("H", "Высота экрана H (мм)", 500)
        self._add_field("W", "Ширина экрана W (мм)", 500)
        self._add_field("Hres", "Разрешение по Y Hres (пикс)", 360)
        self._add_field("Wres", "Разрешение по X Wres (пикс)", 360)
        self._add_field("I0", "I0 (Вт/ср)", 10)
        self._add_field("k_diff", "k_diff", 0.8)
        self._add_field("k_spec", "k_spec", 0.5)
        self._add_field("shininess", "Показатель блеска", 20)

        ttk.Label(self.frame, text="Источники света (x,y,z мм ; ... )").grid(
            row=len(self.fields), column=0, sticky="w"
        )

        self.lights_entry = ttk.Entry(self.frame)
        self.lights_entry.insert(0, "2000,0,2000")
        self.lights_entry.grid(row=len(self.fields), column=1, sticky="ew")
        self.frame.columnconfigure(1, weight=1)

        points_row = len(self.fields) + 1
        ttk.Label(self.frame, text="Точки на экране (x,y мм ; ... )").grid(
            row=points_row, column=0, sticky="w"
        )
        self.points_entry = ttk.Entry(self.frame)
        self.points_entry.insert(0, "0,0; 150,0; -150,0")
        self.points_entry.grid(row=points_row, column=1, sticky="ew")

        check_row = points_row + 1
        self.perspective_var = tk.BooleanVar(value=False)
        # ttk.Checkbutton(
        #     self.frame,
        #     text="Перспектива",
        #     variable=self.perspective_var,
        #     command=self.compute,
        # ).grid(row=check_row, column=0, columnspan=2, sticky="w")

        slider_row = check_row + 1
        slider_frame = ttk.LabelFrame(self.frame, text="Сфера и Камера")
        slider_frame.grid(row=slider_row, column=0, columnspan=2, pady=2, sticky="ew")

        self.sph_x = self._add_slider(slider_frame, "Сфера X (мм)", -2000, 2000, 0)
        self.sph_y = self._add_slider(slider_frame, "Сфера Y (мм)", -2000, 2000, 0)
        self.sph_z = self._add_slider(slider_frame, "Сфера Z (мм)", 100, 4000, 1000)
        self.sph_r = self._add_slider(
            slider_frame, "Радиус сферы R (мм)", 50, 2000, 300
        )

        self.cam_z = self._add_slider(slider_frame, "Камера Z (мм)", 100, 5000, 1500)

        btn_row = slider_row + 1
        btn_frame = ttk.Frame(self.frame)
        btn_frame.grid(row=btn_row, column=0, columnspan=2, pady=2, sticky="w")
        ttk.Button(btn_frame, text="Рассчитать", command=self.compute).pack(
            side="left", padx=2
        )
        ttk.Button(btn_frame, text="Сохранить PNG", command=self.save_png).pack(
            side="left", padx=2
        )

        results_row = btn_row + 1
        self.results_text = tk.Text(self.frame, height=6, width=40, wrap="word")
        self.results_text.grid(
            row=results_row, column=0, columnspan=2, pady=2, sticky="w"
        )

        self.canvas = tk.Canvas(main_frame, bg="black")
        self.canvas.pack(side="right", fill="both", expand=True, padx=4, pady=4)

        self.current_image = None
        self.preview_tk = None
        self.arr = None
        self.params = None

        self.root.bind("<Configure>", self.on_resize)
        self._debounce_id = None
        self.root.after(150, self.auto_update)

    def _add_field(self, key, label, default):
        row = len(self.fields)
        ttk.Label(self.frame, text=label).grid(row=row, column=0, sticky="w")
        entry = ttk.Entry(self.frame, width=10)
        entry.insert(0, str(default))
        entry.grid(row=row, column=1, sticky="ew")
        self.fields[key] = entry

    def _add_slider(self, parent, text, mn, mx, val):
        container = ttk.Frame(parent)
        ttk.Label(container, text=text).pack(anchor="w")
        var = tk.DoubleVar(value=val)
        scale = ttk.Scale(
            container,
            from_=mn,
            to=mx,
            orient="horizontal",
            variable=var,
            command=lambda v: self._debounced_compute(),
        )
        scale.pack(fill="x")
        container.pack(fill="x")
        return var

    def parse_lights(self):
        raw = self.lights_entry.get().strip()
        if not raw:
            return []
        parts = [p.strip() for p in raw.split(";") if p.strip()]
        lights = []
        for p in parts:
            try:
                x, y, z = map(float, p.split(","))
                lights.append((x, y, z))
            except Exception:
                continue
        return lights

    def parse_points(self):
        raw = self.points_entry.get().strip()
        if not raw:
            return []
        parts = [p.strip() for p in raw.split(";") if p.strip()]
        points = []
        for p in parts:
            try:
                x, y = map(float, p.split(","))
                points.append((x, y))
            except Exception:
                continue
        return points

    def auto_update(self):
        self.compute()
        self.root.after(300, self.auto_update)

    def _debounced_compute(self, delay=80):
        if self._debounce_id:
            try:
                self.root.after_cancel(self._debounce_id)
            except Exception:
                pass
        self._debounce_id = self.root.after(delay, self.compute)

    def compute(self):
        try:
            p = {k: float(e.get()) for k, e in self.fields.items()}
            params = {
                "H": p["H"],
                "W": p["W"],
                "Hres": int(max(64, min(1024, int(p["Hres"])))),
                "Wres": int(max(64, min(1024, int(p["Wres"])))),
                "sphere_center": (
                    float(self.sph_x.get()),
                    float(self.sph_y.get()),
                    float(self.sph_z.get()),
                ),
                "sphere_radius": float(self.sph_r.get()),
                "observer_z": float(self.cam_z.get()),
                "I0": p["I0"],
                "k_diff": p["k_diff"],
                "k_spec": p["k_spec"],
                "shininess": p["shininess"],
                "light_sources": self.parse_lights(),
                "perspective": bool(self.perspective_var.get()),
            }

            arr = compute_brightness(params)
            self.arr = arr
            self.params = params

            maxv = float(np.max(arr)) if arr.size else 0.0
            
            if maxv > 0:
                img_u8 = (arr / maxv * 255.0).clip(0, 255).astype(np.uint8)
            else:
                img_u8 = arr.astype(np.uint8)

            self.current_image = Image.fromarray(
                img_u8, mode="L"
            )

            self.display_image()

            minv = np.min(arr[arr > 0]) if np.any(arr > 0) else 0.0
            points = self.parse_points()
            brights = []
            
            for pt in points:
                x, y = pt
                u = ((x + params["W"] / 2.0) / params["W"]) * (params["Wres"] - 1)
                v = ((params["H"] / 2.0 - y) / params["H"]) * (params["Hres"] - 1)
                u_int = int(round(u))
                v_int = int(round(v))
                if (
                    0 <= u_int < params["Wres"]
                    and 0 <= v_int < params["Hres"]
                    and arr[v_int, u_int] > 0
                ):
                    brights.append(arr[v_int, u_int])
                else:
                    brights.append("Неверная точка (за пределами или не на сфере)")

            self.results_text.delete("1.0", tk.END)
            
            info = f"Макс (Вт/ср): {maxv:.4f}\n"
            info += f"Мин (Вт/ср): {minv:.4f}\n"
            
            for i in range(min(3, len(brights))):
                pt_str = ", ".join(f"{c:.1f}" for c in points[i])
            
                if isinstance(brights[i], float):
                    info += f"P{i+1} ({pt_str} мм): {brights[i]:.4f} (Вт/ср)\n"
                else:
                    info += f"P{i+1} ({pt_str} мм): {brights[i]}\n"
            
            self.results_text.insert(tk.END, info)

        except Exception as e:
            print("Ошибка расчёта:", e, file=sys.stderr)

    def display_image(self):
        if self.current_image is None:
            return

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        
        if w <= 1 or h <= 1:
            return

        aspect = self.current_image.width / self.current_image.height
        
        if w / h > aspect:
            new_h = h
            new_w = int(h * aspect)
        else:
            new_w = w
            new_h = int(w / aspect)

        preview = self.current_image.resize((new_w, new_h), resample=Image.BILINEAR)
        self.preview_tk = ImageTk.PhotoImage(preview)
        self.canvas.delete("all")
        self.canvas.create_image(
            (w - new_w) // 2, (h - new_h) // 2, anchor="nw", image=self.preview_tk
        )

    def on_resize(self, event):
        self.display_image()

    def save_png(self):
        if self.current_image is None:
            messagebox.showinfo(
                "Нет изображения", "Пожалуйста, рассчитайте изображение сначала."
            )
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".png", filetypes=[("PNG изображение", "*.png")]
        )
        if not path:
            return
        try:
            self.current_image.save(path, format="PNG")
            messagebox.showinfo("Сохранено", f"Изображение сохранено в:\n{path}")
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = BrightnessApp(root)
    root.mainloop()
