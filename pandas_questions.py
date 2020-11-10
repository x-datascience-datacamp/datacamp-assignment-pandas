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


DIRNAME = os.path.dirname(__file__)


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.read_csv(os.path.join(
        DIRNAME, "data", "referendum.csv"), header=0, sep=';')
    regions = pd.read_csv(os.path.join(
        DIRNAME, "data", "regions.csv"), header=0)
    departments = pd.read_csv(os.path.join(
        DIRNAME, "data", "departments.csv"), header=0)

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    res = pd.merge(regions,
                   departments,
                   suffixes=('_reg', '_dep'),
                   left_on='code',
                   right_on='region_code')
    res = res.drop(['id_reg', 'slug_reg', 'id_dep',
                    'region_code', 'slug_dep'], axis=1)
    return res


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    cond = regions_and_departments.code_reg != "COM"
    regions_and_departments = regions_and_departments[cond]
    regions_and_departments = regions_and_departments.replace(
        {'01': '1', '02': '2', '03': '3', '04': '4',
         '05': '5', '06': '6', '07': '7', '08': '8', '09': '9'})
    res = pd.merge(regions_and_departments,
                   referendum,
                   left_on='code_dep',
                   right_on='Department code',
                   how='inner')
    return res


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    resby = referendum_and_areas.groupby(['code_reg', 'name_reg']).sum().drop(
        'Town code', axis=1).reset_index(level=1)
    return resby


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    area = gpd.read_file(os.path.join(DIRNAME, "data", "regions.geojson"))
    area = area.set_index('code').drop('nom', axis=1)
    merged_geo = gpd.GeoDataFrame(
        pd.concat([referendum_result_by_regions, area], axis=1, join='inner'))

    merged_geo['ratio'] = merged_geo['Choice A'] / \
        (merged_geo['Choice A']+merged_geo['Choice B'])
    merged_geo.plot(column='ratio')

    return merged_geo


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
