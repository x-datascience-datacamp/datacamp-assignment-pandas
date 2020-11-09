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
    referendum = pd.read_csv('./data/referendum.csv', sep=';')
    regions = pd.read_csv('./data/regions.csv', sep=',')
    departments = pd.read_csv('./data/departments.csv', sep=',')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    new_reg = regions.drop(['id', 'slug'], axis=1).rename(
        columns={'code': 'code_reg', 'name': 'name_reg'}
    )
    new_dep = departments.drop(['id', 'slug'], axis=1).rename(
        columns={'code': 'code_dep', 'name': 'name_dep'}
    )
    merged_region_departments = pd.merge(new_reg, new_dep,
                                         left_on="code_reg",
                                         right_on="region_code").drop(
                                         ['region_code'], axis=1)
    return merged_region_departments


def standard_department_name(original_department_code):
    """Add a zero at the beginning of the 1-digit department codes."""
    if len(original_department_code) < 2:
        return str(0) + str(original_department_code)
    else:
        return original_department_code


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum['Department code'] = referendum['Department code'].apply(
                                    lambda x: standard_department_name(x))
    merged_referendum_area = pd.merge(
        referendum, regions_and_departments,
        left_on="Department code", right_on="code_dep")
    return merged_referendum_area


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    referendum_grouped_by_reg = referendum_and_areas.groupby(
        ["code_reg", "name_reg"], as_index=False)
    absolute_count_per_reg = referendum_grouped_by_reg[
        ["Registered", "Abstentions", "Null", "Choice A", "Choice B"]
    ].sum()
    absolute_count_per_reg.set_index('code_reg', inplace=True)
    return absolute_count_per_reg


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geographic_data = gpd.read_file("./data/regions.geojson", sep=";")
    geographic_data.drop(['nom'], axis=1, inplace=True)
    full_data = pd.merge(referendum_result_by_regions, geographic_data,
                         left_on="code_reg", right_on="code")
    total_votes = full_data['Registered'] - (full_data['Abstentions']
                                             + full_data['Null'])
    full_data['ratio'] = (full_data['Choice A'] / total_votes)
    ratio_per_region = gpd.GeoDataFrame(full_data)
    ratio_per_region.plot(column="ratio")
    return ratio_per_region


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
