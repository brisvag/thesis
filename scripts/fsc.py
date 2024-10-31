#!/usr/bin/env python3

from pathlib import Path
import numpy as np
from PIL import Image
from scipy.fft import fftn, fftshift
from scipy.signal import correlate
import napari
from skimage.util import random_noise
from rich.progress import track

import pandas as pd
import plotly.express as px
import kaleido  # not used but needed for save

def shell(shape, start, end):
    center = shape[0] / 2
    ranges = [np.arange(0, d) for d in shape]
    indices = np.stack(np.meshgrid(*ranges, indexing="ij"), axis=-1) + 0.5
    dists = np.linalg.norm(indices - center, axis=-1)

    start = start * shape[0] / 2
    end = end * shape[0] / 2
    mask = (dists >= start) & (dists < end)
    return mask

def ncc(a, b):
    a = (a - np.mean(a)) / (np.std(a) * len(a))
    b = (b - np.mean(b)) / (np.std(b))
    return correlate(a, b, mode='same')


if __name__ == '__main__':
    im = Image.open('moyai.jpg').convert('L')
    a = np.asarray(im)
    nshells = 50
    bins = [(i, i + 1/nshells) for i in np.arange(0, nshells) / nshells]
    shells = [shell(a.shape, start, end) for start, end in bins]

    fscs = []
    for noise_level in (0.01, 0.1):
        noisy1 = random_noise(a, var=noise_level)
        ft1 = fftshift(fftn(noisy1))
        ps1 = np.log(np.abs(ft1)**2 - 1)

        noisy2 = random_noise(a, var=noise_level)
        ft2 = fftshift(fftn(noisy2))
        ps2 = np.log(np.abs(ft2)**2 - 1)

        fsc = []
        for sh in track(shells, description=f'correlating shells for noise={noise_level}...'):
            cc = ncc(np.abs(ft1[sh]), np.abs(ft2[sh]))
            fsc.append(cc.max())
        fscs.append(np.array(fsc))

    v = napari.Viewer()
    v.add_image(ps1)
    v.add_labels(np.sum([s * i for i, s in enumerate(shells)], axis=0), opacity=0.25)

    v.grid.enabled = True
    v.grid.stride = -2

    v.export_figure(Path(__file__).parent.parent / 'img/introduction/fsc_shells.png', scale_factor=3)
    # needs modification...
    df = pd.DataFrame(
        {
            '0.02': fscs[0],
            '0.005': fscs[1],
        },
        index=np.arange(0, nshells) / nshells,
    )
    df.index.name = 'fraction of nyquist'
    fig = px.line(df)

    colors = px.colors.qualitative.Plotly

    fig.add_hline(y=0.143, line_width=3, line_dash="dash", line_color='black', annotation_text='0.143', annotation_position='left')

    for i, fsc in enumerate(fscs):
        sh = np.argmax(fsc < 0.143)
        x = (sh - 0.5) / nshells  # to align properly
        fig.add_vline(x=x, line_width=2, line_dash="dash", line_color=colors[i], annotation_text=str(x), annotation_position='bottom')

    # clean up useless details and layout
    fig.update_xaxes(showticklabels=False)
    fig.update_layout(yaxis_title="correlation", legend_title='Noise variance', overwrite=True, margin=dict(l=20, r=20, t=20, b=20), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')

    fig.write_image(Path(__file__).parent.parent / "img/introduction/fsc_plot.png", width=600, height=325, scale=6)
    fig.show()
