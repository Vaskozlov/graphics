import numpy as np

def ray_sphere_intersection_np(ray_origin, ray_dir, center, radius):
    oc = ray_origin - center
    b = np.sum(ray_dir * oc, axis=-1)
    c = np.sum(oc * oc, axis=-1) - radius * radius
    h = b * b - c
    hit = h >= 0.0
    t = -b - np.sqrt(np.maximum(h, 0.0))
    return hit, t


def compute_brightness(params):
    H, W = params["H"], params["W"]
    Hres, Wres = params["Hres"], params["Wres"]

    xC, yC, zC = params["sphere_center"]
    R = params["sphere_radius"]
    zO = params["observer_z"]
    I0 = params["I0"]
    k_diff = params["k_diff"]
    k_spec = params["k_spec"]
    shininess = params["shininess"]
    lights = params["light_sources"]
    perspective = params["perspective"]

    xs = np.linspace(-W / 2.0, W / 2.0, Wres)
    ys = np.linspace(-H / 2.0, H / 2.0, Hres)
    xv, yv = np.meshgrid(xs, ys, indexing="xy") 

    if not perspective:
        dx = xv - xC
        dy = yv - yC
        inside = dx * dx + dy * dy <= R * R
        img = np.zeros((Hres, Wres), dtype=np.float32)
        
        # если все за пределами или источников нет возвращаем сразу нули
        if not np.any(inside) or len(lights) == 0:
            return img

        # координата z на сфере
        z_sphere = zC + np.sqrt(np.maximum(R * R - dx * dx - dy * dy, 0.0))
        
        # вектор нормали
        nx = (xv - xC) / R
        ny = (yv - yC) / R
        nz = (z_sphere - zC) / R

        # формируем вектора нормалей
        N = np.stack([nx, ny, nz], axis=-1)[..., None, :]

        # вектор взгляда
        V = np.stack([np.zeros_like(xv), np.zeros_like(yv), zO - z_sphere], axis=-1)
        V /= np.linalg.norm(V, axis=-1, keepdims=True)

        # массив векторов вида (x, y, z) с координатами источников света
        lights_arr = np.array(lights, dtype=np.float32) 
        
        # формируем вектор от точки P (точка на сфере) к источнику 
        Lvec = lights_arr[None, None, :, :] - np.stack(
            [xv[..., None], yv[..., None], z_sphere[..., None]], axis=-1
        )
        
        Lnorm = np.linalg.norm(Lvec, axis=-1, keepdims=True)
        
        # избегаем деления на 0
        Ldir = Lvec / np.maximum(Lnorm, 1e-9)

        # рассчитываем диффузию в каждой точке от каждого источника
        # векторное произведение представили в виде суммы произведения компонентов
        diff = np.maximum(np.sum(N * Ldir, axis=-1), 0.0) 

        Vtile = V[..., None, :]
        
        # рассчитываем полувектор
        Hvec = Ldir + Vtile
        Hvec /= np.maximum(np.linalg.norm(Hvec, axis=-1, keepdims=True), 1e-9)
        
        # рассчитываем спектральную составляющую в каждой точке от каждого источника
        # векторное произведение представили в виде суммы произведения компонентов
        spec = np.maximum(np.sum(N * Hvec, axis=-1), 0.0) ** shininess  

        # для каждого источника вычисляем яркость и суммируем
        # яркость считается по модели Блинна-Фонга
        total = np.sum(I0 * (k_diff * diff + k_spec * spec), axis=-1)
        img += total
        img[~inside] = 0.0
        
        return img









    cam_origin = np.array([0.0, 0.0, float(zO)], dtype=np.float32)

    px = xv
    py = yv
    pz = np.zeros_like(px)

    dirs = np.stack(
        [px - cam_origin[0], py - cam_origin[1], pz - cam_origin[2]], axis=-1
    )
    dirs /= np.linalg.norm(dirs, axis=-1, keepdims=True)

    cam = np.stack(
        [
            np.full_like(px, cam_origin[0]),
            np.full_like(py, cam_origin[1]),
            np.full_like(pz, cam_origin[2]),
        ],
        axis=-1,
    )

    hit, t = ray_sphere_intersection_np(
        cam, dirs, np.array([xC, yC, zC], dtype=np.float32), R
    )
    
    img = np.zeros((Hres, Wres), dtype=np.float32)
    
    if not np.any(hit):
        return img

    hit_points = cam + dirs * t[..., None]

    nx = (hit_points[..., 0] - xC) / R
    ny = (hit_points[..., 1] - yC) / R
    nz = (hit_points[..., 2] - zC) / R
    N = np.stack([nx, ny, nz], axis=-1)

    V = -dirs
    V /= np.linalg.norm(V, axis=-1, keepdims=True)

    if len(lights) == 0:
        return img

    lights_arr = np.array(lights, dtype=np.float32)
    
    HP = hit_points[..., None, :]
    Lvec = lights_arr[None, None, :, :] - HP
    Lnorm = np.linalg.norm(Lvec, axis=-1, keepdims=True)
    Ldir = Lvec / np.maximum(Lnorm, 1e-9)

    Ntile = N[..., None, :]
    diff = np.maximum(np.sum(Ntile * Ldir, axis=-1), 0.0) 

    Vtile = V[..., None, :]
    Hvec = Ldir + Vtile
    Hvec /= np.maximum(np.linalg.norm(Hvec, axis=-1, keepdims=True), 1e-9)
    spec = np.maximum(np.sum(Ntile * Hvec, axis=-1), 0.0) ** shininess

    total = np.sum(I0 * (k_diff * diff + k_spec * spec), axis=-1)
    img += total
    img[~hit] = 0.0
    return img

