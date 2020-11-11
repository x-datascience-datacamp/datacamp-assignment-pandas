
"""Plotting referendum results in pandas."""
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
"""
In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png
To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas` o.
"""


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    filename_ref = "/Users/Aris/datacamp-assignment-pandas/data/referendum.csv"
    filename_reg = "/Users/Aris/datacamp-assignment-pandas/data/regions.csv"
    filename_dep = \
        "/Users/Aris/datacamp-assignment-pandas/data/departments.csv"
    referendum = pd.DataFrame(pd.read_csv(filename_ref, sep=";"))
    regions = pd.DataFrame(pd.read_csv(filename_reg, sep=","))
    departments = pd.DataFrame(pd.read_csv(filename_dep, sep=","))
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame."""
    """
    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions.rename(columns={"code": "code_reg"}, inplace=True)
    departments.rename(columns={"region_code": "code_reg"}, inplace=True)
    dataset = pd.merge(regions.loc[:, ["code_reg", "name"]],
                       departments.loc[:, ["code_reg", "code", "name"]],
                       on="code_reg")
    dataset.columns = ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    return dataset


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame."""
    """You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    columnorder = ['code_dep', 'code_reg', 'name_reg', 'name_dep']
    regions_and_departments = regions_and_departments[columnorder]
    todrop = referendum[referendum["Department code"]
                        .str.startswith('Z').isin([True])].index
    todrop2 = regions_and_departments[regions_and_departments["code_reg"]
                                      .str.startswith('C').isin([True])].index
    referendum = referendum.drop(index=todrop)
    regions_and_departments = regions_and_departments.drop(index=todrop2)
    toreplace = regions_and_departments.loc[regions_and_departments["code_dep"]
                                            .str.startswith('0').isin([True]),
                                            "code_dep"].index
    regions_and_departments.iloc[toreplace, 0] =  \
        regions_and_departments.iloc[toreplace, 0].str.replace('0', '')
    newdf = pd.merge(referendum, regions_and_departments,
                     left_on="Department code", right_on="code_dep",
                     how='left')
    return newdf


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region."""
    """The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    columns = ['code_reg', 'name_reg', 'Registered', 'Abstentions',
               'Null', 'Choice A', 'Choice B']
    df = referendum_and_areas[columns]
    df = df.groupby(["code_reg", "name_reg"]).sum()
    df = df.reset_index(level=1)
    return df


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum."""
    """* Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' ove all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    filenamegpd = "/Users/Aris/datacamp-assignment-pandas/data/regions.geojson"
    df = gpd.read_file(filenamegpd)
    df.rename(columns={"nom": "name_reg"}, inplace=True)
    df_2 = pd.merge(referendum_result_by_regions, df, on='name_reg',
                    how='left')
    df_2["ratio"] = df_2["Choice A"]/df_2.drop(columns=["Abstentions", "Null",
                                                        "Registered"])\
        .sum(axis=1)
    df_2 = gpd.GeoDataFrame(df_2)
    df_2.plot(column="ratio", legend=True)
    return df_2


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
