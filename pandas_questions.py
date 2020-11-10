"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""
# %%
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.read_csv(
        "data/referendum.csv", sep=";", header=0, error_bad_lines=False)
    regions = pd.read_csv(
        "data/regions.csv", sep=",", header=0, error_bad_lines=False)
    departments = pd.read_csv(
        "data/departments.csv", sep=",", header=0, error_bad_lines=False)
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions.rename(
        columns={"code": "region_code"}, inplace=True)
    data = pd.merge(
        regions, departments, on="region_code").drop(
            ["id_x", "slug_x", "id_y", "slug_y"], axis=1)
    data.columns = ['code_reg', 'name_reg', 'code_dep', 'name_dep']

    return data


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    def func(x):
        x = str(x["Department code"])
        if(x.startswith("0")):
            x = x[1]
        return x

    regions_and_departments.rename(
        columns={"code_dep": "Department code"}, inplace=True)
    regions_and_departments["Department code"] = regions_and_departments.apply(
        func, axis=1)
    referendum.drop(
        referendum[
            ((referendum["Department code"].isin(["DOM", "COM", "TOM"]))
             | (referendum["Department code"].str.startswith("Z")))
             ].index, inplace=True)

    data = pd.merge(referendum, regions_and_departments, on="Department code")
    data["code_dep"] = data["Department code"]

    return data


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    referendum_and_areas.set_index("code_reg", inplace=True)
    data = referendum_and_areas.groupby(["code_reg", "name_reg"])
    data = data[
        ['Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']].sum()
    data.reset_index("name_reg", inplace=True)

    return data


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    g = gpd.read_file("data/regions.geojson")
    g.rename(columns={"code": "code_reg"}, inplace=True)
    g = pd.merge(g, referendum_result_by_regions, on="code_reg")
    g["ratio"] = g["Choice A"] / (g["Choice A"] + g["Choice B"])
    g.plot(column="ratio", legend="True")

    return g


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

# %%

# %%
