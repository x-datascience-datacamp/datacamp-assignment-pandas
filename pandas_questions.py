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

pd.set_option("display.max_columns", 500)
pd.set_option("display.width", 1000)
pd.set_option("display.max_rows", 500)


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    DIRNAME = os.path.dirname(__file__)

    referendum = pd.read_csv(
        os.path.join(DIRNAME, "data", "referendum.csv"), sep=";"
    )

    regions = pd.read_csv(
        os.path.join(DIRNAME, "data", "regions.csv"), sep=","
    )

    departments = pd.read_csv(
        os.path.join(DIRNAME, "data", "departments.csv"), sep=","
    )

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    merged = regions[["code", "name"]].merge(
        departments[["region_code", "code", "name"]],
        left_on="code",
        right_on="region_code",
    )
    del merged["region_code"]
    merged.columns = ["code_reg", "name_reg", "code_dep", "name_dep"]
    return merged


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    regions_and_departments["code_dep"] = regions_and_departments[
        "code_dep"
    ].apply(lambda x: x.lstrip("0"))

    merged = referendum.merge(
        regions_and_departments, left_on="Department code", right_on="code_dep"
    )

    return merged


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    res = referendum_and_areas.groupby(
        ["code_reg", "name_reg"], as_index=False
    ).sum()
    res = res.set_index("code_reg")
    del res["Town code"]
    return res


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    filename = "data/regions.geojson"
    file = open(filename)
    df = gpd.read_file(file)
    merged = df.merge(
        referendum_result_by_regions, left_on="code", right_on="code_reg"
    )
    merged["ratio"] = merged["Choice A"] / (
        merged["Choice A"] + merged["Choice B"]
    )
    merged.plot(column="ratio", legend=True)
    return merged


if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(df_reg, df_dep)
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
