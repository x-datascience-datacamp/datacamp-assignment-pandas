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
    regions = pd.read_csv('data/regions.csv')
    departments = pd.read_csv('data/departments.csv')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    df = regions.merge(departments, left_on='code',
                       right_on='region_code',
                       suffixes=('_reg', '_dep'))
    return df[['code_reg', 'name_reg', 'code_dep', 'name_dep']]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    if referendum.dropna().shape != referendum.shape:
        raise ValueError("Missing values")
    referendum = referendum.dropna()
    index = {'1': '01', '2': '02', '3': '03', '4': '04', '5': '05',
             '6': '06', '7': '07', '8': '08', '9': '09'}
    for key, value in index.items():
        referendum.loc[referendum['Department code'] == key,
                       'Department code'] = value
    list_dep = list(regions_and_departments.code_dep)
    referendum[referendum['Department code'].isin(list_dep)]
    regions_and_departments[regions_and_departments['code_dep'].isin(list_dep)]
    df = referendum.merge(regions_and_departments, left_on='Department code',
                          right_on='code_dep', suffixes=(False, False))
    df = df[['Department code', 'Department name',
             'Town code', 'Town name', 'Registered',
             'Abstentions', 'Null', 'Choice A',
             'Choice B', 'code_dep', 'code_reg',
             'name_reg', 'name_dep']]
    return df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    output = referendum_and_areas.groupby(["code_reg"]).agg({
                       'name_reg': 'first',
                       'Registered': sum,
                       'Abstentions': sum,
                       'Null': sum,
                       'Choice A': sum,
                       'Choice B': sum})
    return output


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    reg_map = gpd.read_file('data/regions.geojson')
    merged_map_df = referendum_result_by_regions.merge(reg_map,
                                                       left_on='name_reg',
                                                       right_on='nom',
                                                       suffixes=(False, False))
    col_A = merged_map_df['Choice A']
    col_B = merged_map_df['Choice B']
    merged_map_df['exprime'] = col_A + col_B
    merged_map_df['ratio'] = col_A / merged_map_df['exprime']
    df_final = merged_map_df[['ratio', 'name_reg', 'geometry']]
    gdf = gpd.GeoDataFrame(df_final, geometry='geometry')
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
