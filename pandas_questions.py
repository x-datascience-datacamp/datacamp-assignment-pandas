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
    referendum = pd.DataFrame(pd.read_csv('data/referendum.csv', error_bad_lines=False, sep =';'))
    regions = pd.DataFrame(pd.read_csv('data/regions.csv', error_bad_lines=False))
    departments = pd.DataFrame(pd.read_csv('data/departments.csv' , error_bad_lines=False))
    regions.rename(columns={'code':'code_reg',
                          'name':'name_reg'}, 
                 inplace=True)
    departments.rename(columns={'code':'code_dep',
                                'region_code' : 'code_reg',
                                'name':'name_dep'}, 
                 inplace=True)
    referendum.rename(columns ={'Department code':'code_dep'}, 
                      inplace=True)
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    

    regions_and_departments = pd.merge(regions, departments, on = "code_reg", how = "inner")

    return pd.DataFrame(regions_and_departments[['code_reg', 'name_reg', 'code_dep', 'name_dep']])


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    
    regions_and_departments = regions_and_departments[regions_and_departments['code_reg'] != "COM"]
    referendum_and_areas = pd.merge(regions_and_departments, referendum, on = 'code_dep', how = 'inner')
    return pd.DataFrame(referendum_and_areas)


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    referendum_and_areas = referendum_and_areas[['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']]
    referendum_res_by_regions = referendum_and_areas.groupby(by = ['name_reg']).sum()
    return pd.DataFrame(referendum_res_by_regions)


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    mapRegion =gpd.GeoDataFrame(gpd.read_file('data/regions.geojson'))
    mapRegion.rename(columns = {'nom' : 'name_reg'}, inplace = True)
    mapRegion = mapRegion.merge(referendum_results, on = 'name_reg', how = 'inner')
    mapRegion['ratio'] = mapRegion['Choice A']/mapRegion['Registered']
    mapRegion.plot(column = 'ratio')
    return gpd.GeoDataFrame(mapRegion)


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
    plot_referendum_map(referendum_results)
    plt.show()
