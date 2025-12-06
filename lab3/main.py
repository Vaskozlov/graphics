import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def compute_illum():
    try:
        W = float(entry_W.get())
        H = float(entry_H.get())
        Wres = int(entry_Wres.get())
        Hres = int(entry_Hres.get())
        xL = float(entry_xL.get())
        yL = float(entry_yL.get())
        zL = float(entry_zL.get())
        I0 = float(entry_I0.get())
        x0 = float(entry_x0.get())
        y0 = float(entry_y0.get())
        R = float(entry_R.get())
    except ValueError:
        label_results.config(text="Некорректный ввод")
        return

    # Adjust Hres to ensure square pixels (same physical size in mm per pixel)
    if W > 0:
        pixel_size_x = W / Wres
        desired_Hres = int(H / pixel_size_x + 0.5)
        if desired_Hres != Hres:
            Hres = desired_Hres
            entry_Hres.delete(0, tk.END)
            entry_Hres.insert(0, str(Hres))

    x = np.linspace(x0 - W/2, x0 + W/2, Wres)
    y = np.linspace(y0 - H/2, y0 + H/2, Hres)
    X, Y = np.meshgrid(x, y)

    dx = X - xL
    dy = Y - yL
    dz = zL
    r2 = dx**2 + dy**2 + dz**2
    r4 = r2**2
    E = I0 * dz**2 / r4

    mask = (X - x0)**2 + (Y - y0)**2 <= R**2
    E[~mask] = 0.0

    max_E = np.max(E) if np.max(E) > 0 else 1.0 
    img = (E / max_E * 255).astype(np.uint8)

    plt.imsave('illumination.png', img, cmap='gray')

    fig1.clf()
    ax1 = fig1.add_subplot(111)
    im = ax1.imshow(E, cmap='gray', extent=[x.min(), x.max(), y.min(), y.max()], origin='lower')
    ax1.set_aspect('auto')
    ax1.set_title('Распределение освещенности')
    ax1.set_xlabel('X (мм)')
    ax1.set_ylabel('Y (мм)')
    cb = fig1.colorbar(im, ax=ax1)
    cb.set_label('Освещенность (Вт/м²)')
    canvas1.draw()

    fig2.clf()

    row = np.argmin(np.abs(y - y0))
    E_line_horizontal = E[row, :]
    x_line = x
    ax2_horizontal = fig2.add_subplot(211)
    ax2_horizontal.plot(x_line, E_line_horizontal)
    ax2_horizontal.set_title('Горизонтальное сечение (по X)')
    ax2_horizontal.set_xlabel('X (мм)')
    ax2_horizontal.set_ylabel('Освещенность (Вт/м²)')

    col = np.argmin(np.abs(x - x0))
    E_line_vertical = E[:, col]
    y_line = y
    ax2_vertical = fig2.add_subplot(212)
    ax2_vertical.plot(y_line, E_line_vertical)
    ax2_vertical.set_title('Вертикальное сечение (по Y)')
    ax2_vertical.set_xlabel('Y (мм)')
    ax2_vertical.set_ylabel('Освещенность (Вт/м²)')

    fig2.tight_layout()
    canvas2.draw()

    fig2.savefig('cross_section.png')

    
    if np.any(mask):
        E_circle = E[mask]
        max_c = np.max(E_circle)
        min_c = np.min(E_circle)
        avg_c = np.mean(E_circle)
    else:
        max_c = min_c = avg_c = 0.0

    def comp_E(xp, yp):
        rp = np.sqrt((xp - xL)**2 + (yp - yL)**2 + zL**2)
        return I0 * zL**2 / rp**4 if rp > 0 else 0.0

    E_center = comp_E(x0, y0)
    E_xp = comp_E(x0 + R, y0)
    E_xm = comp_E(x0 - R, y0)
    E_yp = comp_E(x0, y0 + R)
    E_ym = comp_E(x0, y0 - R)

    text = f"Центр: {E_center:.10f} Вт/м²\nX +R: {E_xp:.10f} Вт/м²\nX -R: {E_xm:.10f} Вт/м²\nY +R: {E_yp:.10f} Вт/м²\nY -R: {E_ym:.10f} Вт/м²\nМакс. в круге: {max_c:.10f} Вт/м²\nМин. в круге: {min_c:.10f} Вт/м²\nСред. в круге: {avg_c:.10f} Вт/м²"
    label_results.config(text=text)

root = tk.Tk()
root.title("Калькулятор освещенности")

frame = ttk.Frame(root)
frame.pack(pady=10)

labels = ["W (мм):", "H (мм):", "Wres (пикс.):", "Hres (пикс.):", "xL (мм):", "yL (мм):", "zL (мм):", "I0 (Вт/ср):", "x0 (мм):", "y0 (мм):", "R (мм):"]
defaults = ["2000", "2000", "400", "400", "0", "0", "1000", "1000", "0", "0", "800"]
entries = []

for i, label in enumerate(labels):
    ttk.Label(frame, text=label).grid(row=i, column=0, sticky="w")
    entry = ttk.Entry(frame)
    entry.grid(row=i, column=1)
    entry.insert(0, defaults[i])
    entries.append(entry)

entry_W, entry_H, entry_Wres, entry_Hres, entry_xL, entry_yL, entry_zL, entry_I0, entry_x0, entry_y0, entry_R = entries

ttk.Button(frame, text="Вычислить", command=compute_illum).grid(row=11, column=0, columnspan=2, pady=10)

label_results = ttk.Label(root, text="", justify="left")
label_results.pack(pady=10)

fig1 = plt.Figure(figsize=(5, 5))
canvas1 = FigureCanvasTkAgg(fig1, root)
canvas1.get_tk_widget().pack(side="left", padx=10)

fig2 = plt.Figure(figsize=(5, 5))
canvas2 = FigureCanvasTkAgg(fig2, root)
canvas2.get_tk_widget().pack(side="right", padx=10)

root.mainloop()