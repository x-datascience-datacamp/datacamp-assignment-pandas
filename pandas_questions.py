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

    referendum = pd.DataFrame(pd.read_csv('data/referendum.csv', sep=';'))
    regions = pd.DataFrame(pd.read_csv('data/regions.csv'))
    departments = pd.DataFrame(pd.read_csv('data/departments.csv'))

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """

    r = regions.rename(columns={'code': 'code_reg', 'name': 'name_reg'})
    d = departments.rename(columns={'code': 'code_dep', 'name': 'name_dep', "region_code": "code_reg"})
    df = pd.merge(d, r, on="code_reg", how="left")[['code_reg', 'name_reg', 'code_dep', 'name_dep']]
    return df


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """

    ref = referendum.copy()
    ref["code_dep"] = referendum["Department code"]
    for i in range(len(ref["code_dep"])):
        if ref["code_dep"][i] in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
            ref.loc["code_dep", i] = "0" + ref["code_dep"][i]
    ref = ref[ref["code_dep"].str.startswith("Z") == False]
    rd = regions_and_departments[regions_and_departments['code_reg'] != "COM"]
    result = pd.merge(rd, ref, on='code_dep', how='left')
    return result.dropna()


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """

    temp = referendum_and_areas[['code_reg', 'name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']].groupby(["code_reg", "name_reg"]).sum()
    return(temp.reset_index().set_index("code_reg"))


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    data = gpd.read_file('data/regions.geojson')
    temp = data.merge(referendum_results.rename(columns={"name_reg": 'nom'}), on="nom")
    gdf = gpd.GeoDataFrame(temp)
    gdf["ratio"] = gdf["Choice A"] / (gdf["Choice A"] + gdf["Choice B"])
    gpd.GeoDataFrame.plot(gdf, column="ratio")

    return gdf


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
