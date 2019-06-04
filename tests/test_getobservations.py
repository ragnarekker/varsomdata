import unittest as ut
from varsomdata import getobservations as go
import pandas as pd


class TestGetSingeFormsMethods(ut.TestCase):

    def test_get_general_observation(self):
        general_obs = go.get_general_observation('2018-01-20', '2018-02-01')
        general_obs_df = go.get_general_observation('2018-01-20', '2018-02-01', output='DataFrame')
        general_obs_count = go.get_general_observation('2018-01-20', '2018-02-01', output='Count')
        self.assertEqual(len(general_obs), general_obs_count)
        self.assertIsInstance(general_obs_df, pd.DataFrame)

    def test_get_incident(self):
        incident = go.get_incident('2012-03-01', '2012-03-10')
        incident_df = go.get_incident('2012-03-01', '2012-03-10', output='DataFrame')
        incident_count = go.get_incident('2012-03-01', '2012-03-10', output='Count')
        self.assertEqual(len(incident), incident_count)
        self.assertIsInstance(incident_df, pd.DataFrame)

    def test_danger_sign(self):
        danger_signs = go.get_danger_sign('2017-12-13', '2017-12-16', geohazard_tids=10)
        danger_signs_df = go.get_danger_sign('2017-12-13', '2017-12-16', output='DataFrame')
        danger_signs_count = go.get_danger_sign('2017-12-13', '2017-12-16', output='Count')
        self.assertTrue(danger_signs_count <= len(danger_signs) <= 3*danger_signs_count)
        self.assertIsInstance(danger_signs_df, pd.DataFrame)

    def test_get_damage_observation(self):
        damages = go.get_damage_observation('2017-01-01', '2018-02-01')
        damages_df = go.get_damage_observation('2017-01-01', '2018-02-01', output='DataFrame')
        damages_count = go.get_damage_observation('2017-01-01', '2018-02-01', output='Count')
        self.assertTrue(damages_count <= len(damages) <= 3*damages_count)
        self.assertIsInstance(damages_df, pd.DataFrame)

    def test_weather_observation(self):
        weather = go.get_weather_observation('2018-01-28', '2018-02-01')
        weather_df = go.get_weather_observation('2018-01-28', '2018-02-01', output='DataFrame')
        weather_count = go.get_weather_observation('2018-01-28', '2018-02-01', output='Count')
        self.assertEqual(len(weather), weather_count)
        self.assertIsInstance(weather_df, pd.DataFrame)

    def test_get_snow_surface_observation(self):
        snow_surface = go.get_snow_surface_observation('2018-01-29', '2018-02-01')
        snow_surface_df = go.get_snow_surface_observation('2018-01-29', '2018-02-01', output='DataFrame')
        snow_surface_conut = go.get_snow_surface_observation('2018-01-29', '2018-02-01', output='Count')
        self.assertEqual(len(snow_surface), snow_surface_conut)
        self.assertIsInstance(snow_surface_df, pd.DataFrame)

    def test_get_tests(self):
        tests = go.get_tests('2018-01-25', '2018-02-01')
        tests_df = go.get_tests('2018-02-01', '2018-02-05', output='DataFrame')
        tests_count = go.get_tests('2018-02-01', '2018-02-05', output='Count')
        self.assertTrue(tests_count <= len(tests) <= 3*tests_count)
        self.assertIsInstance(tests_df, pd.DataFrame)

    def test_avalanche_obs(self):
        avalanche_obs = go.get_avalanche('2015-03-01', '2015-03-10')
        avalanche_obs_df = go.get_avalanche('2015-03-01', '2015-03-10', output='DataFrame')
        avalanche_obs_count = go.get_avalanche('2015-03-01', '2015-03-10', output='Count')
        self.assertEqual(len(avalanche_obs), avalanche_obs_count)
        self.assertIsInstance(avalanche_obs_df, pd.DataFrame)

    def test_avalanche_activity(self):
        from_date, to_date = '2015-03-01', '2015-03-10'

        avalanche_activity = go.get_avalanche_activity(from_date, to_date)
        avalanche_activity_df = go.get_avalanche_activity(from_date, to_date, output='DataFrame')
        avalanche_activity_count = go.get_avalanche_activity(from_date, to_date, output='Count')

        self.assertIsInstance(avalanche_activity[0], go.AvalancheActivityObs)
        self.assertIsInstance(avalanche_activity_df, pd.DataFrame)

        avalanche_activity_obs = go.get_data(from_date, to_date, registration_types=27)
        self.assertEqual(avalanche_activity_count, len(avalanche_activity_obs))

    def test_avalanche_activity_2(self):
        from_date, to_date = '2017-03-01', '2017-03-10'

        avalanche_activity_2 = go.get_avalanche_activity_2(from_date, to_date)
        avalanche_activity_2_df = go.get_avalanche_activity_2(from_date, to_date, output='DataFrame')
        avalanche_activity_2_count = go.get_avalanche_activity_2(from_date, to_date, output='Count')

        self.assertIsInstance(avalanche_activity_2[0], go.AvalancheActivityObs2)
        self.assertIsInstance(avalanche_activity_2_df, pd.DataFrame)

        avalanche_activity_2_obs = go.get_data(from_date, to_date, registration_types=33)
        self.assertEqual(avalanche_activity_2_count, len(avalanche_activity_2_obs))

    def test_get_avalanche_evaluation(self):
        avalanche_evaluations = go.get_avalanche_evaluation('2012-03-01', '2012-03-10')
        avalanche_evaluations_df = go.get_avalanche_evaluation('2012-03-01', '2012-03-10', output='DataFrame')
        avalanche_evaluations_count = go.get_avalanche_evaluation('2012-03-01', '2012-03-10', output='Count')
        self.assertEqual(len(avalanche_evaluations), avalanche_evaluations_count)
        self.assertIsInstance(avalanche_evaluations_df, pd.DataFrame)

    def test_get_avalanche_evaluation_2(self):
        avalanche_evaluations_2 = go.get_avalanche_evaluation_2('2013-03-01', '2013-03-10')
        avalanche_evaluations_2_df = go.get_avalanche_evaluation_2('2013-03-01', '2013-03-10', output='DataFrame')
        avalanche_evaluations_2_count = go.get_avalanche_evaluation_2('2013-03-01', '2013-03-10', output='Count')
        self.assertEqual(len(avalanche_evaluations_2), avalanche_evaluations_2_count)
        self.assertIsInstance(avalanche_evaluations_2_df, pd.DataFrame)

    def test_get_avalanche_evaluation_3(self):
        avalanche_evaluations_3 = go.get_avalanche_evaluation_3('2017-03-01', '2017-03-10')
        avalanche_evaluations_3_df = go.get_avalanche_evaluation_3('2017-03-01', '2017-03-10', output='DataFrame')
        avalanche_evaluations_3_count = go.get_avalanche_evaluation_3('2017-03-01', '2017-03-10', output='Count')
        self.assertEqual(len(avalanche_evaluations_3), avalanche_evaluations_3_count)
        self.assertIsInstance(avalanche_evaluations_3_df, pd.DataFrame)

    def test_get_avalanche_problem_2(self):
        problems = go.get_avalanche_problem_2('2017-03-01', '2017-03-10')
        problems_df = go.get_avalanche_problem_2('2017-03-01', '2017-03-10', output='DataFrame')
        problems_count = go.get_avalanche_problem_2('2017-03-01', '2017-03-10', output='Count')
        self.assertTrue(problems_count <= len(problems) <= 3*problems_count)
        self.assertIsInstance(problems_df, pd.DataFrame)

    def test_get_snow_profile(self):
        snow_profiles = go.get_snow_profile('2018-12-13', '2018-12-16')
        snow_profiles_df = go.get_snow_profile('2018-12-13', '2018-12-16', output='DataFrame')
        snow_profiles_count = go.get_snow_profile('2018-12-13', '2018-12-16', output='Count')
        self.assertEqual(len(snow_profiles), snow_profiles_count)
        self.assertIsInstance(snow_profiles_df, pd.DataFrame)

    def test_get_ice_thickness(self):
        ice_thicks = go.get_ice_thickness('2018-01-20', '2018-02-10')
        ice_thicks_df = go.get_ice_thickness('2018-01-20', '2018-02-10', output='DataFrame')
        ice_thicks_count = go.get_ice_thickness('2018-01-20', '2018-02-10', output='Count')
        self.assertEqual(len(ice_thicks), ice_thicks_count)
        self.assertIsInstance(ice_thicks_df, pd.DataFrame)

    def test_get_ice_cover(self):
        ice_cover = go.get_ice_cover('2012-03-01', '2012-03-10')
        ice_cover_df = go.get_ice_cover('2012-03-01', '2012-03-10', output='DataFrame')
        ice_cover_count = go.get_ice_cover('2012-03-01', '2012-03-10', output='Count')
        self.assertEqual(len(ice_cover), ice_cover_count)
        self.assertIsInstance(ice_cover_df, pd.DataFrame)

    def test_get_water_level(self):
        water_levels = go.get_water_level('2015-01-01', '2016-01-01')
        water_levels_df = go.get_water_level('2015-01-01', '2016-01-01', output='DataFrame')
        water_levels_count = go.get_water_level('2015-01-01', '2016-01-01', output='Count')
        self.assertEqual(len(water_levels), water_levels_count)
        self.assertIsInstance(water_levels_df, pd.DataFrame)

    def test_get_water_level_2(self):
        new_water_levels = go.get_water_level_2('2017-06-01', '2018-02-01')
        new_water_levels_df = go.get_water_level_2('2017-06-01', '2018-02-01', output='DataFrame')
        new_water_levels_count = go.get_water_level_2('2017-06-01', '2018-02-01', output='Count')
        self.assertEqual(len(new_water_levels), new_water_levels_count)
        self.assertIsInstance(new_water_levels_df, pd.DataFrame)

    def test_get_land_slide_obs(self):
        land_slides = go.get_land_slide_obs('2018-01-01', '2018-02-01')
        land_slides_df = go.get_land_slide_obs('2018-01-01', '2018-02-01', output='DataFrame')
        land_slides_count = go.get_land_slide_obs('2018-01-01', '2018-02-01', output='Count')
        self.assertEqual(len(land_slides), land_slides_count)
        self.assertIsInstance(land_slides_df, pd.DataFrame)


if __name__ == '__main__':
    ut.main()
