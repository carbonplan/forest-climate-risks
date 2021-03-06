# forest-climate-risks

This repository contains the code neccessary to reproduce Figure 4 on fire risks to forest carbon from

> Anderegg et al. (2020) Climate-driven risks to the climate mitigation potential of forests, Science, 10.1126/science.aaz7005

We are actively developing new open source datasets and tools related to this work. This particular repository is just for reproducing the simple analysis and plots for the review article figure.

To run the two scripts that generate the plots, first install the requirements

```
pip install -r requirements.txt
```

And then run the two commands

```
python plots/histograms.py
python plots/maps.py
```

## analysis

For each ecoregion and year, a pixel-wise burn probability was computed as the fraction of pixels in that ecoregion labeled as moderate or severe fire. These probabilities were then averaged across years over two time periods (1984 to 2000, and 2001 to 2017). To project an integrated 100-year risk, we computed the probability of any pixel within a region experiencing at least one fire under a binomial distribution with 100 trials and success probability given by the pixel-wise annual risk described above. This simple analysis does not account for spatial or temporal autocorrelation or attempt to model any drivers of fire risk.

## data

The two derived data files neccessary to directly replicate the figures are included in this repo as [`MTBS.500m.csv`](data/MTBS.500m.csv) and [`ecoregions.500m.geojson`](ecoregions.500m.geojson).

The raw fire data come from the [Monitoring Trends in Burn Severity (MTBS)](https://www.mtbs.gov/) public datasets, specifically, the [burn severity mosaics](https://www.mtbs.gov/direct-download) for CONUS from the years 1984 to 2017. Code for preprocessing these data is available at [carbonplan/data](https://github.com/carbonplan/data/tree/master/scripts/mtbs). Briefly: thematic rasters were binarized so as to set values of 3 and 4 (corresponding to moderate and high burn severity) to 1 and all other values to 0, and then downsampled to 500m via averaging. Some areas contain "striped" masked regions due to a LANDSAT scan line corrector artifact. Treating these pixels as non data values during downsampling at a scale of 10x or more effectively removes this artifact.

The raw geographic regions come from Forest Inventory Analysis (FIA) supersection maps of the U.S. forest regions, as [processed and provided by](https://www.climateactionreserve.org/how/protocols/forest/assessment-area-data/) the Climate Action Reserve (CAR). The specific regions were downloaded from [these shape files](https://www.climateactionreserve.org/wp-content/uploads/2009/03/GIS-Supersection-Shape-File1.zip) and then discretized to a 500m grid to match our processing of the `MTBS` data. See [shapefiles.py](scripts/ecoregions.py) for how this conversion was performed, and see [tables.py](scripts/tables.py) for how the 500m fire raster data was averaged within these ecoregions to construct a dataframe of fire risk probabilities. 
