# noqa: D100
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.read_csv("data/referendum.csv", sep=';')
    regions = pd.read_csv("data/regions.csv", sep=",")
    departments = pd.read_csv("data/departments.csv", sep=",")
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    df = pd.merge(regions, departments, left_on='code',
                  right_on='region_code', how='inner')
    df = df[['region_code', 'name_x', 'code_y', 'name_y']]
    df.rename(columns={'region_code': 'code_reg', 'name_x': 'name_reg',
                       'code_y': 'code_dep',
                       'name_y': 'name_dep'}, inplace=True)

    return df


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum['Department code'] = referendum['Department code'].apply(
        lambda x: x.zfill(2))
    df = pd.merge(regions_and_departments, referendum,
                  left_on='code_dep', right_on='Department code')

    return df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    df = referendum_and_areas.groupby(['code_reg', 'name_reg'],
                                      as_index=False)[['Registered',
                                                       'Abstentions',
                                                       'Null',
                                                       'Choice A',
                                                       'Choice B']].sum()
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
    gp = gpd.read_file("data/regions.geojson")
    gp.rename(columns={"code": "code_reg"}, inplace=True)
    gp = pd.merge(gp, referendum_result_by_regions, on="code_reg")
    gp["ratio"] = gp["Choice A"] / \
        (gp["Registered"] - gp["Abstentions"] - gp['Null'])
    gp.plot(column="ratio",
            legend="True",
            legend_kwds={'label': "Rate of Choice A"})
    return gp


if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(df_reg, df_dep)
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments)
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas)
    plot_referendum_map(referendum_results)
    plt.show()
