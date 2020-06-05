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

z = zarr.open('data/MTBS.2017.500m.zarr/0', 'r')
g = zarr.open('data/MTBS.2017.500m.zarr', 'r')
t = Affine(*list(g.attrs['transform'])[0:6])
a = asarray(z)
shapes_rc = [xy_to_rc(s,t) for s in shapes]

s = GeoSeries(shapes_rc)
s.to_file('ecoregions.500m.geojson', driver='GeoJSON')