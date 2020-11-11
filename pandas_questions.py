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
    regions = pd.DataFrame(pd.read_csv("data/regions.csv", sep=','))
    departments = pd.DataFrame(
        pd.DataFrame(
            pd.read_csv(
                "data/departments.csv",
                sep=',')))

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    temp1 = regions.rename(
        columns={
            "code": "region_code",
            "name": "name_reg",
            "id": "id_reg",
            "slug": "slug_reg"})
    temp2 = departments.rename(
        columns={
            "code": "code_dep",
            "name": "name_dep"})
    df = temp1.merge(temp2, on="region_code")
    df = df.rename(columns={"region_code": "code_reg"})
    df = df.drop(["id_reg", "id", "slug", "slug_reg"], axis="columns")
    return df


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    tempdf1 = referendum.drop(
        referendum[referendum["Department name"] ==
                   "FRANCAIS DE L'ETRANGER"].index, axis="index")
    tempdf1 = tempdf1.drop(
        tempdf1[tempdf1["Department code"].str.startswith('Z')].index,
        axis="index")
    tempdf2 = regions_and_departments
    temp_code = tempdf1["Department code"]
    for i in range(len(temp_code.values)):
        if temp_code.values[i] in [
                "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
            temp_code.values[i] = "0" + temp_code.values[i]
    tempdf1["code_dep"] = temp_code
    df = tempdf1.merge(tempdf2, on="code_dep", how="left")
    return df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    tempdf = referendum_and_areas[["code_reg", "name_reg"]]
    tempdf = tempdf.drop_duplicates()
    df = referendum_and_areas.groupby("code_reg").sum()
    df = df.drop(["Town code"], axis="columns")
    df = df.merge(tempdf, on="code_reg")
    df = df.set_index("code_reg")

    return df


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geodata = gpd.read_file("data/regions.geojson")
    geodata = geodata.rename(columns={"code": "code_reg"})
    df = geodata.merge(referendum_result_by_regions, on="code_reg")
    df["ratio"] = df["Choice A"] / \
        (df["Registered"] - df["Abstentions"] - df["Null"])
    df.plot(column="ratio", legend=True)
    return df


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
