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


DIRNAME = os.path.dirname(__file__)


def load_data():
    """Load data from the CSV files."""
    referendum = pd.read_csv(os.path.join(DIRNAME,
                                          "data",
                                          "referendum.csv"), sep=";")

    regions = pd.read_csv(os.path.join(DIRNAME,
                                       "data",
                                       "regions.csv"), sep=",")

    departments = pd.read_csv(os.path.join(DIRNAME,
                                           "data",
                                           "departments.csv"), sep=",")
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions = regions.rename(
        columns={"code": "code_reg",
                 "name": "name_reg"})

    departments = departments.rename(
        columns={"code": "code_dep",
                 "name": "name_dep"})

    merge_df = pd.merge(regions,
                        departments,
                        left_on="code_reg",
                        right_on="region_code",
                        how='inner')

    regions_and_departments = merge_df[['code_reg',
                                        'name_reg',
                                        'code_dep',
                                        'name_dep']]

    return regions_and_departments


def remove_0(x):
    if x[0] == '0':
        x = x[1:]
    return x


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    regions_and_departments['code_dep'] = regions_and_departments[
        'code_dep'].apply(lambda x: remove_0(x))

    referendum_and_area = pd.merge(
        referendum,
        regions_and_departments,
        left_on="Department code",
        right_on="code_dep",
        how='inner'
        )

    return referendum_and_area


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    compute_referendum_result_by_regions = referendum_and_areas[
        [
            'code_reg',
            'name_reg',
            'Registered',
            'Abstentions',
            'Null',
            'Choice A',
            'Choice B'
        ]
        ].groupby(by=[
            "name_reg",
            "code_reg"], as_index=False
            ).sum().set_index("code_reg")

    return compute_referendum_result_by_regions


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    data = gpd.read_file(os.path.join(DIRNAME,
                                      "data",
                                      "regions.geojson"), sep=";")

    referendum_result_by_regions = pd.merge(referendum_result_by_regions,
                                            data,
                                            left_on="code_reg",
                                            right_on="code",
                                            how='inner')

    referendum_result_by_regions['ratio'] = (
        referendum_result_by_regions['Choice A'] /
        (
            referendum_result_by_regions['Registered'] -
            referendum_result_by_regions['Abstentions'] -
            referendum_result_by_regions['Null']
            )
        )

    referendum_result_by_regions = gpd.GeoDataFrame(
        referendum_result_by_regions
        )
    referendum_result_by_regions.plot(column='ratio')
    return referendum_result_by_regions


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
