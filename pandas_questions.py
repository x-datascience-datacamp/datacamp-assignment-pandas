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
    referendum = pd.DataFrame({})
    regions = pd.DataFrame({})
    departments = pd.DataFrame({})

    referendum = pd.read_csv("./data/referendum.csv", delimiter=";")
    regions = pd.read_csv("./data/regions.csv")
    departments = pd.read_csv("./data/departments.csv")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions_and_departments = pd.merge(regions[['code', 'name']],
                                       departments[['region_code', 'code',
                                                    'name']],
                                       left_on=['code'],
                                       right_on=['region_code'], how='left',
                                       suffixes=('_reg', '_dep')).drop(
                                           ['region_code'], axis=1)
    return regions_and_departments


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    # Make both dataframe has the same type of common column and drop
    # DOM-TOM-COM departments, and the french living abroad
    regions_and_departments.code_dep = [x.lstrip("0") for x in
                                        regions_and_departments.code_dep]
    referendum_and_areas = pd.merge(referendum, regions_and_departments,
                                    left_on=['Department code'],
                                    right_on=['code_dep'],
                                    how='left').dropna()
    return referendum_and_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    returned_col = ['code_reg', 'name_reg', 'Registered', 'Abstentions',
                    'Null', 'Choice A', 'Choice B']
    referendum_result_by_regions = referendum_and_areas[returned_col].groupby(
        ['code_reg', 'name_reg'], as_index=False).sum().set_index('code_reg')
    return referendum_result_by_regions


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    regions_gdf = gpd.read_file("./data/regions.geojson")
    merged_df = pd.merge(referendum_result_by_regions, regions_gdf,
                         left_on=['code_reg'], right_on=['code'],
                         how='left').set_index('code')
    merged_gdf = gpd.GeoDataFrame(merged_df)
    merged_gdf['ratio'] = merged_gdf['Choice A'] / (merged_gdf['Choice A'] +
                                                    merged_gdf['Choice B'])
    merged_gdf.plot(column='ratio')

    return merged_gdf


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
