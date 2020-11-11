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
    col_reg_rename = {"code": "code_reg", "name": "name_reg"}
    df_reg = regions[["code", "name"]].rename(columns=col_reg_rename)
    c = {"region_code": "code_reg",
         "code": "code_dep", "name": "name_dep"}
    df_dep = departments[["region_code", "code", "name"]].rename(columns=c)
    return pd.merge(df_reg, df_dep, on="code_reg", how="inner")


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    c = {"0" + str(i): str(i) for i in range(1, 11)}
    regions_and_departments = regions_and_departments.replace({'code_dep': c})
    df_ = pd.merge(referendum, regions_and_departments,
                   right_on="code_dep", left_on="Department code", how="inner")
    return df_


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    count_var = ['Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    keys_group = ['code_reg', 'name_reg']
    df_count = referendum_and_areas.groupby(keys_group)[count_var].sum()
    df_count.reset_index(keys_group, inplace=True)
    df_count.set_index('code_reg', drop=True, inplace=True)
    return df_count


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
    geom_data = gpd.read_file(file)
    geom_data = pd.merge(geom_data, referendum_result_by_regions,
                         left_on='code', right_on='code_reg', how="inner")
    expresed_ballots = ['Choice A', 'Choice B']
    total_ballots = geom_data[expresed_ballots].sum(axis=1)
    geom_data['ratio'] = geom_data['Choice A'] / total_ballots
    print(geom_data.head(10))
    legend_lab = "Proportion of choice A in the region"
    geom_data.plot(column="ratio",
                   legend=True, cmap='Greens', vmin=.3, vmax=.7,
                   legend_kwds={'label': legend_lab}, edgecolor="k",)
    return geom_data


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
