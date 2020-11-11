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
    referendum = pd.read_csv('data/referendum.csv', sep=';')
    regions = pd.read_csv('data/regions.csv',)
    departments = pd.read_csv('data/departments.csv')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    a = regions.drop(["id", "slug"], axis=1)
    a = a.rename(columns={"code": "code_reg", "name": "name_reg"})
    b = departments.drop(["id", "slug"], axis=1)
    b = b.rename(columns={"code": "code_dep", "name": "name_dep",
                          "region_code": "code_reg"})

    return pd.merge(a, b, on='code_reg', how='left')


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    dom_tom = referendum.index[referendum["Department code"].str.contains("Z")]
    ref = referendum.drop(dom_tom)

    test = ref["Department code"].isin(["1", "2", "3", "4", "5",
                                        "6", "7", "8", "9"])
    ref.loc[test, "Department code"] = '0' + ref.loc[test, "Department code"]

    result = pd.merge(ref, regions_and_departments,
                      left_on="Department code", right_on="code_dep",
                      how='outer').dropna()

    return result


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    result = referendum_and_areas[['code_reg', 'name_reg',
                                   'Registered', 'Abstentions',
                                   'Null', 'Choice A', 'Choice B']]
    result = result.groupby(['code_reg', 'name_reg']).sum()

    return result.reset_index('name_reg')


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    res = gpd.read_file('data/regions.geojson',)

    res = pd.merge(res, referendum_result_by_regions,
                   left_on="code", right_on="code_reg",
                   how='outer').dropna()

    res['ratio'] = res['Choice A'] / (res['Choice A'] + res['Choice B'])

    res.plot(column='ratio')

    return res


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
