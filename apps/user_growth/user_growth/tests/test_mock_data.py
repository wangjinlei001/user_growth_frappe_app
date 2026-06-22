import frappe
from frappe.tests.utils import FrappeTestCase

from user_growth.mock_data import seed_mock_data


class TestMockData(FrappeTestCase):
    def tearDown(self):
        frappe.db.delete("User Service Lifecycle", {"user_id": ["like", "UG-%"]})

    def test_seed_mock_data_creates_requested_records(self):
        inserted = seed_mock_data(record_count=12)
        count = frappe.db.count("User Service Lifecycle", {"user_id": ["like", "UG-%"]})

        self.assertEqual(inserted, 12)
        self.assertEqual(count, 12)

    def test_seed_mock_data_is_idempotent(self):
        first = seed_mock_data(record_count=12)
        second = seed_mock_data(record_count=12)
        count = frappe.db.count("User Service Lifecycle", {"user_id": ["like", "UG-%"]})

        self.assertEqual(first, 12)
        self.assertEqual(second, 0)
        self.assertEqual(count, 12)
