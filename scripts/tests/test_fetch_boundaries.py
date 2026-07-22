import unittest

from scripts.fetch_boundaries import normalize_admin1, normalize_countries


class NormalizeBoundariesTests(unittest.TestCase):
    def test_normalizes_country_and_admin1_codes(self):
        countries = normalize_countries(
            {"features": [{"properties": {"ISO_A3": "SGP", "NAME_EN": "Singapore"}, "geometry": {"type": "Polygon", "coordinates": []}}]},
            0,
        )
        admin1 = normalize_admin1(
            {"features": [{"properties": {"adm0_a3": "SGP", "iso_3166_2": "SG-01", "name_en": "Central"}, "geometry": {"type": "Polygon", "coordinates": []}}]},
            0,
        )
        self.assertEqual(countries["features"][0]["properties"]["iso_code"], "SGP")
        self.assertEqual(admin1["SGP"][0]["properties"]["code"], "SG-01")

    def test_skips_features_without_country_code(self):
        result = normalize_admin1(
            {"features": [{"properties": {}, "geometry": {"type": "Polygon", "coordinates": []}}]},
            0,
        )
        self.assertEqual(dict(result), {})


if __name__ == "__main__":
    unittest.main()
