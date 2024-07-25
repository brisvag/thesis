#!/usr/bin/env python3

from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import kaleido  # not used but needed for save

N = 1000
x = np.linspace(0, np.pi * 2, N)

blob = np.zeros(N)
rng = slice(N//2, N*2//3)
blob[rng] = -np.sin(x*3)[rng]

spike = np.zeros(N)
spike[N//3:N//2] = np.linspace(0, 1, N//2-N//3)

cc = np.correlate(spike, blob, mode='same')
cc /= cc.max()

df = pd.DataFrame(
    {
        'spike': spike,
        'blob': blob,
        'cross correlation': cc,
        'empty': np.full(N, np.nan),  # just so we get an extra subplot
    },
    index=x,
)
df.columns.name = 'function'
df.index.name = 'x'

fig = px.line(df, facet_row='function', facet_row_spacing=0.01)

# add spike and shifted blob to bottom subplot
blob_shifted = np.roll(df.blob, np.argmax(cc) - N // 2)
fig.add_trace(go.Scatter(x=df.index, y=spike, line_color=px.colors.qualitative.Plotly[0]), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=blob_shifted, line_color=px.colors.qualitative.Plotly[1]), row=1, col=1)
# hide legend for everything in last subplot
fig.update_traces({'showlegend': False}, row=1, col=1)

# clean up useless details and layout
fig.update_xaxes(visible=False, fixedrange=True)
fig.update_yaxes(visible=False, fixedrange=True)
fig.update_layout(annotations=[], overwrite=True, margin=dict(l=20, r=20, t=20, b=20), plot_bgcolor='white', paper_bgcolor='white')

fig.write_image(Path(__file__).parent.parent / "img/introduction/cross_correlation.png", width=800, height=400, scale=3)
