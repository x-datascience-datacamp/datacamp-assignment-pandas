import numpy as np
import pandas as pd
import geopandas as gpd

from pandas_questions import load_data
from pandas_questions import plot_referendum_map
from pandas_questions import merge_referendum_and_areas
from pandas_questions import merge_regions_and_departments
from pandas_questions import compute_referendum_result_by_regions


def test_load_data():
    referendum, regions, departments = load_data()

    df_ref = pd.read_csv('data/referendum.csv', sep=';')
    assert set(referendum.columns) == set(df_ref.columns)

    df_reg = pd.read_csv('data/regions.csv')
    assert set(regions.columns) == set(df_reg.columns)

    df_dep = pd.read_csv('data/departments.csv')
    assert set(departments.columns) == set(df_dep.columns)


def test_merge_regions_and_departments():

    referendum, df_reg, df_dep = load_data()

    regions_and_departments = merge_regions_and_departments(
        df_reg, df_dep
    )

    assert set(regions_and_departments.columns) == set([
        'code_reg', 'name_reg', 'code_dep', 'name_dep'
    ])
    assert regions_and_departments.shape == (109, 4)


def test_merge_referendum_and_area():
    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(
        df_reg, df_dep
    )
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )

    # check that there is no missing values
    assert referendum_and_areas.shape == referendum_and_areas.dropna().shape, (
        "There should be no missing values in the DataFrame. Use dropna?"
    )

    assert set(referendum_and_areas.columns) == set([
        'Department code', 'Department name', 'Town code', 'Town name',
        'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B',
        'code_dep', 'code_reg', 'name_reg', 'name_dep'
    ])
    assert referendum_and_areas.shape == (36565, 13), (
        "Shape of the DataFrame should be (36565, 13). "
        "Check for mismatch in column formats."
    )


def test_compute_referendum_result_by_regions():
    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(
        df_reg, df_dep
    )
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_result_by_regions = compute_referendum_result_by_regions(
        referendum_and_areas
    )

    # Check result shape
    assert set(referendum_result_by_regions.columns) == set([
        'name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B'
    ]), (
        'To keep the name of the region, you can use either another merge or '
        'a clever groupby.'
    )
    assert referendum_result_by_regions.shape == (13, 6)

    # check that some of the values
    referendum_result_by_regions = referendum_result_by_regions.set_index(
        'name_reg'
    )
    assert referendum_result_by_regions['Registered'].sum() == 43_262_592
    assert referendum_result_by_regions.loc[
        'Normandie', 'Abstentions'] == 426_075
    assert referendum_result_by_regions.loc[
        'Grand Est', 'Choice A'] == 1_088_684
    assert referendum_result_by_regions.loc['Occitanie', 'Null'] == 62_732


def test_plot_referendum_map():
    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(
        df_reg, df_dep
    )
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_result_by_regions = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    gdf_referendum = plot_referendum_map(referendum_result_by_regions)

    assert isinstance(gdf_referendum, gpd.GeoDataFrame), (
        "The return object should be a GeoDataFrame, not a "
        f"{type(gdf_referendum)}."
    )
    assert 'ratio' in gdf_referendum.columns
    gdf_referendum = gdf_referendum.set_index('name_reg')
    assert np.isclose(gdf_referendum['ratio'].loc['Normandie'], 0.427467)
