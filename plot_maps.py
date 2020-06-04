import zarr
import shapefile
import matplotlib.pyplot as plt

from scipy.stats import binom
from numpy import asarray, arange, clip, mean
from rasterio import Affine
from pandas import read_csv
from descartes import PolygonPatch
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
from shapely.geometry.polygon import orient
from shapely.ops import transform
from shapely.geometry import Polygon, MultiPolygon, Point
from rasterio.transform import rowcol
from palettable.colorbrewer.sequential import YlOrRd_9

def xy_to_rc(p, t):
    if type(p) is Polygon:
        x, y = p.exterior.xy
        rc = rowcol(t, x, y)
        return Polygon(list(zip(rc[0], rc[1])))
    if type(p) is MultiPolygon:
        polygons = []
        for pp in p:
            x, y = pp.exterior.xy
            rc = rowcol(t, x, y)
            polygons.append(Polygon(list(zip(rc[0], rc[1]))))
        return MultiPolygon(polygons)

def extract_shapes(sf):
    shapes = []
    for i, s in enumerate(sf.shapes()):
        if len(s.parts) == 1:
            shapes.append(Polygon(s.points))
        else:
            polygons = []
            for ip in range(len(s.parts)):
                start = s.parts[ip]
                end = s.parts[ip+1] if ip < (len(s.parts) - 1) else len(s.points)
                p = Polygon(s.points[start:end])
                polygons.append(p)
            mp = MultiPolygon(polygons)
            shapes.append(mp)
    return shapes

# read data
df = read_csv('data/MTBS-1984-2017-500m.csv', index_col=0)

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

sf = shapefile.Reader('data/CAR_Supersections/CAR_Supersections')
shapes = extract_shapes(sf)

z = zarr.open('data/MTBS.2017.500m.zarr/0', 'r')
g = zarr.open('data/MTBS.2017.500m.zarr', 'r')
t = Affine(*list(g.attrs['transform'])[0:6])
a = asarray(z)
shapes_rc = [xy_to_rc(s,t) for s in shapes]

flip = lambda x, y: (y, x)
scale = lambda p: (1 - binom.cdf(0, 100, p))
colormap = YlOrRd_9.mpl_colormap

plt.rcParams.update({'font.size': 6})

def plot_map(data):
    plt.figure(figsize=(7, 7))
    ax = plt.gca()
    value = lambda i: scale(data[i]) * 2
    draw = lambda i, s: PolygonPatch(transform(flip, s), 
        fc=colormap(value(i)), ec=[0, 0, 0], linewidth=0.3, alpha=1.0)
    [ax.add_patch(draw(i, s)) if value(i) < 0.04 else None for i, s in enumerate(shapes_rc)]
    [ax.add_patch(draw(i, s)) if value(i) >= 0.04 else None for i, s in enumerate(shapes_rc)]
    ax.axis('scaled')
    ylim = ax.get_ylim()
    ax.set_ylim(ylim[1], ylim[0])
    ax.set_axis_off()
    cb = plt.colorbar(ScalarMappable(norm=Normalize(vmin=0, vmax=50), cmap=colormap), 
        ax=ax, label='100 year integrated fire disturbance risk', shrink=0.25, ticks=[0, 50])
    cb.outline.set_linewidth(0.2)
    cb.ax.tick_params(width=0.2)

plot_map(first_half['fraction'])
plot_map(second_half['fraction'])
plt.show(block=True)