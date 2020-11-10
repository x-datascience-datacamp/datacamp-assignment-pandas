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
    p = pd.merge(departments, regions, left_on='region_code', right_on='code')
    p.rename(columns={'region_code': 'code_reg', 'name_y': 'name_reg',
                      'code_x': 'code_dep',
                      'name_x': 'name_dep'}, inplace=True)
    p = p[['code_reg', 'name_reg', 'code_dep', 'name_dep']]
    return (p)


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.
    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum = referendum[referendum["Department name"] !=
                            "FRANCAIS DE L'ETRANGER"]
    referendum = referendum[referendum["Department code"].isin(
        referendum["Department code"].unique()[:96])]
    dep = []
    for depcode in referendum["Department code"]:
        if len(depcode) == 1:
            dep.append("0" + depcode)
        else:
            dep.append(depcode)
    referendum["Department code"] = dep
    p = pd.merge(referendum, regions_and_departments,
                 left_on='Department code', right_on='code_dep')
    return pd.DataFrame(p)


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    p = referendum_and_areas[['code_reg', 'name_reg', 'Registered',
                              'Abstentions', 'Null', 'Choice A', 'Choice B']]
    p = p.groupby(['code_reg']).sum()
    p = p.reset_index('code_reg')
    p = pd.merge(referendum_and_areas[['code_reg', 'name_reg']], p,
                 on='code_reg')
    p = p.drop_duplicates()
    p = p.set_index('code_reg')
    return (p)


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo = 'data/regions.geojson'
    data = gpd.read_file(geo)
    fig = pd.merge(referendum_result_by_regions, data, left_on="code_reg",
                   right_on="code")
    fig['ratio'] = fig['Choice A'] / (fig['Choice A'] + fig['Choice B'])
    gpd.GeoDataFrame(fig).plot(column='ratio')
    return gpd.GeoDataFrame(fig)


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
