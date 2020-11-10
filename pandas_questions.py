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
    referendum = pd.read_csv('./data/referendum.csv', sep=";")
    regions = pd.read_csv('./data/regions.csv', sep=",")
    departments = pd.read_csv('./data/departments.csv', sep=",")
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    merged = pd.merge(regions, departments, left_on='code',
                      right_on='region_code', how='inner')
    regions_and_department = merged[['region_code', 'name_x',
                                     'code_y', 'name_y']]
    regions_and_department.rename(columns={'region_code': 'code_reg',
                                           'name_x': 'name_reg',
                                           'code_y': 'code_dep',
                                           'name_y': 'name_dep'}, inplace=True)
    return regions_and_department


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    df = referendum.copy()
    df = df[df['Department name'] != "FRANCAIS DE L'ETRANGER"]
    cods = df['Department code'].unique()
    df = df[df['Department code'].isin(cods[:-10])]
    cols = [x[1] if x[0] == '0' else
            x for x in regions_and_departments['code_dep']]
    regions_and_departments['code_dep'] = cols
    referendum_and_areas = pd.merge(df,
                                    regions_and_departments,
                                    left_on='Department code',
                                    right_on='code_dep', how='left')
    return referendum_and_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    cols = ['code_reg', 'name_reg', 'Registered', 'Abstentions', 'Null',
            'Choice A', 'Choice B']
    ref_and_ar = referendum_and_areas.copy()
    grouped = ref_and_ar[cols].groupby(['code_reg']).sum().reset_index()
    referendum_results = pd.merge(grouped,
                                  ref_and_ar[['code_reg', 'name_reg']],
                                  on='code_reg')[cols].drop_duplicates()
    referendum_results = referendum_results.set_index('code_reg')
    return referendum_results


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geographicData = gpd.read_file('./data/regions.geojson')
    merged = pd.merge(geographicData, referendum_result_by_regions,
                             left_on="code", right_on="code_reg")
    merged['ratio'] = merged['Choice A'] / (
        merged['Choice A'] + merged['Choice B'])
    merged.plot(column='ratio')
    return gpd.GeoDataFrame(merged)


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
