import unittest

from octue.cloud.emulators.cloud_storage import GoogleCloudStorageEmulatorTestResultModifier


class BaseTestCase(unittest.TestCase):
    # Add a cloud storage emulator.
    test_result_modifier = GoogleCloudStorageEmulatorTestResultModifier(
        default_bucket_name="octue-octue-twined-services-octue-twined"
    )

    setattr(unittest.TestResult, "startTestRun", test_result_modifier.startTestRun)
    setattr(unittest.TestResult, "stopTestRun", test_result_modifier.stopTestRun)
