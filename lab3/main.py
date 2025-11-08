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
        label_results.config(text="Invalid input")
        return

    # Generate grid for rectangular area centered at (x0, y0)
    x = np.linspace(x0 - W/2, x0 + W/2, Wres)
    y = np.linspace(y0 - H/2, y0 + H/2, Hres)
    X, Y = np.meshgrid(x, y)

    # Compute illuminance E
    dx = X - xL
    dy = Y - yL
    dz = zL
    r2 = dx**2 + dy**2 + dz**2
    r4 = r2**2
    E = I0 * dz**2 / r4

    # Normalize to 0-255 grayscale for saving
    max_E = np.max(E) if np.max(E) > 0 else 1.0  # Avoid division by zero
    img = (E / max_E * 255).astype(np.uint8)

    # Save image as grayscale
    plt.imsave('illumination.png', img, cmap='gray')

    # Visualize distribution with inferno cmap and colorbar
    fig1.clf()
    ax1 = fig1.add_subplot(111)
    im = ax1.imshow(E, cmap='inferno', extent=[x.min(), x.max(), y.min(), y.max()], origin='lower')
    ax1.set_title('Illumination Distribution')
    ax1.set_xlabel('X (mm)')
    ax1.set_ylabel('Y (mm)')
    cb = fig1.colorbar(im, ax=ax1)
    cb.set_label('Illuminance (W/m²)')
    canvas1.draw()

    # Cross-section graph through center (along X at y closest to y0)
    row = np.argmin(np.abs(y - y0))
    E_line = E[row, :]
    x_line = x
    fig2.clf()
    ax2 = fig2.add_subplot(111)
    ax2.plot(x_line, E_line)
    ax2.set_title('Cross-Section Through Center')
    ax2.set_xlabel('X (mm)')
    ax2.set_ylabel('Illuminance (W/m²)')
    canvas2.draw()

    # Stats within circle
    mask = (X - x0)**2 + (Y - y0)**2 <= R**2
    if np.any(mask):
        E_circle = E[mask]
        max_c = np.max(E_circle)
        min_c = np.min(E_circle)
        avg_c = np.mean(E_circle)
    else:
        max_c = min_c = avg_c = 0.0

    # Exact values at specific points
    def comp_E(xp, yp):
        rp = np.sqrt((xp - xL)**2 + (yp - yL)**2 + zL**2)
        return I0 * zL**2 / rp**4 if rp > 0 else 0.0

    E_center = comp_E(x0, y0)
    E_xp = comp_E(x0 + R, y0)
    E_xm = comp_E(x0 - R, y0)
    E_yp = comp_E(x0, y0 + R)
    E_ym = comp_E(x0, y0 - R)

    # Display results
    text = f"Center: {E_center:.10f}\nX +R: {E_xp:.10f}\nX -R: {E_xm:.10f}\nY +R: {E_yp:.10f}\nY -R: {E_ym:.10f}\nMax in circle: {max_c:.10f}\nMin in circle: {min_c:.10f}\nAvg in circle: {avg_c:.10f}"
    label_results.config(text=text)

# GUI setup
root = tk.Tk()
root.title("Illumination Calculator")

frame = ttk.Frame(root)
frame.pack(pady=10)

# Parameter inputs with defaults
labels = ["W (mm):", "H (mm):", "Wres (pixels):", "Hres (pixels):", "xL (mm):", "yL (mm):", "zL (mm):", "I0 (W/sr):", "x0 (mm):", "y0 (mm):", "R (mm):"]
defaults = ["2000", "2000", "400", "400", "0", "0", "1000", "1000", "0", "0", "800"]
entries = []

for i, label in enumerate(labels):
    ttk.Label(frame, text=label).grid(row=i, column=0, sticky="w")
    entry = ttk.Entry(frame)
    entry.grid(row=i, column=1)
    entry.insert(0, defaults[i])
    entries.append(entry)

entry_W, entry_H, entry_Wres, entry_Hres, entry_xL, entry_yL, entry_zL, entry_I0, entry_x0, entry_y0, entry_R = entries

ttk.Button(frame, text="Compute", command=compute_illum).grid(row=11, column=0, columnspan=2, pady=10)

# Results display
label_results = ttk.Label(root, text="", justify="left")
label_results.pack(pady=10)

# Matplotlib canvases
fig1 = plt.Figure(figsize=(5, 4))
canvas1 = FigureCanvasTkAgg(fig1, root)
canvas1.get_tk_widget().pack(side="left", padx=10)

fig2 = plt.Figure(figsize=(5, 4))
canvas2 = FigureCanvasTkAgg(fig2, root)
canvas2.get_tk_widget().pack(side="right", padx=10)

root.mainloop()