#!/usr/bin/env python3

from pathlib import Path
import numpy as np
from PIL import Image
from scipy.fft import fftn, fftshift, ifftn, ifftshift
from skimage.util import random_noise
import napari

def smoothstep_normalized(arr, min_val, max_val):
    rng = max_val - min_val
    normalized = (arr - min_val) / rng
    smooth = np.where(
        normalized < 0,
        0,
        np.where(normalized <= 1, 3 * normalized**2 - 2 * normalized**3, 1),
    )
    return 1 - smooth


def annulus(shape, start, end, padding=0.0):
    center = shape[0] / 2
    ranges = [np.arange(0, d) for d in shape]
    indices = np.stack(np.meshgrid(*ranges, indexing="ij"), axis=-1) + 0.5
    dists = np.linalg.norm(indices - center, axis=-1)

    radius = end * shape[0] / 2
    inner_radius = start * shape[0] / 2
    padding = padding * shape[0] / 2
    mask = smoothstep_normalized(dists, radius, radius + padding)
    if inner_radius:
        inner_mask = smoothstep_normalized(dists, inner_radius, inner_radius + padding)
        mask -= inner_mask
    return mask


if __name__ == '__main__':
    im = Image.open('/home/brisvag/Downloads/moyai.jpg').convert('L')
    a = np.asarray(im)
    a = random_noise(a, var=0.5)
    ft = fftshift(fftn(a))
    ps = np.log(np.abs(ft)**2 - 1)

    lowpass = annulus(a.shape, 0, .05, padding=0.01)
    bandpass = annulus(a.shape, .02, .15, padding=0.01)
    highpass = annulus(a.shape, .1, 2, padding=0.01)

    ft_low = ft * lowpass
    ft_band = ft * bandpass
    ft_high = ft * highpass

    ps_low = np.log(np.abs(ft_low)**2 - 1)
    ps_band = np.log(np.abs(ft_band)**2 - 1)
    ps_high = np.log(np.abs(ft_high)**2 - 1)

    low = ifftn(ifftshift(ft_low)).real
    band = ifftn(ifftshift(ft_band)).real
    high = ifftn(ifftshift(ft_high)).real

    v = napari.Viewer()
    v.add_image(a)
    v.add_image(low)
    v.add_image(band)
    v.add_image(high)

    il = v.add_image(ps)
    v.add_image(ps_low).contrast_limits = il.contrast_limits
    v.add_image(ps_band).contrast_limits = il.contrast_limits
    v.add_image(ps_high).contrast_limits = il.contrast_limits

    v.grid.enabled = True
    v.grid.stride = -1
    v.grid.shape = (-1, 4)

    v.export_figure(Path(__file__).parent.parent / 'img/introduction/filtering.png')
    # needs modification...
