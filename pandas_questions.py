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
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    merged_df = pd.merge(departments, regions,
                         left_on='region_code', right_on='code',
                         how='left')

    merged_df = merged_df[['code_y', 'name_y', 'code_x', 'name_x']]

    merged_df.columns = ['code_reg', 'name_reg', 'code_dep', 'name_dep']

    return merged_df


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    rd = regions_and_departments.copy()
    ref = referendum.copy()
    ref = ref.loc[ref['Department name'] != "FRANCAIS DE L'ETRANGER"]
    ref = ref.loc[~ref['Department code'].str.contains('Z')]

    ref['Department code'] = ref['Department code'].str.zfill(2)

    merged_df = pd.merge(ref, rd,
                         left_on='Department code', right_on='code_dep')

    return merged_df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    results = referendum_and_areas.groupby(['code_reg', 'name_reg'],
                                           as_index=False).sum()

    cols = ['code_reg', 'name_reg', 'Registered',
            'Abstentions', 'Null', 'Choice A', 'Choice B']

    results = results[cols]
    return results.set_index('code_reg')


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    gdf = gpd.read_file("data/regions.geojson", sep=";")

    merged_df = pd.merge(referendum_result_by_regions, gdf,
                         left_on='code_reg', right_on='code',
                         how='left')

    merged_df['ratio'] = (
            merged_df['Choice A'] /
            (merged_df['Registered'] -
             merged_df['Abstentions'] -
             merged_df['Null'])
    )

    map_gdf = gpd.GeoDataFrame(merged_df)
    map_gdf.plot(column="ratio")

    return map_gdf


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


referendum, regions, departments = load_data()
rd = merge_regions_and_departments(regions, departments)
m = merge_referendum_and_areas(referendum, rd)
c = compute_referendum_result_by_regions(m)
print(m)
print(c)
