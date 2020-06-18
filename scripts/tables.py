# this script uses shape files of ecoregions
# to aggregate statistics from burned area rasters

import zarr
import gcsfs
from geopandas import read_file
from pandas import DataFrame, concat
from numpy import asarray, where
from shapely.prepared import prep
from shapely.geometry import Point

# load ecoregions
sf = read_file('data/ecoregions.500m.geojson')

# load array of burned area rasters
gcs = gcsfs.GCSFileSystem(anon=True)
root = 'carbonplan-data/processed/MTBS/raster.zarr/'
store = gcsfs.GCSMap(root=root, gcs=gcs, check=False)
group = zarr.group(store=store)
array = asarray(group['4000m']['burned_area'])

# function for comparing a region to a bounding box
def inbounds(p, b):
    c1 = p[:,0] > b[0]
    c2 = p[:,0] < b[2]
    c3 = p[:,1] > b[1]
    c4 = p[:,1] < b[3]
    return c1 & c2 & c3 & c4

# main loop over years
years = ['%s' % (d + 1984) for d in range(2018-1984)]
dfs = []
index = range(len(sf))
columns = ['ecoregion', 'year', 'fraction']
for y, year in enumerate(years):
    df = DataFrame(index=index, columns=columns)
    vals = asarray(where(array[y] > 0)).T
    for s, shape in enumerate(sf['geometry']):
        df.at[s, 'ecoregion'] = s
        df.at[s, 'year'] = year
        bounds = shape.bounds
        prepared = prep(shape)
        inds = inbounds(vals, bounds)
        inside = asarray(
            [prepared.contains(Point([p[0], p[1]])) for p in vals[inds]]
        )
        if len(inside) > 0:
            rc = vals[inds][inside]
            total = array[y, rc.T[0], rc.T[1]].sum()
            df.at[s,'fraction'] = total / shape.area
        else:
            df.at[s,'fraction'] = 0
    dfs.append(df)

out = concat(dfs, axis=0)
out.reset_index(drop=True).to_csv('data/MTBS.500m.csv')