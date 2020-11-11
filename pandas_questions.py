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
    """Load data from the CSV files referundum/regions/departments.
    """
    referendum = pd.read_csv("data/referendum.csv", delimiter=";")
    regions = pd.read_csv("data/regions.csv", delimiter=",")
    departments = pd.read_csv("data/departments.csv", delimiter=",")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    df = pd.merge(
        departments,
        regions,
        how='left',
        left_on='region_code',
        right_on='code')
    df = df.loc[:, ['region_code', 'name_y', 'code_x', 'name_x']]
    df = df.rename(
        columns={
            'region_code': 'code_reg',
            'name_y': 'name_reg',
            'code_x': 'code_dep',
            'name_x': 'name_dep'})
    return df


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum2 = referendum.copy()
    referendum2["Department code"] = referendum2["Department code"].apply(
        lambda x: '0' + x if(len(x) == 1) else x)

    df = pd.merge(
        referendum2,
        regions_and_departments,
        how='left',
        left_on='Department code',
        right_on='code_dep')
    df = df.dropna()
    return df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    df = referendum_and_areas.copy()
    df = df.drop(['Department code', 'Department name', 'Town code',
                  'Town name', 'code_dep', 'name_dep'], axis=1)
    df = df.groupby(['name_reg', 'code_reg']).sum()
    df = df.reset_index(level='name_reg')
    return df


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    gpd_France = gpd.read_file("data/regions.geojson")
    df = pd.merge(
        referendum_result_by_regions,
        gpd_France,
        left_on='name_reg',
        right_on='nom',
        how='left').drop(
        'nom',
        axis=1).set_index('code')
    df['ratio'] = df['Choice A'] / \
        (df['Choice A'] + df['Choice B'] + df['Null'])
    gpd_result = gpd.GeoDataFrame(df)

    fig, ax = plt.subplots(1, 1)
    ax.set_axis_off()
    fig.suptitle('Result of the referendum', fontsize=20)
    ax.set_title('Ratio of choice A per region of France')
    gpd_result.plot(
        column='ratio',
        ax=ax,
        legend=True,
        cmap='OrRd',
        figsize=(
            10,
            7))

    return gpd_result


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
