import unittest

from pydantic import ValidationError

from models.place import PlaceStatus
from schemas.place import PlaceCreate, PlaceUpdate, TagCreate
from services.places import status_lights_map


class StatusLightsMapTests(unittest.TestCase):
    def test_actual_experience_lights_map(self):
        for status in ("visited", "lived", "worked", "studied"):
            with self.subTest(status=status):
                self.assertTrue(status_lights_map(status))

    def test_wishlist_does_not_light_map(self):
        self.assertFalse(status_lights_map(PlaceStatus.wishlist))

    def test_place_accepts_stable_geography_codes(self):
        place = PlaceCreate(
            name="Gardens by the Bay",
            longitude=103.8636,
            latitude=1.2816,
            country_name="Singapore",
            country_iso="SGP",
            province_name="Singapore",
            province_code="SG-01",
        )
        self.assertEqual(place.country_iso, "SGP")

    def test_place_rejects_invalid_country_code(self):
        with self.assertRaises(ValidationError):
            PlaceCreate(
                name="Invalid",
                longitude=0,
                latitude=0,
                country_name="Invalid",
                country_iso="sg",
                province_name="Invalid",
                province_code="INVALID-1",
            )

    def test_place_update_accepts_partial_changes(self):
        update = PlaceUpdate(name="Updated place", longitude=120)
        self.assertEqual(update.name, "Updated place")
        self.assertEqual(update.longitude, 120)

    def test_place_update_rejects_invalid_coordinates(self):
        with self.assertRaises(ValidationError):
            PlaceUpdate(latitude=91)

    def test_tag_rejects_empty_name(self):
        with self.assertRaises(ValidationError):
            TagCreate(name="")


if __name__ == "__main__":
    unittest.main()
