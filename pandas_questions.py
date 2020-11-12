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
    referendum = pd.DataFrame(pd.read_csv('data/referendum.csv', sep=';'))
    regions = pd.DataFrame(pd.read_csv('data/regions.csv'))
    departments = pd.DataFrame(pd.read_csv('data/departments.csv'))

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    df = pd.merge(regions,
                  departments,
                  how='left',
                  left_on='code',
                  right_on='region_code',
                  suffixes=("_reg", "_dep"),
                  )
    df = df[['code_reg', 'name_reg', 'code_dep', 'name_dep']]
    return df


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum['Department code'] = referendum[
                                    'Department code'].apply(
                                        lambda x: str(x).zfill(2))
    df = pd.merge(regions_and_departments,
                  referendum,
                  how='left',
                  left_on='code_dep',
                  right_on='Department code'
                  )
    df.drop(df[df['code_reg'].isin(
                                   ('COM', '01', '02', '03', '04', '06')
                                  )
               ].index, inplace=True)

    return df.dropna()


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    columns = ['code_reg',
               'name_reg',
               'Registered',
               'Abstentions',
               'Null',
               'Choice A',
               'Choice B'
               ]
    df = referendum_and_areas[columns]
    df = df.groupby(['code_reg', 'name_reg']).sum(
                            numeric_only=True
                            ).reset_index().set_index('code_reg')

    return df


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    data = gpd.read_file('data/regions.geojson')
    data.drop(data[data['code'].isin(
                                     ('01', '02', '03', '04', '06')
                                    )
                   ].index, inplace=True)
    full_data = gpd.GeoDataFrame(pd.merge(
            referendum_result_by_regions.reset_index(),
            data,
            how='left',
            left_on='code_reg',
            right_on='code')
                                 )
    full_data.drop(columns=['nom', 'code'], inplace=True)
    full_data.loc[:, 'ratio'] = full_data['Choice A'] / full_data[
                    ['Choice A', 'Choice B']].sum(axis=1)
    full_data.plot(column='ratio')

    return full_data


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
