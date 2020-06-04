# forest-climate-risks

This repository contains the Python code neccessary to reproduce Figure 4 from

> Anderegg et al. (2020) Climate-driven risks to the climate mitigation potential of forests, Science

We are actively developing more general purpose data products and tools related to this work. This particular repository is just for reproducing the analysis and plotting for the Figure.

To run the two scripts that generate the plots, first install the requirements

```
pip install -r requirements.txt
```

And then run the two commands

```
python plot_histograms.py
python plot_maps.py
```

The two key pieces of underlying data are a derived table of fire probabilities averaged within ecoregions, and the shapefiles for the ecoregions obtained from the Climate Action Reserve.

The fire probabilities are themselves obtained from processing the raw [MTBS raster data](https://www.mtbs.gov/direct-download), as follows:

- Step 1
- Step 2
- ...



