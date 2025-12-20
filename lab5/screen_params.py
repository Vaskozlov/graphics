import tkinter as tk
from tkinter import ttk

class ScreenParamsComponent:
    def __init__(self, parent_frame):
        self.screen_params = {}
        self.create_inputs(parent_frame)

    def create_inputs(self, parent_frame):
        row = 0
        ttk.Label(parent_frame, text="Ширина экрана (мм):").grid(row=row, column=0)
        self.screen_params['w_mm'] = ttk.Entry(parent_frame, width=10)
        self.screen_params['w_mm'].grid(row=row, column=1)
        self.screen_params['w_mm'].insert(0, "2000")
        row += 1

        ttk.Label(parent_frame, text="Высота экрана (мм):").grid(row=row, column=0)
        self.screen_params['h_mm'] = ttk.Entry(parent_frame, width=10)
        self.screen_params['h_mm'].grid(row=row, column=1)
        self.screen_params['h_mm'].insert(0, "2000")
        row += 1

        ttk.Label(parent_frame, text="Разрешение по ширине:").grid(row=row, column=0)
        self.screen_params['w_res'] = ttk.Entry(parent_frame, width=10)
        self.screen_params['w_res'].grid(row=row, column=1)
        self.screen_params['w_res'].insert(0, "600")
        row += 1

        ttk.Label(parent_frame, text="Разрешение по высоте:").grid(row=row, column=0)
        self.screen_params['h_res'] = ttk.Entry(parent_frame, width=10)
        self.screen_params['h_res'].grid(row=row, column=1)
        self.screen_params['h_res'].insert(0, "600")
        row += 1

        ttk.Label(parent_frame, text="Расстояние наблюдателя (мм):").grid(row=row, column=0)
        self.screen_params['zo'] = ttk.Entry(parent_frame, width=10)
        self.screen_params['zo'].grid(row=row, column=1)
        self.screen_params['zo'].insert(0, "1800")

    def get_params(self):
        return {key: float(entry.get()) for key, entry in self.screen_params.items()}
