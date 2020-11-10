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
    referendum = pd.read_csv("data/referendum.csv", sep=";")
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions = regions.drop(columns=['id', 'slug'])
    departments = departments.drop(columns=['id', 'slug'])
    merge = departments.merge(regions, how="outer", left_on="region_code", right_on="code")
    merge = merge.drop(columns=["code_y"])
    merge = merge.rename(columns={"region_code": "code_reg", "code_x": "code_dep",
                                  "name_x": "name_dep", "name_y": "name_reg"})
    cols = merge.columns.tolist()
    tmp = cols[1]
    cols[1] = cols[3]
    cols[3] = cols[2]
    cols[2] = tmp
    merge = merge[cols]

    return merge


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    regions_and_departments["code_dep"] = regions_and_departments["code_dep"].apply(
        lambda value: value[1] if value[0] == '0' else value)
    merge = referendum.merge(regions_and_departments, how="inner", left_on="Department code", right_on="code_dep")
    merge = merge.drop(merge[merge["name_reg"].isin(["Collectivités d'Outre-Mer", "Guadeloupe",
                                                     "Mayotte", "Guyane", "La Réunion", "Martinique"])].index)
    return merge


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    results = referendum_and_areas.groupby(['code_reg', 'name_reg'])[['Registered',
                                                                      'Abstentions',
                                                                      'Null',
                                                                      'Choice A',
                                                                      'Choice B',
                                                                      'name_reg']].sum().reset_index()
    results = results.set_index('code_reg')
    return results


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    data = gpd.read_file("data/regions.geojson")
    merge = data.merge(referendum_result_by_regions, how="outer", left_on='nom', right_on='name_reg')
    merge['ratio'] = merge['Choice A'] /(merge['Choice B'] + merge['Choice A'])
    merge.plot()
    return merge


if __name__ == "__main__":

    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

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
