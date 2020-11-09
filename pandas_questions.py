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
import os

ABROAD_REGION_CODES = ['01', '02', '03', '04', '06', 'COM']


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    dirname = os.path.dirname(__file__)

    referendum = pd.read_csv(
        os.path.join(dirname, "data", "referendum.csv"), sep=";"
    )
    regions = pd.read_csv(os.path.join(dirname, "data", "regions.csv"))
    departments = pd.read_csv(os.path.join(dirname, "data", "departments.csv"))
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    # dropping unecessary columns and renaming for each dataframe
    modified_regions = regions.drop(['id', 'slug'], axis=1).rename(
        columns={'code': 'code_reg', 'name': 'name_reg'}
    )
    modified_departments = departments.drop(['id', 'slug'], axis=1).rename(
        columns={'code': 'code_dep', 'name': 'name_dep'}
    )
    # merge on region code
    merged_df = pd.merge(
        modified_regions,
        modified_departments,
        left_on="code_reg",
        right_on="region_code"
    )
    return merged_df.drop(['region_code'], axis=1)


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    # pad the code departments 1 -> 01
    referendum['Department code'] = referendum['Department code'].apply(
        lambda x: x.zfill(2)
    )
    # merge on code department and drop join column, DOM/abroad departments will
    # be automatically dropped since they are not present in
    # regions_and_departments dataframe
    return pd.merge(
        referendum,
        regions_and_departments,
        left_on="Department code",
        right_on="code_dep"
    )


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """

    return pd.DataFrame({})


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    return gpd.GeoDataFrame({})


if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(
        df_reg, df_dep
    )
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    print(referendum_and_areas)
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
