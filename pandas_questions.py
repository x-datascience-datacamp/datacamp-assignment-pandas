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
    ref = pd.read_csv('data/referendum.csv', sep=';')
    regions = pd.read_csv('data/regions.csv')
    departments = pd.read_csv('data/departments.csv')
    return ref, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    d = pd.DataFrame({
        'code_dep': departments["code"],
        'name_dep': departments["name"],
        'code_reg': departments["region_code"]
    })
    d2 = pd.DataFrame({
        'name_reg': regions["name"],
        'code_reg': regions["code"]
    })
    return d.merge(d2, on='code_reg')


def merge_referendum_and_areas(ref, reg_and_dep):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    reg_and_dep["code_dep"] = reg_and_dep["code_dep"].apply(lambda x : x.lstrip('0'))
    m = ref.merge(reg_and_dep, how="outer", left_on='Department code', right_on='code_dep')
    return m.dropna()


def compute_referendum_result_by_regions(reg_and_area):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    return reg_and_area.groupby('name_reg').sum()


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    reg_map = gpd.read_file('data/regions.geojson')
    reg_map['name_reg'] = reg_map['nom']
    merged = gpd.GeoDataFrame(referendum_result_by_regions.merge(reg_map, right_on='nom', left_on='name_reg'))
    merged['ratio'] = merged['Choice A'] / (merged['Choice A'] + merged['Choice B'])
    merged.plot(column='ratio', legend=True)
    plt.show()
    return merged


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
