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
    """
    Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    left_reg = regions.copy().loc[:, ['code', 'name']]
    left_reg.columns = ['code_reg', 'name_reg']

    right_dep = departments.copy().loc[:, ['region_code', 'code', 'name']]
    right_dep.columns = ['code_reg', 'code_dep', 'name_dep']

    res = pd.merge(left=left_reg, right=right_dep, on='code_reg', how='left')

    return pd.DataFrame(res)


def merge_referendum_and_areas(referendum, regions_and_departments):
    """
    Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    # extra represent the extrateritorrial councils with as referendum
    extra = referendum['Department code'].str.startswith('Z')
    left = referendum.drop(referendum.loc[extra].index)
    left['code_dep'] = left['Department code']

    right = regions_and_departments.copy()
    DOM_TOM_COM = [
        "Guadeloupe", "Martinique", "Guyane", "La Réunion", "Mayotte",
        "Collectivités d'Outre-Mer"
        ]
    index_dom = right['name_reg'].isin(DOM_TOM_COM)
    right = right.drop(right.loc[index_dom].index)

    # We need the same code indexation for both data sets
    clean_code = right['code_dep'].values
    for i in range(len(clean_code)):
        # We want 01 to be 1, O2 to be 2 ..
        if clean_code[i] != '2A' and clean_code[i] != '2B':
            clean_code[i] = str(int(clean_code[i]))
    right['code_dep'] = clean_code

    res = pd.merge(left, right, on='code_dep', how='left')

    return pd.DataFrame(res)


def compute_referendum_result_by_regions(referendum_and_areas):
    """
    Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    res = referendum_and_areas[[
        'code_reg', 'name_reg', 'Registered', 'Abstentions', 'Null',
        'Choice A', 'Choice B'
        ]]
    res = res.groupby(by=['code_reg', 'name_reg'], as_index=False)[
        'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B'
        ].sum().set_index('code_reg')

    return pd.DataFrame(res)


def plot_referendum_map(referendum_result_by_regions):
    """
    Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    regions_geo = gpd.read_file(
        'data/regions.geojson'
        )
    regions_geo = regions_geo.set_index('code')
    res = pd.merge(
        referendum_result_by_regions, regions_geo,
        left_index=True, right_index=True
        )
    res.drop('nom', axis=1, inplace=True)
    res['ratio'] = res['Choice A'] / (
        res['Choice A'] + res['Choice B']
        )

    return gpd.GeoDataFrame(res)


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
