import math

from parameterized import parameterized
from pytest import approx

from sdc_scissor.feature_extraction_api.equi_distance_strategy import EquiDistanceStrategy
from sdc_scissor.feature_extraction_api.angle_based_strategy import AngleBasedStrategy
from sdc_scissor.feature_extraction_api.feature_extraction import FeatureExtractor
from sdc_scissor.testing_api.test import Test


class TestFeatureExtraction:
    @parameterized.expand([
        [999, 20],
        [200, 12]
    ])
    def test_straight_road_equi_distance_strategy(self, distance, nr_segments):
        road_points = [[x, 0] for x in range(distance + 1)]
        test = Test(0, road_points, 'NOT_EXECUTED')
        segmentation_strategy = EquiDistanceStrategy(nr_segments)

        feature_extractor = FeatureExtractor(segmentation_strategy)

        road_features = feature_extractor.extract_features(test)

        assert road_features.direct_distance == distance
        assert road_features.road_distance == distance
        assert road_features.num_l_turns == 0
        assert road_features.num_r_turns == 0
        assert road_features.num_straights == nr_segments
        assert road_features.median_angle == 0
        assert road_features.total_angle == 0
        assert road_features.mean_angle == 0
        assert road_features.std_angle == 0
        assert road_features.max_angle == 0
        assert road_features.min_angle == 0
        assert road_features.median_pivot_off == 0
        assert road_features.mean_pivot_off == 0
        assert road_features.std_pivot_off == 0
        assert road_features.max_pivot_off == 0
        assert road_features.min_pivot_off == 0

    def test_90_degree_right_turn_only(self):
        nr_segments = 2
        road_points = []
        radius = 50
        angle = 90
        center_of_turn = (50, 0)

        for i in range(0, angle + 1, 1):
            x = -1 * radius * math.cos(math.radians(i))  # minus for right turn
            y = radius * math.sin(math.radians(i))

            # translation of coordinates
            x = x + center_of_turn[0]

            road_points.append([x, y])

        segmentation_strategy = EquiDistanceStrategy(nr_segments)

        feature_extractor = FeatureExtractor(segmentation_strategy)

        test = Test(0, road_points, 'NOT_EXECUTED')
        road_features = feature_extractor.extract_features(test)
        assert road_features.num_l_turns == 0
        assert road_features.num_r_turns == nr_segments
        assert road_features.num_straights == 0
        assert road_features.median_angle == approx(-angle / nr_segments, abs=2)
        assert road_features.total_angle == approx(-angle, abs=2)
        assert road_features.mean_angle == approx(-angle / nr_segments, abs=2)
        assert road_features.max_angle == approx(-angle / nr_segments, abs=2)
        assert road_features.min_angle == approx(-angle / nr_segments, abs=2)
        assert road_features.median_pivot_off == approx(radius, abs=2)
        assert road_features.mean_pivot_off == approx(radius, abs=2)
        assert road_features.max_pivot_off == approx(radius, abs=2)
        assert road_features.min_pivot_off == approx(radius, abs=2)

    def test_90_degree_left_turn_only(self):
        nr_segments = 1
        # nr_segments = 2
        # segmentation_strategy = EquiDistanceStrategy(nr_segments)
        segmentation_strategy = AngleBasedStrategy(angle_threshold=5, decision_distance=10)

        road_points = []
        radius = 50
        angle = 90
        center_of_turn = (0, 0)

        for i in range(0, angle + 1, 1):
            x = radius * math.cos(math.radians(i))  # minus for right turn
            y = radius * math.sin(math.radians(i))

            # translation of coordinates
            x = x + center_of_turn[0]

            road_points.append([x, y])

        test = Test(0, road_points, 'NOT_EXECUTED')
        feature_extractor = FeatureExtractor(segmentation_strategy)

        road_features = feature_extractor.extract_features(test)

        assert road_features.num_l_turns == nr_segments
        assert road_features.num_r_turns == 0
        assert road_features.num_straights == 0
        assert road_features.median_angle == approx(angle / nr_segments, abs=2)
        assert road_features.total_angle == approx(angle, abs=2)
        assert road_features.mean_angle == approx(angle / nr_segments, abs=2)
        assert road_features.max_angle == approx(angle / nr_segments, abs=2)
        assert road_features.min_angle == approx(angle / nr_segments, abs=2)
        assert road_features.median_pivot_off == approx(radius, abs=2)
        assert road_features.mean_pivot_off == approx(radius, abs=2)
        assert road_features.max_pivot_off == approx(radius, abs=2)
        assert road_features.min_pivot_off == approx(radius, abs=2)

    def test_left_then_right_turn_segments_90_degrees_each(self):
        nr_segments = 2
        road_points = []
        radius = 50
        angle = 90
        center_of_turn = (0, 0)

        # left turn
        for i in range(0, angle + 1, 1):
            x = radius * math.cos(math.radians(i))  # minus for right turn
            y = radius * math.sin(math.radians(i))

            # translation of coordinates
            x = x + center_of_turn[0]
            y = y + center_of_turn[1]

            road_points.append([x, y])

        # right turn
        center_of_turn = (x, y + radius)
        for i in range(1, angle + 1, 1):
            x = -radius * math.sin(math.radians(i))  # minus for right turn
            y = -radius * math.cos(math.radians(i))

            # translation of coordinates
            x = x + center_of_turn[0]
            y = y + center_of_turn[1]

            road_points.append([x, y])

        segmentation_strategy = EquiDistanceStrategy(nr_segments)
        feature_extractor = FeatureExtractor(segmentation_strategy)
        test = Test(0, road_points, 'NOT_EXECUTED')

        road_features = feature_extractor.extract_features(test)

        # pythagoras
        assert road_features.direct_distance == approx(math.sqrt(2 * ((2 * radius) ** 2)), abs=2)

        # half of a circle
        assert road_features.road_distance == approx(math.pi * radius, abs=2)
        assert road_features.num_l_turns == 1
        assert road_features.num_r_turns == 1
        assert road_features.num_straights == 0
        assert road_features.median_angle == approx(0, abs=2)
        assert road_features.total_angle == approx(0, abs=2)
        assert road_features.mean_angle == approx(0, abs=2)
        assert road_features.max_angle == approx(angle, abs=2)
        assert road_features.min_angle == approx(-angle, abs=2)
        assert road_features.median_pivot_off == approx(radius, abs=2)
        assert road_features.mean_pivot_off == approx(radius, abs=2)
        assert road_features.max_pivot_off == approx(radius, abs=2)
        assert road_features.min_pivot_off == approx(radius, abs=2)
