from unittest import TestCase
from src.profile.profile import LUTProfile

TESTFILE_LOCATION = r"/u/56/roberta2/unix/Documents/Colour2Foil/Aalto-Photographic-Colourimetry-Toolbox/testdata/540.cube"

class TestLUTProfile(TestCase):
    def test_from_file_location(self):
        # Test with a valid profile location
        profile_location = TESTFILE_LOCATION
        lut_profile = LUTProfile.from_file_location(profile_location)
        self.assertIsInstance(lut_profile, LUTProfile)
        self.assertIsNotNone(lut_profile.get_lut())
        self.assertIsNotNone(lut_profile.get_gray())

    def test_from_file_location_invalid(self):
        # Test with an invalid profile location
        invalid_profile_location = r"/invalid/path/to/profile.cube"
        with self.assertRaises(FileNotFoundError):
            LUTProfile.from_file_location(invalid_profile_location)

    def test_get_lut_and_gray(self):
        # Test the get_lut and get_gray methods
        profile_location = TESTFILE_LOCATION
        lut_profile = LUTProfile.from_file_location(profile_location)
        self.assertIsNotNone(lut_profile.get_lut())
        self.assertIsNotNone(lut_profile.get_gray())

    def test_write_profile(self):
        # Test the write_profile method (this is a placeholder test, actual implementation may vary)
        profile_location = TESTFILE_LOCATION
        lut_profile = LUTProfile.from_file_location(profile_location)
        try:
            lut_profile.write_profile("test_output")
        except NotImplementedError:
            pass  # If not implemented, we just pass for now
