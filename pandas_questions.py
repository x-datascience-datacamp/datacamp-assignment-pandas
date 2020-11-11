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
    regions = pd.read_csv('data/regions.csv', sep=',')
    departments = pd.read_csv('data/departments.csv', sep=',')
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    return pd.merge(departments[['region_code', 'code', 'name']],
                    regions[['code', 'name']],
                    left_on=['region_code'],
                    right_on=['code'],
                    how='left',
                    suffixes=('_dep', '_reg')).drop('region_code', axis=1)


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    not_Z_df = referendum[~referendum['Department code'].str.startswith('Z')]
    not_Z_df['Department code'] = not_Z_df['Department code'].str.zfill(2)
    merged_df = pd.merge(not_Z_df,
                         regions_and_departments,
                         left_on='Department code',
                         right_on='code_dep'
                         )
    return merged_df.dropna()


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    # drop unnecessary cols
    unnecessary_cols = [
        'Department code', 'Department name', 'Town code', 'Town name',
        'code_dep', 'name_dep'
    ]
    core_df = referendum_and_areas.drop(unnecessary_cols, axis=1)
    core_df = core_df.groupby(['code_reg', 'name_reg']).sum()
    core_df = core_df.reset_index().set_index('code_reg')
    return core_df


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    # define file
    geojson_file = open("./data/regions.geojson")
    geo_df = gpd.read_file(geojson_file)
    # set index
    geo_df = geo_df.set_index('code')
    # merge dfs
    geo_df = geo_df.merge(referendum_result_by_regions,
                          left_index=True,
                          right_index=True)
    # create and plot ratio variable
    geo_df['ratio'] = geo_df['Choice A']/(geo_df['Choice B']
                                          + geo_df['Choice A'])
    geo_df.plot(column='ratio')
    return geo_df


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
