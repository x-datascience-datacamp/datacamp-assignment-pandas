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
    referendum = pd.read_csv('referendum.csv', sep=';')
    regions = pd.read_csv('regions.csv', sep=',')
    departments = pd.read_csv('departments.csv', sep=',')
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    reg_dep = pd.merge(regions, departments,
                       how='inner', left_on='code',
                       right_on='region_code')
    reg_dep = reg_dep[['code_x', 'name_x', 'code_y', 'name_y']]
    reg_dep.rename(columns={'code_x': 'code_reg',
                                      'name_x': 'name_reg',
                                      'code_y': 'code_dep',
                                      'name_y': 'name_dep'}, inplace=True)
    return reg_dep


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    delete = ['ZZ', 'ZX', 'ZS', 'ZP', 'ZN', 'ZW', 'ZM', 'ZD', 'ZC', 'ZB', 'ZA']
    referendum = referendum[~referendum['Department code'].isin(delete)]
    regions_and_departments['code_dep'] = regions_and_departments[
                                          'code_dep'].apply(lambda x: x[1]
                                                            if x[0] == '0'
                                                            else x)
    delete_2 = ['1', '2', '3', '4', '5', '6', 'COM']
    reg_dep = regions_and_departments[
                                      ~regions_and_departments[
                                        'code_reg'].isin(delete_2)]
    ref_areas = pd.merge(referendum, reg_dep,
                         how='inner', left_on='Department code',
                         right_on='code_dep')
    ref_areas = ref_areas.drop(['code_dep', 'name_dep'], axis=1)
    ref_areas = ref_areas[['code_reg',
                           'name_reg',
                           'Department code',
                           'Department name',
                           'Town code',
                           'Town name',
                           'Registered',
                           'Abstentions',
                           'Null',
                           'Choice A',
                           'Choice B']]
    ref_areas = ref_areas.rename(columns={'code_reg': 'Region code',
                                          'name_reg': 'Region name'})
    return ref_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    grouped = referendum_and_areas.groupby('Region code',
                                           as_index=False)[[
                                               'Region name',
                                               'Registered',
                                               'Abstentions',
                                               'Null',
                                               'Choice A',
                                               'Choice B']].sum()

    return grouped


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo = gpd.read_file('regions.geojson')
    geo = gpd.GeoDataFrame(pd.merge(referendum_result_by_regions,
                           geo,
                           left_on='Region code',
                           right_on='code',
                           how='inner'))

    geo['div'] = geo['Choice A']/(geo['Choice A']
                                  + geo['Choice B'])
    geo = geo.plot(column='div')
    return geo


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
