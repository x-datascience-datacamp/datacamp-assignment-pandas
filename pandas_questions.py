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
    referendum = pd.read_csv("data/referendum.csv", sep=';')
    regions = pd.read_csv("data/regions.csv", sep=',')
    departments = pd.read_csv("data/departments.csv", sep=',')
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    df_merged = pd.merge(regions, departments, left_on="code",
                         right_on="region_code")[
        ["code_x", "name_x", "code_y", "name_y"]]
    df_merged = df_merged.rename(columns={
                                 "code_x": "code_reg",
                                 "name_x": "name_reg",
                                 "code_y": "code_dep",
                                 "name_y": "name_dep"})

    return df_merged


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    def remove_zeros(x):
        if x[0] != "0":
            return x
        else:
            return x[1:]

    referendum = referendum.loc[~referendum["Department code"].str.contains("Z"
                                                                            )]
    regions_and_departments = regions_and_departments.loc[
        regions_and_departments["code_reg"] != "COM"]
    dumpy_var_to_satisfy_flake8 = regions_and_departments["code_dep"].apply(
        remove_zeros)
    regions_and_departments["code_dep"] = dumpy_var_to_satisfy_flake8
    df_merged = pd.merge(referendum, regions_and_departments,
                         left_on="Department code", right_on="code_dep")

    return df_merged


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    referendum_and_areas_test = referendum_and_areas[[
        'code_reg', 'Registered', 'Abstentions', 'Null',
        'Choice A', 'Choice B']]
    referendum_and_areas_test = referendum_and_areas_test.groupby(
        "code_reg").sum()
    name_reg = referendum_and_areas[[
        "name_reg", "code_reg"]].set_index("code_reg")
    name_reg = name_reg.drop_duplicates()
    name_reg.merge(referendum_and_areas_test, left_index=True,
                   right_index=True, how="right")
    return name_reg.merge(referendum_and_areas_test, left_index=True,
                          right_index=True, how="right")


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from regions.geojson.
    * Merge these info into referendum_result_by_regions.
    * Use the method GeoDataFrame.plot to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geographic_data = gpd.read_file("data/regions.geojson").set_index("code")
    ratio_df = pd.merge(right=referendum_result_by_regions,
                        left=geographic_data,
                        right_index=True,
                        left_on="code")
    choice_A = ratio_df["Choice A"]
    choice_B = ratio_df["Choice B"]
    ratio = choice_A / (choice_A + choice_B)
    ratio_df["ratio"] = ratio
    ratio_df.plot(column="ratio")
    return gpd.GeoDataFrame(ratio_df)


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
