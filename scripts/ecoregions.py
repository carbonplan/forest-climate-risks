# this script was used to convert shapefiles
# from raw FIA ecoregions used by the Climate Action Reserve
# into a 500m resolution with discretized indices
# and bounding box matched to our processing of MTBS data
#
# raw data downloaded from 
# https://www.climateactionreserve.org/wp-content/uploads/2009/03/GIS-Supersection-Shape-File1.zip

RAW_PATH = 'GIS-Supersection-Shape-File1.zip'
SAVE_PATH = 'ecoregions.500m.geojson'

import shapefile
from rasterio import Affine
from shapely.ops import transform
from shapely.geometry import Polygon, MultiPolygon
from rasterio.transform import rowcol

def parse(raw):
    shapes = []
    for i, s in enumerate(raw.shapes()):
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

def discretize(p, t):
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

raw = shapefile.Reader(RAW_PATH)
parsed = parse(raw)

flip = lambda x, y: (y, x)
t = Affine(*[500.00000000000006, 0.0, -2493045.0, 0.0, -500.00000000000006, 3310005.0])
discretized = [discretize(s, t) for s in parsed]
flipped = [transform(flip, s) for s in discretized]

sf = GeoSeries(flipped)
sf.to_file(SAVE_PATH, driver='GeoJSON')