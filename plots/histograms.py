from pandas import read_csv
from scipy.stats import binom
import matplotlib.pyplot as plt
from numpy import arange, clip, mean
from palettable.colorbrewer.sequential import YlOrRd_9

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

def integrated_risk(p):
    return (1 - binom.cdf(0, 100, p))

def plot_histogram(data):
    cmap = YlOrRd_9.mpl_colormap
    plt.figure(figsize=(7, 3))
    N, bins, patches = plt.hist(
        clip(integrated_risk(data) * 100, 0, 50), 
        bins=arange(0, 55, 5), 
        rwidth=0.9, 
        edgecolor='black', 
        linewidth=1.2
    )
    for thisbin, thispatch in zip(bins, patches):
        # scale by 2 so it saturates at 50
        color = cmap(thisbin / 100 * 2)
        thispatch.set_facecolor(color)
    plt.axvline(
        mean(integrated_risk(data) * 100), 
        color='k', 
        linestyle='dashed', 
        linewidth=1
    )
    plt.yscale('log')
    plt.ylim([0.5, 100])
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)

plt.rcParams.update({'font.size': 10})
plot_histogram(first_half['fraction'])
plot_histogram(second_half['fraction'])
plt.show(block=True)