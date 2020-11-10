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
    """Load data from the CSV files referendum/regions/departments."""
    referendum = pd.DataFrame(pd.read_csv(r'data/referendum.csv', sep=';'))
    regions = pd.DataFrame(pd.read_csv(r'data/regions.csv', sep=','))
    departments = pd.DataFrame(pd.read_csv(r'data/departments.csv', sep=','))

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions2, departments2 = regions.copy(), departments.copy()
    regions2 = regions2.rename({'id': 'id_reg',
                                'code': 'code_reg',
                                'name': 'name_reg',
                                'slug': 'slug_reg'}, axis=1)
    departments2 = departments2.rename({'id': 'id_dep',
                                        'region_code': 'code_reg',
                                        'code': 'code_dep',
                                        'name': 'name_dep',
                                        'slug': 'slug_dep'}, axis=1)
    merged = pd.merge(regions2, departments2, on='code_reg')

    merged = merged[['code_reg', 'name_reg', 'code_dep', 'name_dep']]
    merged['code_dep'] = merged['code_dep'].replace({'01': '1', '02': '2',
                                                     '03': '3', '04': '4',
                                                     '05': '5', '06': '6',
                                                     '07': '7', '08': '8',
                                                     '09': '9'})

    return merged


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    ref = referendum.copy()
    r_and_d = regions_and_departments.copy()
    merged = pd.merge(ref, r_and_d,
                      left_on='Department code', right_on='code_dep')
    return merged


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    ref_and_areas = referendum_and_areas.drop(['Town code'], axis=1)
    ref_and_areas = ref_and_areas.groupby(['code_reg', 'name_reg']).sum()
    ref_and_areas = ref_and_areas.reset_index(level=['name_reg'])
    return ref_and_areas


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    filename = 'data/regions.geojson'
    file = open(filename)
    reg = gpd.read_file(file)
    join = pd.merge(reg, referendum_result_by_regions,
                    left_on='code', right_on='code_reg')
    join['ratio'] = join['Choice A'] / (join['Choice A'] + join['Choice B'])
    join.plot(column='ratio')
    return gpd.GeoDataFrame(join)


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
