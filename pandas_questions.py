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
import geodaisy.converters as convert
import shapely.wkt


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    path_dep = '''/Users/maximeberillon/Documents/Data Camp/
                  datacamp-assignment-pandas/data/departments.csv'''
    path_ref = '''/Users/maximeberillon/Documents/Data Camp/
                  datacamp-assignment-pandas/data/referendum.csv'''
    path_reg = '''/Users/maximeberillon/Documents/Data Camp/
                  datacamp-assignment-pandas/data/regions.csv'''
    referendum = pd.read_csv(path_ref, delimiter=';')
    regions = pd.read_csv(path_reg)
    departments = pd.read_csv(path_dep)
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    df = pd.merge(regions[['code', 'name']],
                  departments[['region_code', 'code', 'name']],
                  left_on='code',
                  right_on='region_code',
                  how='right') \
        .drop(columns=['region_code']) \
        .rename(columns={'code_x': 'code_reg', 'name_x': 'name_reg',
                         'code_y': 'code_dep', 'name_y': 'name_dep'})
    return df


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    df = pd.merge(regions_and_departments,
                  referendum,
                  left_on='code_dep',
                  right_on='Department code',
                  how='left') \
        .drop(columns=['Department code', 'Department name'])
    result = df[~df['code_reg'].isin(['01', '02', '03', '04', '06', 'COM'])]
    return result


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    df = referendum_and_areas
    result = df.groupby(['code_reg', 'name_reg'],
                        as_index=False)['Registered',
                                        'Abstentions',
                                        'Null',
                                        'Choice A',
                                        'Choice B'] \
        .sum() \
        .set_index('code_reg')
    return result


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    # Loading the geographic data
    df = pd.read_json(
        '/Users/maximeberillon/Documents/Data Camp/ \
        datacamp-assignment-pandas/data/regions.geojson')
    df2 = pd.concat([df.drop(['features'], axis=1),
                     df['features'].apply(pd.Series)], axis=1)
    df3 = pd.concat([df2.drop(['geometry'], axis=1),
                     df2['geometry'].apply(pd.Series)], axis=1)
    df4 = pd.concat([df3.drop(['properties'], axis=1),
                     df3['properties'].apply(pd.Series)], axis=1)
    referendum_result_by_regions = pd.merge(referendum_result_by_regions,
                                            df4,
                                            left_on='code_reg',
                                            right_on='code',
                                            how='left') \
        .drop(columns=['type', 'nom']) \
        .rename(columns={'code': 'code_reg'})
    referendum_result_by_regions['geometry'] = \
        referendum_result_by_regions['geometry'] \
        .apply((lambda x: shapely.wkt.loads(convert.geojson_to_wkt(x))))
    gpd_referendum_result_by_regions = gpd.GeoDataFrame(
        referendum_result_by_regions,
        geometry=referendum_result_by_regions['geometry'])
    gpd_referendum_result_by_regions['ratio'] = \
        gpd_referendum_result_by_regions['Choice A'] / \
        (gpd_referendum_result_by_regions['Choice A'] +
         gpd_referendum_result_by_regions['Choice B'] +
         gpd_referendum_result_by_regions['Null'])
    gpd_referendum_result_by_regions.plot(column='ratio')
    return gpd_referendum_result_by_regions


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
