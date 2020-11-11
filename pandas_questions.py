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
    referendum = pd.read_csv("./data/referendum.csv", sep=";")
    regions = pd.read_csv("./data/regions.csv", sep=",")
    departments = pd.read_csv("./data/departments.csv", sep=",")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    columns = ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    regions_and_departments = pd.merge(regions[['code', 'name']],
                                       departments[['region_code',
                                                    'code', 'name']],
                                       left_on='code', right_on='region_code',
                                       suffixes=['_reg', '_dep'])
    regions_and_departments = regions_and_departments[columns]
    return regions_and_departments


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    pading_referendum = referendum["Department code"].str.pad(2, fillchar="0")
    referendum["Department code"] = pading_referendum
    referendum_and_areas = pd.merge(referendum, regions_and_departments,
                                    left_on="Department code",
                                    right_on="code_dep",
                                    how="left")
    referendum_and_areas = referendum_and_areas.dropna()

    return referendum_and_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    columns = ['code_reg', 'name_reg', 'Registered', 'Abstentions',
               'Null', 'Choice A', 'Choice B']
    data_grouped = referendum_and_areas.groupby(['code_reg', 'name_reg'],
                                                as_index=False)[columns].sum()

    return data_grouped.set_index("code_reg")


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    data = gpd.read_file("data/regions.geojson")
    data = data.merge(referendum_result_by_regions,
                      left_on="code", right_on="code_reg")
    data["ratio"] = data["Choice A"] / (data['Registered'] -
                                        data['Abstentions'] - data['Null'])
    data.plot("ratio")
    plt.show()

    return data


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
