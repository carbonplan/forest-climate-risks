import os
import zarr
import shapefile
from tqdm import tqdm
from pandas import DataFrame, concat
from numpy import asarray, where
from rasterio import Affine
from shapely.prepared import prep
from shapely.geometry import Point

from treeplan.utils import xy_to_rc, extract_shapes, inbounds

sf = shapefile.Reader('/Users/freeman/Downloads/CAR_Supersections/CAR_Supersections')
shapes = extract_shapes(sf)

years = ['%s' % (d + 1984) for d in range(2018-1984)]

dfs = []

for y in years:
    print('processing year: %s' % y)
    f = 'MTBS.%s.500m' % y
    b = '/Users/freeman/github/treeplan-data/processed/'
    z = zarr.open(os.path.join(b, 'rasters', f + '.zarr', '0'), 'r')
    g = zarr.open(os.path.join(b, 'rasters', f + '.zarr'), 'r')
    t = Affine(*list(g.attrs['transform'])[0:6])
    a = asarray(z)
    vals = asarray(where(a > 0)).T
    shapes_rc = [xy_to_rc(s,t) for s in shapes]

    df = DataFrame(index=range(len(shapes_rc)), columns=['ecoregion', 'year', 'fraction'])
    for i, shape in tqdm(enumerate(shapes_rc)):
        df.at[i, 'ecoregion'] = i
        df.at[i, 'year'] = y
        bounds = shape.bounds
        prepapred = prep(shape)
        inds = inbounds(vals, bounds)
        inside = asarray([prepapred.contains(Point(p)) for p in vals[inds]])
        if len(inside) > 0:
            rc = vals[inds][inside]
            df.at[i,'fraction'] = a[rc.T[0], rc.T[1]].sum() / shape.area
        else:
            df.at[i,'fraction'] = 0
    dfs.append(df)

out = concat(dfs, axis=0)

out.reset_index(drop=True).to_csv('MTBS-1984-2017-500m-fixed.csv')