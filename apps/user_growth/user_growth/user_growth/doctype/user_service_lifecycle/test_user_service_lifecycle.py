import frappe
from frappe.tests.utils import FrappeTestCase


class TestUserServiceLifecycle(FrappeTestCase):
    def test_churned_user_requires_churn_date(self):
        doc = frappe.get_doc(
            {
                "doctype": "User Service Lifecycle",
                "user_id": "UG-TEST-CHURN-MISSING",
                "customer_name": "测试客户",
                "service_status": "Churned",
                "signup_date": "2026-01-01",
                "province": "广东",
                "region": "华南",
                "acquisition_channel": "自然流量",
                "plan_type": "Pro",
                "monthly_revenue": 399,
                "industry": "互联网",
                "account_manager": "李明",
            }
        )

        with self.assertRaises(frappe.ValidationError):
            doc.insert()

    def test_churn_date_cannot_be_before_signup_date(self):
        doc = frappe.get_doc(
            {
                "doctype": "User Service Lifecycle",
                "user_id": "UG-TEST-CHURN-BEFORE",
                "customer_name": "测试客户",
                "service_status": "Churned",
                "signup_date": "2026-02-01",
                "churn_date": "2026-01-01",
                "province": "浙江",
                "region": "华东",
                "acquisition_channel": "广告投放",
                "plan_type": "Basic",
                "monthly_revenue": 199,
                "industry": "电商",
                "account_manager": "王芳",
            }
        )

        with self.assertRaises(frappe.ValidationError):
            doc.insert()

    def test_active_user_clears_churn_date(self):
        doc = frappe.get_doc(
            {
                "doctype": "User Service Lifecycle",
                "user_id": "UG-TEST-ACTIVE-CLEAR",
                "customer_name": "测试客户",
                "service_status": "Active",
                "signup_date": "2026-03-01",
                "churn_date": "2026-04-01",
                "province": "江苏",
                "region": "华东",
                "acquisition_channel": "老客推荐",
                "plan_type": "Enterprise",
                "monthly_revenue": 2999,
                "industry": "制造",
                "account_manager": "赵强",
            }
        )

        doc.insert()
        self.assertIsNone(doc.churn_date)
        doc.delete()
