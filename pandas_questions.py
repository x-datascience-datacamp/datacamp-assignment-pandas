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
from pathlib import Path

Dir = Path('.')


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.read_csv(Dir / "data" / "referendum.csv", sep=";")
    regions = pd.read_csv(Dir / "data" / "regions.csv")
    departments = pd.read_csv(Dir / "data" / "departments.csv")
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    reg_and_dep = pd.merge(
            regions, departments,
            how='inner',
            left_on="code",
            right_on="region_code",
            suffixes=["_reg", "_dep"])
    reg_and_dep = reg_and_dep[['code_reg', 'name_reg', 'code_dep', 'name_dep']]
    return reg_and_dep


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    # Pad strings in the Series/Index by prepending ‘0’ characters.1 -> 01
    referendum['Department code'] = referendum['Department code'].str.zfill(2)
    ref_reg_and_dep = pd.merge(
            referendum, regions_and_departments,
            left_on="Department code",
            right_on="code_dep")
    # No need to drop DOM-TOM-COM and the french living abroad
    # because merge will remove them automatically with intersetion operation
    ref_reg_and_dep = pd.merge(referendum, regions_and_departments,
                               left_on="Department code",
                               right_on="code_dep")
    return ref_reg_and_dep


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    columns = ["code_reg", "name_reg"]
    regions_groups = referendum_and_areas.groupby(
        columns, as_index=False
    )
    count_by_regions = regions_groups[
        ["Registered", "Abstentions", "Null", "Choice A", "Choice B"]
    ].sum()
    # Setting index on code_reg
    return count_by_regions.set_index('code_reg')


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo_df = gpd.read_file(Dir / "data" / "regions.geojson", sep=";")
    # Merge these info into `referendum_result_by_regions` and dropping
    # duplicate name column
    regions_geometry = pd.merge(
        referendum_result_by_regions,
        geo_df,
        left_on="code_reg",
        right_on="code"
    ).drop(['nom'], axis=1)
    # compute ratio of choice A over all registered
    regions_geometry['ratio'] = (
        regions_geometry['Choice A'] /
        (regions_geometry['Registered'] -
         regions_geometry['Abstentions'] - regions_geometry['Null'])
    )
    # plotting and returning results
    geo_regions_ratios = gpd.GeoDataFrame(regions_geometry)
    geo_regions_ratios.plot(column="ratio")
    return geo_regions_ratios


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
