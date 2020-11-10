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
    referendum = pd.read_csv("data/referendum.csv", sep=";")
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    # Preliminar operations for regions data
    regions_ = regions.copy()
    regions_.rename(columns={'code': 'code_reg',
                             'name': 'name_reg'},
                    inplace=True)
    # Preliminar operations for department data
    departments_ = departments.copy()
    departments_.rename(columns={'region_code': 'code_reg',
                                 'code': 'code_dep',
                                 'name': 'name_dep'}, inplace=True)
    # Merge regions and departments
    df = pd.merge(regions_, departments_, how='left', on='code_reg')
    df = df.loc[:, ['code_reg', 'name_reg', 'code_dep', 'name_dep']]
    return df


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    reg_dep = regions_and_departments.copy()
    refe = referendum.copy()

    # Drop the lines relative to DOM-TOM-COM departments
    # For regions_and_departments
    reg_dep = reg_dep.loc[reg_dep['code_reg'] != 'COM']
    out = ['971', '972', '973', '974', '975', '976']
    reg_dep = reg_dep[~reg_dep['code_dep'].isin(out)]
    # For referendum
    out = ['ZA', 'ZB', 'ZC', 'ZD', 'ZM', 'ZN', 'ZP', 'ZS', 'ZW', 'ZX', 'ZZ']
    refe = refe[~refe['Department code'].isin(out)]

    # Uniformize the value of Department code
    old = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
    new = ['01', '02', '03', '04', '05', '06', '07', '08', '09']
    new_code = refe[['Department code']].replace(to_replace=old, value=new)
    refe[['Department code']] = new_code

    # Merge and drop na
    df = pd.merge(reg_dep, refe,
                  how="left", left_on='code_dep', right_on='Department code')
    df = df.dropna()

    return df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    df = referendum_and_areas.copy()

    # Keep a df with code_reg and name_reg
    df_name = df[['code_reg', 'name_reg']].drop_duplicates()
    df_name = df_name.set_index('code_reg')

    # Absolute count for desired variables
    df_abs_count = df.groupby('code_reg').sum()
    df_abs_count = df_abs_count[['Registered', 'Abstentions', 'Null',
                                 'Choice A', 'Choice B']]

    # Merge
    df = pd.merge(df_name, df_abs_count, on='code_reg')

    return df


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    # Import regions.geojson
    regions = gpd.read_file("data/regions.geojson")

    # Merge and set index at code
    df_merged = pd.merge(referendum_result_by_regions, regions,
                         left_on='code_reg', right_on='code')
    df_merged = df_merged.set_index('code')

    # Calculate and add the ratio
    expressed = (df_merged['Choice A']+df_merged['Choice B'])
    df_merged['ratio'] = df_merged['Choice A']/expressed

    # Transform the dataframe to GeoDataFrame
    df_merged = gpd.GeoDataFrame(df_merged, geometry='geometry')

    # Plot the rate of 'Choice A'
    df_merged.plot('ratio')
    plt.show()

    return df_merged


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
