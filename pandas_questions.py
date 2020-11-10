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


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    DIRNAME = os.path.dirname(__file__)

    referendum = pd.DataFrame(
        pd.read_csv(os.path.join(DIRNAME, "data", "referendum.csv"), sep=";")
    )
    regions = pd.DataFrame(
        pd.read_csv(os.path.join(DIRNAME, "data", "regions.csv"), sep=",")
    )
    departments = pd.DataFrame(
        pd.read_csv(os.path.join(DIRNAME, "data", "departments.csv"), sep=",")
    )

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    to_return = pd.merge(
        regions[["code", "name"]],
        departments[["region_code", "code", "name"]],
        left_on="code",
        right_on="region_code",
        how="right",
    )
    to_return = to_return.drop(["region_code"], axis=1)
    to_return.columns = ["code_reg", "name_reg", "code_dep", "name_dep"]

    return pd.DataFrame(to_return)


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    ref = referendum[
        -referendum["Department name"].isin(["FRANCAIS DE L'ETRANGER"])
    ]
    ref = ref[-ref["Department code"].str.contains("Z")]
    ref["Department code"] = ref["Department code"].str.pad(2, fillchar="0")
    regions_and_departments = regions_and_departments[
        (regions_and_departments["code_reg"] != "DOM")
        & (regions_and_departments["code_reg"] != "TOM")
        & (regions_and_departments["code_reg"] != "COM")
    ]
    regions_and_departments = regions_and_departments[
        regions_and_departments["code_dep"].str.len() < 3
    ]
    to_return = pd.merge(
        regions_and_departments,
        ref,
        left_on="code_dep",
        right_on="Department code",
        how="right",
    )

    return pd.DataFrame(to_return)


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    to_return = referendum_and_areas.loc[
        :,
        [
            "code_reg",
            "name_reg",
            "Registered",
            "Abstentions",
            "Null",
            "Choice A",
            "Choice B",
        ],
    ]
    to_return = to_return.groupby(["code_reg", "name_reg"]).sum()
    to_return.reset_index(inplace=True)
    to_return.set_index("code_reg", inplace=True)

    return pd.DataFrame(to_return)


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    DIRNAME = os.path.dirname(__file__)
    geo = gpd.read_file(os.path.join(DIRNAME, "data", "regions.geojson"))
    geo.set_index("code", inplace=True)
    referendum_result_by_regions = pd.merge(
        referendum_result_by_regions,
        geo["geometry"],
        left_index=True,
        right_index=True,
    )
    expressed_votes = referendum_result_by_regions.loc[
        :, "Choice A":"Choice B"
    ].sum(axis=1)
    ratio = referendum_result_by_regions["Choice A"] / expressed_votes
    gpd.GeoDataFrame(referendum_result_by_regions).plot(
        column=ratio, legend=True
    )
    to_return = referendum_result_by_regions.copy()
    to_return["ratio"] = ratio

    return gpd.GeoDataFrame(to_return)


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
