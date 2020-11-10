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


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.read_csv('./data/referendum.csv', sep=';')
    regions = pd.read_csv('./data/regions.csv')
    departments = pd.read_csv('./data/departments.csv')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    departments.columns = ['id', 'code', 'code_dep', 'name', 'slug']
    regions_and_departments = departments.merge(regions, on='code')
    regions_and_departments = \
        regions_and_departments[['code', 'name_y', 'code_dep', 'name_x']]
    regions_and_departments.columns = \
        ['code_reg', 'name_reg', 'code_dep', 'name_dep']

    return regions_and_departments


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum['Department code'] = \
        referendum['Department code'].apply(lambda x: x.zfill(2))
    referendum_and_areas = regions_and_departments.merge(
        referendum, left_on='code_dep',
        right_on='Department code', how='left')
    referendum_and_areas = referendum_and_areas.dropna()
    return referendum_and_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    result_by_regions = referendum_and_areas.groupby(['code_reg']).sum()
    result_by_regions.drop('Town code', inplace=True, axis=1)
    result_by_regions = result_by_regions.reset_index()
    regions = referendum_and_areas[['code_reg', 'name_reg']].drop_duplicates()
    merge = result_by_regions.merge(regions, on='code_reg', how='left')
    merge.set_index('code_reg')
    merge = merge[[
        'name_reg', 'Registered',
        'Abstentions', 'Null', 'Choice A', 'Choice B']]
    return merge


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geodata = gpd.read_file('./data/regions.geojson')
    map_results = pd.merge(
        geodata, referendum_result_by_regions,
        left_on='nom', right_on='name_reg', how='right')
    map_results['ratio'] = \
        map_results['Choice A'] /\
        (map_results[['Choice A', 'Choice B']]).sum(axis=1)
    gpd.GeoDataFrame.plot(map_results, column='ratio')
    return map_results


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

    plot_referendum_map(referendum_results)
    plt.show()
