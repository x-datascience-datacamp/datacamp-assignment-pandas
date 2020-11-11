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
    referendum = pd.read_csv("./data/referendum.csv", sep=";")
    regions = pd.read_csv("./data/regions.csv")
    departments = pd.read_csv("./data/departments.csv")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    new_columns1 = {"code": "code_reg", "name": "name_reg"}
    new_columns2 = {"region_code": "code_reg", "code": "code_dep",
                    "name": "name_dep"}
    reg = regions[['code', 'name']].rename(columns=new_columns1)
    dep = departments[['region_code',
                       'code', 'name']].rename(columns=new_columns2)
    reg_n_dep = pd.merge(dep, reg, on='code_reg',
                         how='left')
    return reg_n_dep


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    r_n_d = regions_and_departments.copy()
    r_n_d = r_n_d.replace({'code_dep':
                          {"0"+str(i): str(i) for i in range(1, 10)}})
    ref_n_area = pd.merge(referendum, r_n_d, right_on='code_dep',
                          left_on='Department code', how='inner')

    return ref_n_area


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    columns = ['name_reg', 'Registered', 'Abstentions',
               'Null', 'Choice A', 'Choice B']
    groups = ['code_reg', 'name_reg']
    ref_by_reg = referendum_and_areas.groupby(groups)[columns].sum()
    ref_by_reg.reset_index(groups, inplace=True)
    ref_by_reg.set_index('code_reg', inplace=True)

    return ref_by_reg


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.pu
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    map_data = gpd.read_file("./data/regions.geojson")
    map_n_res = pd.merge(map_data, referendum_result_by_regions,
                         left_on='code', right_on='code_reg', how='inner')
    expressed = ['Choice A', 'Choice B']
    total_exp = map_n_res[expressed].sum(axis=1)
    a_rate = map_n_res['Choice A'] / total_exp
    map_n_res['ratio'] = a_rate
    map_n_res.plot(column='ratio', legend=True, cmap='seismic_r', vmin=0,
                   vmax=1, legend_kwds={'label': "Rate of Choice A by region"},
                   edgecolor='k')

    return map_n_res


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
