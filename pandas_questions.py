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
    path = '/Users/simondemouchy/datacamp-assignment-pandas/data/'

    referendum = pd.read_csv(path+'referendum.csv', sep=';')
    regions = pd.read_csv(path+'regions.csv')
    departments = pd.read_csv(path+'departments.csv')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    departments = departments.drop(columns=['slug', 'id'])
    regions = regions.drop(columns=['slug', 'id'])

    departments = departments.rename(columns={'code': 'code_dep',
                                              'name': 'name_dep',
                                              'region_code': 'code_reg'})
    regions = regions.rename(columns={'code': 'code_reg', 'name': 'name_reg'})

    return pd.merge(regions, departments, on='code_reg')


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    _, regions, departments = load_data()
    referendum = referendum.drop(columns=['Department name'])
    referendum = referendum.rename(columns={'Department code': 'code_dep'})
    OUT = ['ZA', 'ZB', 'ZC', 'ZD', 'ZM', 'ZN', 'ZP', 'ZS', 'ZW', 'ZX', 'ZZ']
    referendum = referendum[-referendum['code_dep'].isin(OUT)]
    
    df = merge_regions_and_departments(regions, departments)
    df["code_dep"] = df["code_dep"].apply(lambda x : x.lstrip('0'))
    return pd.merge(referendum, df, on='code_dep')


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    referendum_and_areas = referendum_and_areas.drop(columns=['Town code'])
    return referendum_and_areas.groupby('name_reg', as_index=False).sum()


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    path = '/Users/simondemouchy/datacamp-assignment-pandas/data/'
    reg_map = gpd.read_file(path+'regions.geojson')
    map_ref = gpd.GeoDataFrame(referendum_result_by_regions.merge(reg_map, right_on='nom', left_on='name_reg'))
    map_ref['ratio'] = map_ref['Choice A'] / (map_ref['Choice A'] + map_ref['Choice B'])
    map_ref.plot(column='ratio', legend=True)
    plt.show()
    return map_ref


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
