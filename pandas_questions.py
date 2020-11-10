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
    referendum = pd.DataFrame(pd.read_csv("data/referendum.csv", sep=';'))
    regions = pd.DataFrame(pd.read_csv("data/regions.csv"))
    departments = pd.DataFrame(pd.read_csv("data/departments.csv"))
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions.columns = ["id_reg", "c_reg", "n_reg", "s_reg"]
    departments.columns = ['id_dep', 'c_reg', 'c_dep', 'n_dep', 's_dep']
    r = pd.merge(regions, departments, on='c_reg')
    D = {'a': r['c_reg'], 'b': r['n_reg'], 'c': r['c_dep'], 'd': r['n_dep']}
    re = pd.DataFrame(data=D)
    re.columns = ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    return re


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    r = referendum.copy()
    rd = regions_and_departments.copy()
    for i in range(len(r['Department code'])):
        if len(r['Department code'][i]) == 1:
            r['Department code'][i] = '0'+r['Department code'][i]
        else:
            r['Department code'][i] = r['Department code'][i]
    result = pd.merge(r, rd, left_on='Department code', right_on='code_dep')
    result = result.dropna()
    return result


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    referendum_and_areas = referendum_and_areas.drop(
        columns=['name_dep', 'Department name', 'Town code'])
    r = referendum_and_areas.groupby(
                        by=["code_reg", "name_reg"]).sum().reset_index()
    r = r.set_index("code_reg")
    return r


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    data = gpd.read_file('./data/regions.geojson')
    rrr = referendum_result_by_regions.copy()
    merge = pd.merge(data, rrr, left_on='code', right_on='code_reg')
    merge['ratio'] = merge['Choice A']/(merge['Choice A']+merge['Choice B'])
    merge.plot(column='ratio')

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
