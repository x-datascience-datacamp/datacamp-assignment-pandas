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
    departments['code_dep'] = departments['code']
    departments['name_dep'] = departments['name']
    regions['code_reg'] = regions['code']
    regions['name_reg'] = regions['name']
    merged = pd.merge(regions, departments,
                      left_on="code", right_on="region_code")
    regions_departments = merged[['code_dep', 'code_reg',
                                  'name_dep', 'name_reg']]

    return regions_departments


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.Youdr.

    op the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum['Department code'] = referendum['Department code'].apply(
                                    lambda x: x.zfill(2))
    ref_area_NAN = pd.merge(referendum, regions_and_departments, how='left',
                            left_on='Department code', right_on='code_dep')
    referendum_areas = ref_area_NAN.dropna()
    return referendum_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    drop_col = ['Town code', 'Department name', 'name_dep']
    referendum_areas = referendum_and_areas.drop(columns=drop_col)
    referendum_areas_grp = referendum_areas.groupby(
                ['code_reg', 'name_reg']).sum().reset_index()
    results = referendum_areas_grp.set_index('code_reg')

    return results


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geodat = gpd.read_file('./data/regions.geojson')
    Results = pd.merge(geodat, referendum_result_by_regions, left_on="code",
                       right_on="code_reg")
    Results['ratio'] = Results['Choice A'] / (
                       Results['Choice A'] + Results['Choice B'])
    Results.plot(column='ratio')
    return gpd.GeoDataFrame(Results)


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
