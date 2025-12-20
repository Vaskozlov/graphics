
import os
import numpy as np
from PIL import Image, ImageTk
from multiprocessing import Pool

class RendererComponent:
    def render(self, screen_p, spheres, lights):
        w_mm = screen_p['w_mm']
        h_mm = screen_p['h_mm']
        w_res = int(screen_p['w_res'])
        h_res = int(screen_p['h_res'])
        zo = screen_p['zo']

        if spheres:
            scene_center = np.mean([s['center'] for s in spheres], axis=0)
        else:
            scene_center = np.array([0, 0, 0])

        views = {
            'front': {'eye': scene_center + np.array([0, 0, zo]), 'sx': np.array([1, 0, 0]), 'sy': np.array([0, 1, 0]), 'sc': scene_center},
            'side1': {'eye': scene_center + np.array([zo, 0, 0]), 'sx': np.array([0, 0, 1]), 'sy': np.array([0, 1, 0]), 'sc': scene_center},
            'top': {'eye': scene_center + np.array([0, zo, 0]), 'sx': np.array([1, 0, 0]), 'sy': np.array([0, 0, 1]), 'sc': scene_center},
            'side2': {'eye': scene_center + np.array([-zo, 0, 0]), 'sx': np.array([0, 0, -1]), 'sy': np.array([0, 1, 0]), 'sc': scene_center}
        }

        view_images = {}
        images = {}
        
        for view_name, view in views.items():
            image = self.render_view(w_mm, h_mm, w_res, h_res, view, spheres, lights)
            pil_image = Image.fromarray(image)
            images[view_name] = pil_image
            view_images[view_name] = pil_image
            
        return images, view_images

    def render_view(self, w_mm, h_mm, w_res, h_res, view, spheres, lights):
        image = np.zeros((h_res, w_res, 3), dtype=np.float32)
        eye = view['eye']
        sx = view['sx']
        sy = view['sy']
        sc = view['sc']

        pixel_w = w_mm / w_res
        pixel_h = h_mm / h_res

        args = [(i, j, eye, sx, sy, sc, pixel_w, pixel_h, w_res, h_res, spheres, lights) for i in range(h_res) for j in range(w_res)]

        num_processes = os.cpu_count()
        chunksize = max(1, len(args) // num_processes)

        with Pool(processes=num_processes) as pool:
            results = pool.starmap(self.compute_pixel, args, chunksize=chunksize)

        idx = 0
        for i in range(h_res):
            for j in range(w_res):
                image[i, j] = results[idx]
                idx += 1

        image = self.normalize_image(image)
        return image

    def compute_pixel(self, i, j, eye, sx, sy, sc, pixel_w, pixel_h, w_res, h_res, spheres, lights):
        ray_dir = self.compute_ray_direction(i, j, w_res, h_res, pixel_w, pixel_h, sc, sx, sy, eye)
        if ray_dir is None:
            return np.zeros(3)

        hit_sphere_idx, min_t = self.find_closest_intersection(eye, ray_dir, spheres)
        
        if hit_sphere_idx is not None:
            hit_point = eye + min_t * ray_dir
            sphere = spheres[hit_sphere_idx]
            normal = (hit_point - sphere['center']) / sphere['radius']
            view_dir = -ray_dir
            return self.compute_lighting(hit_point, normal, view_dir, sphere, lights, spheres, hit_sphere_idx)
        
        return np.zeros(3)

    def compute_ray_direction(self, i, j, w_res, h_res, pixel_w, pixel_h, sc, sx, sy, eye):
        px = (j - w_res / 2 + 0.5) * pixel_w
        py = -(i - h_res / 2 + 0.5) * pixel_h
        pixel_pos = sc + px * sx + py * sy
        ray_dir = pixel_pos - eye
        ray_norm = np.linalg.norm(ray_dir)
        
        if ray_norm == 0:
            return None
        
        return ray_dir / ray_norm

    def find_closest_intersection(self, eye, ray_dir, spheres):
        min_t = np.inf
        hit_sphere_idx = None
        
        for idx, sphere in enumerate(spheres):
            t = self.ray_sphere_intersect(eye, ray_dir, sphere['center'], sphere['radius'])
            if 0 < t < min_t:
                min_t = t
                hit_sphere_idx = idx
                
        return hit_sphere_idx, min_t

    def compute_lighting(self, hit_point, normal, view_dir, sphere, lights, spheres, hit_sphere_idx):
        color = np.zeros(3)
        
        for light in lights:
            visibility, light_dir, dist_sample = self.compute_visibility_and_direction(hit_point, normal, light, spheres, hit_sphere_idx)
            
            if visibility == 0:
                continue

            diffuse = sphere['kd'] * max(0, np.dot(normal, light_dir))
            h = light_dir + view_dir
            h_norm = np.linalg.norm(h)
            
            if h_norm > 0:
                h /= h_norm
            
            specular = sphere['ks'] * max(0, np.dot(normal, h)) ** sphere['shin']
            atten = light['i0'] / (dist_sample ** 2 + 1)
            light_contrib = light['color'] * atten * visibility
            color += sphere['color'] * light_contrib * diffuse + light_contrib * specular
            
        return color

    def compute_visibility_and_direction(self, hit_point, normal, light, spheres, hit_sphere_idx):
        return self.compute_point_light_visibility(hit_point, normal, light, spheres, hit_sphere_idx)

    def compute_point_light_visibility(self, hit_point, normal, light, spheres, hit_sphere_idx):
        light_dir = light['pos'] - hit_point
        dist = np.linalg.norm(light_dir)
        
        if dist == 0:
            return 0, None, 0
        
        light_dir /= dist
        epsilon = 0.001
        shadow_origin = hit_point + normal * epsilon
        
        shadowed = any(
            0 < self.ray_sphere_intersect(shadow_origin, light_dir, spheres[other_idx]['center'], spheres[other_idx]['radius']) < dist
            for other_idx in range(len(spheres)) if other_idx != hit_sphere_idx
        )
        
        visibility = 0 if shadowed else 1
        
        return visibility, light_dir, dist

    def normalize_image(self, image):
        max_val = np.max(image)

        if max_val > 0:
            image = (image / max_val * 255).astype(np.uint8)
        else:
            image = image.astype(np.uint8)

        return image

    def ray_sphere_intersect(self, origin, dir, center, radius):
        oc = origin - center
        a = np.dot(dir, dir)
        b = 2 * np.dot(oc, dir)
        c = np.dot(oc, oc) - radius ** 2
        disc = b ** 2 - 4 * a * c

        if disc < 0:
            return np.inf

        sqrt_disc = np.sqrt(disc)
        t1 = (-b - sqrt_disc) / (2 * a)
        t2 = (-b + sqrt_disc) / (2 * a)

        if t1 > 0 and t2 > 0:
            return min(t1, t2)
        elif max(t1, t2) > 0:
            return max(t1, t2)
        else:
            return np.inf
