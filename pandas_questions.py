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


d = os.getcwd()


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.read_csv(d + "/data/referendum.csv", sep=';')
    regions = pd.read_csv(d + "/data/regions.csv")
    departments = pd.read_csv(d + "/data/departments.csv")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    s = regions.rename(columns={"code": "region_code", "name": "name_region"})
    X = pd.merge(s[['region_code', 'name_region']], departments[[
                 'region_code', 'code', 'name']], on='region_code', how='left')
    X = X.rename(
        columns={
            "region_code": "code_reg",
            "name_region": "name_reg",
            "code": "code_dep",
            "name": "name_dep"})
    return X


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    X = referendum
    X = X.drop(X[X['Department code'].str.startswith('Z')].index)
    Y = regions_and_departments
    Y = Y.drop(Y[Y['code_reg'] == 'COM'].index)
    Y = Y.drop(Y[Y['code_reg'].str.startswith('0')].index)
    dep = []
    for d in X['Department code']:
        if len(d) == 1:
            dep.append("0" + d)
        else:
            dep.append(d)
    X['Department code'] = dep
    Z = pd.merge(Y, X, left_on='code_dep', right_on='Department code')

    return Z


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    res = referendum_and_areas[['code_reg',
                                'name_reg',
                                'Registered',
                                'Abstentions',
                                'Null',
                                'Choice A',
                                'Choice B']].groupby('code_reg').sum()
    name_regions = referendum_and_areas[[
        'code_reg', 'name_reg']].drop_duplicates().set_index('code_reg')
    f = pd.merge(name_regions, res, on='code_reg', how='left')
    return f


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo = 'data/regions.geojson'
    data = gpd.read_file(geo)
    merge = pd.merge(referendum_result_by_regions, data, left_on="code_reg",
                     right_on="code")
    merge['ratio'] = merge['Choice A'] / \
        (merge['Choice A'] + merge['Choice B'])
    gpd.GeoDataFrame(merge).plot(column='ratio')
    return gpd.GeoDataFrame(merge)


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
