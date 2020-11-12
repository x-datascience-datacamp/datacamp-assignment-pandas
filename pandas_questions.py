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
    referendum = pd.read_csv(
        'data/referendum.csv', header=0, sep=';')
    regions = pd.read_csv(
        'data/regions.csv', header=0, sep=',')
    departments = pd.read_csv(
        'data/departments.csv', header=0,
        sep=',')
    referendum = referendum.dropna()
    regions = regions.dropna()
    departments = departments.dropna()

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    merged_regions_and_departments = pd.merge(
        regions.rename(
            columns={
                'code': 'code_reg',
                'name': 'name_reg'})[['code_reg', 'name_reg']],
        departments.rename(columns={
            'region_code': 'code_reg',
            'code': 'code_dep',
            'name': 'name_dep'})[['code_reg', 'code_dep', 'name_dep']],
        on='code_reg', how='right')
    return merged_regions_and_departments


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad
    """
    referendum = referendum.dropna()
    regions_and_departments.dropna()
    dom_tom_com = referendum[referendum[
        'Department code'].str.startswith('Z')].index
    referendum = referendum.drop(dom_tom_com)
    # regions_and_departments['name_dep'] = regions_and_departments[
    #     'name_dep'].str.replace(
    #         '-', ' ').str.replace(
    #             'ô', 'o').str.replace(
    #                 'é', 'e').str.replace(
    #                     'è', 'e').str.replace(
    #                         'CORSE DU SUD', 'CORSE SUD').str.upper()
    regions_and_departments['code_dep'] = regions_and_departments[
        'code_dep'].str.replace(
            '01', '1').str.replace(
                '02', '2').str.replace(
                    '03', '3').str.replace(
                        '04', '4').str.replace(
                            '05', '5').str.replace(
                                '06', '6').str.replace(
                                    '07', '7').str.replace(
                                        '08', '8').str.replace(
                                            '09', '9')
    regions_and_departments.drop(columns='name_dep')

    merged_referendum_and_areas = pd.merge(
        regions_and_departments,
        referendum.rename(
            columns={
                'Department code': 'code_dep'}), on='code_dep', how='right')
    merged_referendum_and_areas[
        'Department code'] = merged_referendum_and_areas['code_dep']
    return merged_referendum_and_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    referendum_and_areas = referendum_and_areas[[
        'code_reg', 'name_reg', 'Registered', 'Abstentions',
        'Null', 'Choice A', 'Choice B']]
    names_for_codes = referendum_and_areas[['code_reg', 'name_reg']]
    names_for_codes = names_for_codes.drop_duplicates()
    referendum_and_areas = referendum_and_areas.groupby('code_reg').sum()
    referendum_and_areas = pd.merge(
        names_for_codes, referendum_and_areas, how='right', on='code_reg')
    referendum_and_areas = referendum_and_areas.set_index('code_reg')

    return referendum_and_areas


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geographic = pd.DataFrame(gpd.read_file('data/regions.geojson'))

    ratio = referendum_result_by_regions['Choice A']/(
        referendum_result_by_regions[
            'Choice A'] + referendum_result_by_regions['Choice B'])
    referendum_result_by_regions['ratio'] = ratio

    referendum_result_by_regions = pd.merge(
        referendum_result_by_regions,
        geographic.rename(columns={'code': 'code_reg', 'nom': 'name_reg'}),
        how='left', on=['code_reg', 'name_reg'])
    referendum_result_by_regions = gpd.GeoDataFrame(
        referendum_result_by_regions)
    referendum_result_by_regions.plot(column='ratio')
    return referendum_result_by_regions


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
