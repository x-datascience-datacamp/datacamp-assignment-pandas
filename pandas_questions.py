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
    regions = pd.read_csv('data/regions.csv', sep=',')
    departments = pd.read_csv('data/departments.csv', sep=',')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    r = regions
    dp = departments
    d = r.merge(dp, how='right', right_on='region_code', left_on='code')
    d = d.drop(columns=['id_x', 'region_code', 'slug_x', 'id_y', 'slug_y'])
    d = d.rename(columns={'code_x': 'code_reg', 'name_x': 'name_reg',
                          'code_y': 'code_dep', 'name_y': 'name_dep'})
    d['code_dep'] = d['code_dep'].apply(lambda x: x[1] if x[0] == '0' else x)

    return d


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    r = referendum
    d = regions_and_departments
    ref = r[r['Department name'] != 'FRANCAIS DE L\'ETRANGER']
    ref['Department code'] = ref['Department code'].astype(str)
    d['code_dep'] = d['code_dep'].astype(str)
    h = d.merge(ref, how='right', right_on='Department code',
                left_on='code_dep')
    h = h.dropna()
    h.set_index('code_reg')
    return h


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    h = referendum_and_areas
    h = h.drop(columns=['name_dep', 'Department code', 'code_dep',
                        'Department name', 'Town code', 'Town name'])
    h = h.dropna()
    h = h.groupby(['code_reg', 'name_reg']).sum().reset_index('name_reg')

    return h


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    h = referendum_result_by_regions
    df = gpd.read_file('data/regions.geojson')
    df = df.merge(h, how='right', left_on='nom', right_on='name_reg')
    df['ratio'] = df['Choice A']/(df['Choice A']+df['Choice B'])
    df.plot(column='ratio', legend=True)

    return df


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
