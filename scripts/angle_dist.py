#!/usr/bin/env python3

from pathlib import Path
import pandas as pd
import numpy as np
from pyem.geom import expmap, rot2euler  # https://github.com/asarnow/pyem

import plotly.express as px
import kaleido  # not used but needed for save


def rec2df(arr):
    """Unpack nested recarray into a flat dataframe."""
    def _unpack_recarray(arr, name=None):
        names = arr.dtype.names
        dct = {}
        if names is None:
            if arr.ndim == 1:
                # normal column, just spit it out
                dct[name] = arr
            else:
                # column with multidimensional data
                # split it into indexed columns
                for i in range(arr.shape[1]):
                    dct[f'{name}_col{i:02}'] = arr[:, i]
        else:
            # named subcolumns
            for subname in names:
                dct.update(_unpack_recarray(arr[subname], subname))
        return dct

    return pd.DataFrame(_unpack_recarray(arr))


def load_data(data_path, passthrough_path):
    data = rec2df(np.load(data_path))
    passthrough = rec2df(np.load(passthrough_path))

    df = pd.merge(data, passthrough, on='uid', suffixes=('', '_DROP')).filter(regex="^(?!.*DROP)")
    return df



if __name__ == '__main__':
    df1 = load_data('/home/brisvag/tmp/plots/j181/particles_selected.cs', '/run/media/brisvag/writable/plots/j181/P88_J181_passthrough_particles_selected.cs')

    df1['source'] = 'filament picking'
    df1 = df1[['alignments2D/class', 'filament/filament_pose', 'source']]
    df1.columns = ['class', 'angle', 'source']
    df1['angle'] = (df1['angle'] / np.pi * 180)

    df2 = load_data('/home/brisvag/tmp/plots/j184/cryosparc_P88_J184_009_particles.cs', '/run/media/brisvag/writable/plots/j184/P88_J184_passthrough_particles.cs')

    df2['source'] = 'assigned angle'
    df2 = df2[['alignments2D/class', 'alignments3D/pose_col00', 'alignments3D/pose_col01', 'alignments3D/pose_col02', 'source']]
    df2.columns = ['class', 'rot', 'tilt', 'psi', 'source']

    # taken from pyem, conversion from Rodriguez coordinates to Euler angles
    # this was probably the missing piece the first time around :(
    df2[['rot', 'tilt', 'psi']] = -np.rad2deg(rot2euler(expmap(df2[['rot', 'tilt', 'psi']].values)))

    # the third angle is PSI in relion, which essentially represent in-plane angle for in-plane filaments
    df2 = df2[['class', 'psi', 'source']]
    df2.columns = ['class', 'angle', 'source']

    df = pd.concat([df1, df2])
    df['angle'] = np.mod(df['angle'], 180)

    fig = px.histogram(df, x='angle', color='class', facet_col='source')

    fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    fig.write_image(Path(__file__).parent.parent / "img/other/ftsz_angle_dist_good.png", width=700, height=300, scale=4)
    fig.show()
