import matplotlib.pyplot as plt

from pandas import read_csv
from geopandas import read_file
from scipy.stats import binom
from numpy import asarray, arange, clip, mean
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
from descartes import PolygonPatch
from palettable.colorbrewer.sequential import YlOrRd_9

# read fire data
df = read_csv('data/MTBS-1984-2017-500m.csv', index_col=0)

# read spatial data
sf = read_file('data/ecoregions.500m.geojson')

# select first half (1984 - 2000)
first_half = (df.set_index('ecoregion')
    .query('year <= 2000')
    .groupby('ecoregion')
    .mean())

# select second half (2001 - 2017)
second_half = (df.set_index('ecoregion')
    .query('year > 2000')
    .groupby('ecoregion')
    .mean())

# calculate integrated risk score from fire probability
def integrated_risk(p):
    return (1 - binom.cdf(0, 100, p))

def plot_map(data):
    plt.figure(figsize=(7, 7))
    cmap = YlOrRd_9.mpl_colormap
    ax = plt.gca()
    draw = lambda i, shape: PolygonPatch(
        shape, 
        fc=cmap(integrated_risk(data[i]) * 2), 
        ec=[0, 0, 0], 
        linewidth=0.3, 
        alpha=1.0
    )
    [ax.add_patch(draw(i, shape)) for i, shape in enumerate(sf['geometry'])]
    ylim = ax.get_ylim()
    ax.set_ylim(ylim[1], ylim[0])
    ax.set_axis_off()
    ax.axis('scaled')
    cb = plt.colorbar(
        ScalarMappable(norm=Normalize(vmin=0, vmax=50), cmap=cmap), 
        ax=ax, 
        label='100 year integrated fire disturbance risk', 
        shrink=0.25, 
        ticks=[0, 50]
    )
    cb.outline.set_linewidth(0.2)
    cb.ax.tick_params(width=0.2)

plt.rcParams.update({'font.size': 8})
plot_map(first_half['fraction'])
plot_map(second_half['fraction'])
plt.show(block=True)