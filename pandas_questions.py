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
    reg = regions[['code', 'name']]
    reg.columns = ['code_reg', 'name_reg']

    dep = departments[['region_code', 'code', 'name']]
    dep.columns = ['code_reg', 'code_dep', 'name_dep']
    print(dep.head(3))
    print(reg.head(3))
    sol = pd.merge(reg, dep, on='code_reg', how='left')
    return sol


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    # On rajoute un 0 devant les départements à un seul numéro
    referendum['Department code'] = referendum['Department code'].apply(
        lambda x: x.zfill(2))

    solution = pd.merge(regions_and_departments, referendum,
                        right_on="Department code", left_on="code_dep",
                        how='right').dropna(axis=0)

    return solution


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    ref_region = referendum_and_areas.groupby(['code_reg']).agg({
        'name_reg': 'max', 'Registered': 'sum', 'Abstentions': 'sum',
        'Null': 'sum', 'Choice A': 'sum', 'Choice B': 'sum'})
    return ref_region


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    regions = gpd.read_file('data/regions.geojson')

    df = pd.merge(regions, referendum_result_by_regions,
                  right_on='name_reg', left_on='nom')

    df['ratio'] = df['Choice A']/(df['Choice A'] + df['Choice B'])

    geo_df = gpd.GeoDataFrame(df)
    geo_df.plot(column='ratio')
    return geo_df


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
