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
    referendum = pd.read_csv('./data/referendum.csv', ';')
    regions = pd.read_csv('./data/regions.csv')
    departments = pd.read_csv('./data/departments.csv')
    # we add a 0 to the 9 first dept. codes of referendum dataframe
    referendum['Department code'] = (referendum['Department code']
                                     .apply(lambda x: x.rjust(2, '0')))
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    df = pd.merge(regions[['code','name']], 
                  departments[['region_code','code','name']],
                  left_on='code', right_on='region_code', indicator=False,
                  suffixes=('_reg','_dep')).drop(['region_code'],axis=1)
    return df


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    # we sort 'regs._and_depts.' dataframe by 'code_dep'
    regions_and_departments = (regions_and_departments
                               .sort_values(by='code_dep')
                               .reset_index(drop=True))
    # then we can take the first 96 depts.
    # which corresponds to metropolitan France
    regions_and_departments = regions_and_departments[0:96]
    df = pd.merge(regions_and_departments, referendum, 
                  left_on='code_dep', right_on='Department code', 
                  indicator=False)
    return df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    df = referendum_and_areas.groupby(['code_reg','name_reg'], 
                                      as_index=False)[
                                      ['Registered','Abstentions', 'Null', 
                                       'Choice A', 'Choice B']].sum()
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
    reg = gpd.read_file('./data/regions.geojson')
    reg.set_index('code', inplace=True)
    df = pd.merge(referendum_result_by_regions, reg, how='left', 
                  left_index=True, right_index=True)
    total = df['Choice A'] + df['Choice B']
    df['ratio'] = df['Choice A'] / total
    # we recreate our GeoDataframe
    gf = gpd.GeoDataFrame(df, geometry=df.geometry)
    gf.plot(column='ratio', legend=True,
            legend_kwds={'label': "Ratio of choice A over expressed ballots"})
    return gf


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
