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

    referendum = pd.read_csv("data/referendum.csv", sep=';')
    regions = pd.read_csv("data/regions.csv", sep=',')
    departments = pd.read_csv("data/departments.csv", sep=',')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """

    departments = departments.rename(columns={'region_code': 'code_reg',
                                              'code': 'code_dep',
                                              'name': 'name_dep'})
    regions = regions.rename(columns={'code': 'code_reg', 'name': 'name_reg'})
    regions_and_departments = pd.merge(
        regions[['code_reg', 'name_reg']],
        departments[['code_reg', 'code_dep', 'name_dep']],
        on='code_reg', how='left')

    return regions_and_departments


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    # the format for departments code is not the same : we correct it
    referendum['Department code'] = referendum['Department code'].apply(
        lambda code: code.zfill(2))
    referendum_and_areas = pd.merge(
        regions_and_departments, referendum,
        left_on='code_dep', right_on='Department code', how='left')
    referendum_and_areas = referendum_and_areas.dropna()

    return referendum_and_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """

    referendum_and_areas = referendum_and_areas.drop(
        columns=['code_dep', 'name_dep', 'Town name',
                 'Town code', 'Department name', 'Department code'])
    # Group by both name and code to not lose a column
    referendum_result_by_regions = referendum_and_areas.groupby(
        by=['name_reg', 'code_reg'], as_index=False).sum()
    referendum_result_by_regions = referendum_result_by_regions.set_index(
        ['code_reg'])

    return referendum_result_by_regions


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    geomap = gpd.read_file('data/regions.geojson')
    geomap_results = pd.merge(geomap, referendum_result_by_regions,
                              left_on='code', right_on='code_reg')
    # Caution : Null votes do not count as expressed ballots
    geomap_results['ratio'] = geomap_results['Choice A'] / (geomap_results[
        'Choice A'] + geomap_results['Choice B'])
    geomap_results.plot('ratio')
    return geomap_results


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
