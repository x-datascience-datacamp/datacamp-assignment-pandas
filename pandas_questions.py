"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.read_csv("data/referendum.csv", sep=";")
    regions = pd.read_csv("data/regions.csv", sep=",")
    departments = pd.read_csv("data/departments.csv", sep=",")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions = regions[['code', 'name']]
    departments = departments[['code', 'name', 'region_code']]
    regions_and_departments = pd.merge(regions, departments, how='inner',
                                       left_on='code',
                                       right_on='region_code')
    regions_and_departments = regions_and_departments.drop(
                                columns=['region_code'])
    regions_and_departments.columns = ['code_reg', 'name_reg',
                                       'code_dep', 'name_dep']

    return regions_and_departments


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum = referendum[~referendum['Department code'].str.contains('Z')]
    code_series = referendum["Department code"].str.pad(2, fillchar="0")
    referendum.loc[:, "Department code"] = code_series
    referendum_and_areas = pd.merge(referendum, regions_and_departments,
                                    how='left',
                                    left_on='Department code',
                                    right_on='code_dep')

    return referendum_and_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    referendum_and_areas = referendum_and_areas.drop("Town code", axis=1)
    referendum_results = referendum_and_areas.groupby(
                            ["code_reg", "name_reg"]).sum()

    referendum_results.reset_index().set_index("code_reg")

    return referendum_results.reset_index().set_index("code_reg")


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geopd = gpd.read_file('./data/regions.geojson')
    geopd = geopd.set_index('code')
    geopd = geopd.join(referendum_result_by_regions, how='left')
    geopd['ratio'] = geopd['Choice A'] / (geopd['Choice A'] +
                                          geopd['Choice B'])
    geopd.plot(column='ratio')
    return geopd


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
