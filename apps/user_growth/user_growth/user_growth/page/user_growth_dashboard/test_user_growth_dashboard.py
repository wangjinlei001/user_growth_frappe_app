import frappe
from frappe.tests.utils import FrappeTestCase


class TestUserGrowthDashboard(FrappeTestCase):
    def test_dashboard_data_accepts_filters_from_http_call(self):
        result = frappe.call(
            "user_growth.user_growth.page.user_growth_dashboard.user_growth_dashboard.get_dashboard_data",
            filters='{}',
        )

        self.assertIn("summary", result)
        self.assertIn("monthly", result)
