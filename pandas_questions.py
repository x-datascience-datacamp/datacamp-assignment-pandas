"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using geopandas.
"""
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    """Load data from the CSV files referendum/regions/departments."""
    referendum = pd.read_csv("./data/referendum.csv", sep=';')
    regions = pd.read_csv("./data/regions.csv", sep=',')
    departments = pd.read_csv('./data/departments.csv', sep=',')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions.drop(["slug", "id"], axis=1, inplace=True)
    regions = regions.rename(columns={'code': 'code_reg'})

    departments.drop(["slug", "id"], axis=1, inplace=True)
    departments = departments.rename(columns={"region_code": "code_reg"})

    regions_and_departments = pd.merge(regions, departments, on="code_reg",
                                       suffixes=("_reg", "_dep"))
    regions_and_departments.rename(columns={'code': 'code_dep'}, inplace=True)

    return regions_and_departments


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """

    delete_departments = ['ZA', 'ZB', 'ZC', 'ZD', 'ZM', 'ZN',
                          'ZP', 'ZS', 'ZW', 'ZX', 'ZZ']
    referendum[~referendum['Department code'].isin(delete_departments)]
    referendum['Department code'] = referendum['Department code'].str.zfill(2)
    referendum_and_areas = pd.merge(regions_and_departments, referendum,
                                    left_on='code_dep',
                                    right_on='Department code')
    return referendum_and_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by code_reg and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    referendum_result_by_regions = referendum_and_areas.groupby(
                                    by=['code_reg', 'name_reg'],
                                    as_index=False).sum()
    referendum_result_by_regions.drop('Town code', axis=1, inplace=True)
    referendum_result_by_regions.set_index('code_reg', inplace=True)
    return referendum_result_by_regions


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from regions.geojson.
    * Merge these info into referendum_result_by_regions.
    * Use the method GeoDataFrame.plot to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo_data = pd.read_json('data/regions.geojson')
    gdf = gpd.GeoDataFrame.from_features(geo_data['features'])
    gdf.drop('nom', axis=1, inplace=True)
    gdf = gdf.set_index('code')
    join_gdf = gdf.join(referendum_result_by_regions)
    sum_choices = (join_gdf['Choice A'] + join_gdf['Choice B'])
    join_gdf['ratio'] = join_gdf['Choice A'] / sum_choices
    join_gdf.plot(column='ratio', cmap='Reds', legend=True)

    return join_gdf


if __name__ == "_main_":

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