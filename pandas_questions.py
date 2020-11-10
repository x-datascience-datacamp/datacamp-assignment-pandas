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
    """Load data from the CSV files referendum/regions/departments."""
    referendum = pd.read_csv('data/referendum.csv', sep=';')
    regions = pd.read_csv('data/regions.csv', sep=',')
    departments = pd.read_csv('data/departments.csv', sep=',')
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.
    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions_and_departments = pd.merge(departments, regions, how='left',
                                       left_on='region_code', right_on='code')\
                                           [['code_x', 'name_x', 'code_y', 'name_y']]
    regions_and_departments = \
        regions_and_departments[['code_y', 'name_y', 'code_x', 'name_x']]
    regions_and_departments.columns = ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    regions_and_departments.loc[:8, 'code_dep'] = \
        regions_and_departments.loc[:8, 'code_dep'].apply(lambda x: x[1:])
    return regions_and_departments


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum = referendum[-referendum['Department code'].str.contains('Z')]
    referendum_and_areas = pd.merge(referendum,regions_and_departments, left_on = 'Department code',\
         right_on = 'code_dep', how = 'left').reset_index(drop = True)
    return referendum_and_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """

    referendum_result_by_regions = referendum_and_areas.groupby(['code_reg', 'name_reg'], as_index = False)\
        ['Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B'].agg('sum')
    referendum_result_by_regions.index = referendum_result_by_regions['code_reg']
    referendum_result_by_regions = referendum_result_by_regions.drop(referendum_result_by_regions.columns[0], axis=1)
    referendum_result_by_regions = referendum_result_by_regions.iloc[:14,:]
    return referendum_result_by_regions


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    regions_geo = gpd.read_file('data/regions.geojson')
    results_df = pd.merge(referendum_result_by_regions, regions_geo, left_on = 'code_reg', right_on = 'code', how = 'left')
    results_df['ratio'] = results_df['Choice A']/(results_df['Choice A']+results_df['Choice B'])
    results_df = gpd.GeoDataFrame(results_df)
    results_df.plot(column='ratio')
    return results_df


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
