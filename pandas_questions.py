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
    reg = regions.rename(columns={'code': 'code_reg', 'name': 'name_reg'})
    dep = departments.rename(columns={
        'region_code': 'code_reg', 'code': 'code_dep', 'name': 'name_dep'
        })
    df = pd.merge(
        reg[['code_reg', 'name_reg']],
        dep[['code_reg', 'code_dep', 'name_dep']],
        on='code_reg', how='left'
        )

    return df


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    ref = referendum.copy()
    ref['Department code'] = ref['Department code'].apply(lambda x: x.zfill(2))
    df = pd.merge(
        ref,
        regions_and_departments,
        left_on='Department code',
        right_on='code_dep',
        how='inner'
        )

    return df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    cols = ['code_reg', 'name_reg', 'Registered',
            'Abstentions', 'Null', 'Choice A', 'Choice B']
    df = referendum_and_areas[cols].groupby(
        ['code_reg', 'name_reg'],  as_index=False
        ).sum()
    df.set_index('code_reg', inplace=True)

    return df


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    gdf = gpd.read_file('data/regions.geojson')
    df = pd.merge(
        referendum_result_by_regions, gdf, left_on='code_reg', right_on='code'
        )
    df['ratio'] = df['Choice A'] / (df['Choice A'] + df['Choice B'])
    referendum_map = gpd.GeoDataFrame(df)
    referendum_map.plot(column='ratio')

    return referendum_map


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
