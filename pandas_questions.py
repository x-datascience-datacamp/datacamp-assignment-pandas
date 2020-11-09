"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.read_csv("data/referendum.csv",
                             sep=';', error_bad_lines=False)
    regions = pd.read_csv("data/regions.csv")
    # Departement 01 => Department 1
    regions['code'] = regions['code'].apply(
        lambda x: str(int(x)) if x.isdigit() else x)
    # Drop DOM TOM COM regions.
    regions = regions[regions['code'].apply(
        lambda x: x not in ['COM', '1', '2', '3', '4', '5', '6'])]
    departments = pd.read_csv("data/departments.csv")
    departments['code'] = departments['code'].apply(
        lambda x: str(int(x)) if x.isdigit() else x)
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    cols = ['code_reg', 'name_reg', 'code_dep', 'name_dep']

    regions = regions.set_index('code')
    departments = departments.set_index('region_code')
    output = departments.join(regions, lsuffix='_dep', rsuffix='_reg')
    output = output.reset_index().rename(
        {'code': 'code_dep', 'index': 'code_reg'}, axis=1)
    output = output[cols]
    return output


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum['code_dep'] = referendum['Department code']
    referendum = referendum.set_index('code_dep')
    regions_and_departments = regions_and_departments.set_index('code_dep')
    output = referendum.join(regions_and_departments,
                             how='inner').reset_index()
    return output


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    output = pd.pivot_table(referendum_and_areas,
                            index='name_reg',
                            values=['Registered',
                                    'Abstentions',
                                    'Null',
                                    'Choice A',
                                    'Choice B'],
                            aggfunc=np.sum)

    output = output.reset_index()
    return output


def plot_referendum_map(referendum_results):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    regions_json = pd.read_json('data/regions.geojson')
    geo = gpd.GeoDataFrame.from_features(regions_json['features'])
    geo = geo.set_index('nom')
    referendum_results = referendum_results.set_index(
        'name_reg')
    geo_join = geo.join(referendum_results, how='inner').reset_index()
    geo_join = geo_join.rename({'index': 'name_reg'}, axis=1)
    geo_join['ratio'] = geo_join['Choice A'] / \
        (geo_join['Choice A'] + geo_join['Choice B'])
    geo_join.plot(column='ratio',
                  cmap='Reds',
                  legend=True,
                  legend_kwds={
                      'label': "Share of expressed votes for Choice A",
                      'orientation': "horizontal"})
    return geo_join


if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(
        df_reg, df_dep
    )
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )

    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
