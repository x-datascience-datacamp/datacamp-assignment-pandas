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
    referendum = pd.DataFrame(pd.read_csv("data/referendum.csv", sep=';'))
    regions = pd.DataFrame(pd.read_csv("data/regions.csv", sep=','))
    departments = pd.DataFrame(pd.read_csv("data/departments.csv", sep=','))

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions_and_departments = pd.merge(
                            departments,
                            regions,
                            left_on='region_code',
                            right_on='code',
                            suffixes=("_dep", "_reg")
                                    )
    final_col = ['code_reg', 'name_reg', 'code_dep', 'name_dep']

    return regions_and_departments[final_col]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum.copy = referendum.copy()
    mask = referendum.copy['Department code'].map(len) < 2
    referendum.copy.loc[mask, 'Department code'] = (
            referendum.copy.loc[mask, 'Department code'].apply(lambda x: '0'+x)
                                                    )
    referendum_and_areas = pd.merge(
                        referendum.copy,
                        regions_and_departments,
                        how='inner',
                        left_on='Department code',
                        right_on='code_dep'
                                    )

    return referendum_and_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    referendum_results = referendum_and_areas.groupby("code_reg").sum()
    df_region_name = referendum_and_areas[['code_reg', 'name_reg']]
    df_region_name = df_region_name.set_index('code_reg')
    df_region_name = df_region_name[~df_region_name.duplicated()]
    referendum_results = pd.concat(
                        [referendum_results, df_region_name],
                        axis=1
                                )
    final_col = [
            'name_reg',
            'Registered',
            'Abstentions',
            'Null',
            'Choice A',
            'Choice B'
                ]

    return referendum_results[final_col]


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo_regions = gpd.read_file('data/regions.geojson')
    df = pd.merge(geo_regions, referendum_result_by_regions,
                  right_on='name_reg', left_on='nom')

    df['ratio'] = df['Choice A']/(df['Choice A'] + df['Choice B'])

    gdf = gpd.GeoDataFrame(df)
    gdf.plot(column='ratio')

    return gdf


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
