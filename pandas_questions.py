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

    referendum = pd.read_csv('data//referendum.csv', sep=';')
    regions = pd.read_csv('data//regions.csv')
    departments = pd.read_csv('data//departments.csv')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """

    regg = regions.copy().rename(columns={'code': 'code_reg',
                                          'name': 'name_reg'},
                                 inplace=False)
    depp = departments.copy().rename(
        columns={'region_code': 'code_reg',
                 'code': 'code_dep',
                 'name': 'name_dep'})
    new = pd.merge(depp,
                   regg,
                   on='code_reg',
                   how='left')[['code_reg',
                                'name_reg',
                                'code_dep',
                                'name_dep']]

    return new


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """

    ref = referendum.copy().rename(columns={'Department code': 'code_dep'})
    ref = ref[ref['Department name'] != "FRANCAIS DE L'ETRANGER"]
    new = regions_and_departments.copy()
    new = new[new['code_reg'] != 'COM']
    new['code_dep'] = new['code_dep'].apply(lambda x: x.lstrip('0'))
    new2 = pd.merge(ref,
                    new,
                    on='code_dep',
                    how='left').dropna()
    new2 = new2.rename(columns={'code_dep': 'Department code'})
    new2.insert(9, 'code_dep', new2.loc[:, 'Department code'])

    return new2


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """

    res = referendum_and_areas.copy()
    res = res.groupby(by=['code_reg', 'name_reg']).sum()
    res = res.reset_index().set_index('code_reg')
    del res['Town code']

    return res


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    data = gpd.read_file('data//regions.geojson')
    data = data.rename(columns={'code': 'code_reg', 'nom': 'name_reg'})
    df = pd.merge(data,
                  referendum_result_by_regions.reset_index(),
                  on=['code_reg', 'name_reg']).set_index('code_reg')
    df['ratio'] = df['Choice A']/(df['Choice A']+df['Choice B'])
    gdf = gpd.GeoDataFrame(df)
    gpd.GeoDataFrame.plot(gdf, column='ratio')
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
