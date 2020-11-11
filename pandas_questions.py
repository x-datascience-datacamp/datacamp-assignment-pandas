"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacap/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.read_csv("data/referendum.csv", sep=';')
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv", sep=',')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    new_df = pd.merge(
                departments, regions,
                left_on=['region_code'], right_on=['code'])
    new_df = new_df[['region_code', 'name_y', 'code_x', 'name_x']]
    new_df.columns = ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    return new_df


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum, regions, departments = load_data()
    merging_referendum = regions_and_departments[
        regions_and_departments[
            'code_dep'].str.len() == 2]
    referendum = referendum[~referendum['Department code'].str.contains('Z')]
    referendum['Department code'] = referendum[
        'Department code'].str.zfill(2)
    merging_referendum = pd.merge(
        referendum, merging_referendum,
        left_on='Department code', right_on='code_dep'
    )
    return merging_referendum


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    referendum, regions, departments = load_data()
    regions_and_departments = merge_regions_and_departments(
                                regions, departments)
    merging_referendum = merge_referendum_and_areas(
        referendum, regions_and_departments)
    referendum_regions = merging_referendum.set_index(
        'code_reg').groupby(
        by=['name_reg', 'code_reg']).sum().reset_index()
    referendum_regions = referendum_regions.set_index(
        'code_reg')
    referendum_regions = referendum_regions[[
        'name_reg', 'Registered',
        'Abstentions', 'Null', 'Choice A', 'Choice B']]

    return referendum_regions


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geomap = gpd.read_file('data/regions.geojson')
    geomap_results = pd.merge(
        geomap, referendum_result_by_regions,
        left_on='code', right_on='code_reg')
    geomap_results['ratio'] = geomap_results['Choice A'] / (
                            geomap_results['Choice A'] +
                            geomap_results['Choice B'])
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
