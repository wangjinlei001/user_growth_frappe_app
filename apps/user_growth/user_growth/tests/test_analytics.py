from unittest import TestCase
from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

from user_growth.analytics import get_default_date_range, get_growth_analytics, get_monthly_metrics


class TestGrowthAnalytics(FrappeTestCase):
    def setUp(self):
        frappe.db.delete("User Service Lifecycle", {"user_id": ["like", "UG-AN-%"]})
        self.records = [
            {
                "user_id": "UG-AN-001",
                "customer_name": "活跃一号",
                "service_status": "Active",
                "signup_date": "2026-01-10",
                "province": "广东",
                "region": "华南",
                "acquisition_channel": "自然流量",
                "plan_type": "Pro",
                "monthly_revenue": 399,
                "industry": "互联网",
                "account_manager": "李明",
            },
            {
                "user_id": "UG-AN-002",
                "customer_name": "流失一号",
                "service_status": "Churned",
                "signup_date": "2026-01-15",
                "churn_date": "2026-03-20",
                "province": "浙江",
                "region": "华东",
                "acquisition_channel": "广告投放",
                "plan_type": "Basic",
                "monthly_revenue": 199,
                "industry": "电商",
                "account_manager": "王芳",
            },
            {
                "user_id": "UG-AN-003",
                "customer_name": "活跃二号",
                "service_status": "Active",
                "signup_date": "2026-03-05",
                "province": "北京",
                "region": "华北",
                "acquisition_channel": "老客推荐",
                "plan_type": "Enterprise",
                "monthly_revenue": 2999,
                "industry": "金融",
                "account_manager": "赵强",
            },
        ]
        for record in self.records:
            doc = frappe.get_doc({"doctype": "User Service Lifecycle", **record})
            doc.insert()

    def tearDown(self):
        frappe.db.delete("User Service Lifecycle", {"user_id": ["like", "UG-AN-%"]})

    def test_default_date_range_spans_twelve_months(self):
        from_date, to_date = get_default_date_range(today=frappe.utils.getdate("2026-06-22"))
        self.assertEqual(str(from_date), "2025-07-01")
        self.assertEqual(str(to_date), "2026-06-22")

    def test_growth_analytics_summary(self):
        result = get_growth_analytics({"from_date": "2026-01-01", "to_date": "2026-03-31"})
        summary = result["summary"]

        self.assertEqual(summary["total_users"], 3)
        self.assertEqual(summary["active_users"], 2)
        self.assertEqual(summary["churned_users"], 1)
        self.assertEqual(summary["current_mrr"], 3398)
        self.assertEqual(summary["latest_month_new_users"], 1)
        self.assertEqual(summary["latest_month_churned_users"], 1)

    def test_growth_analytics_monthly_values(self):
        result = get_growth_analytics({"from_date": "2026-01-01", "to_date": "2026-03-31"})
        monthly = {row["month"]: row for row in result["monthly"]}

        self.assertEqual(monthly["2026-01"]["new_users"], 2)
        self.assertEqual(monthly["2026-01"]["churned_users"], 0)
        self.assertEqual(monthly["2026-03"]["new_users"], 1)
        self.assertEqual(monthly["2026-03"]["churned_users"], 1)
        self.assertEqual(monthly["2026-03"]["net_growth"], 0)

    def test_empty_data_returns_zero_summary(self):
        result = get_growth_analytics({"from_date": "2024-01-01", "to_date": "2024-01-31"})
        summary = result["summary"]

        self.assertEqual(summary["total_users"], 0)
        self.assertEqual(summary["active_users"], 0)
        self.assertEqual(summary["current_mrr"], 0)
        self.assertEqual(result["monthly"][0]["new_users"], 0)

    def test_summary_counts_churned_user_as_active_before_churn_date(self):
        rows = [
            frappe._dict(
                user_id="UG-AN-HIST-001",
                customer_name="历史边界客户",
                service_status="Churned",
                signup_date="2026-01-01",
                churn_date="2026-04-01",
                province="上海",
                region="华东",
                acquisition_channel="自然流量",
                plan_type="Pro",
                monthly_revenue=599,
                industry="制造",
                account_manager="陈晨",
            )
        ]

        with (
            patch("user_growth.analytics.get_default_date_range", return_value=(frappe.utils.getdate("2026-01-01"), frappe.utils.getdate("2026-03-31"))),
            patch("user_growth.analytics.get_lifecycle_rows", return_value=rows),
        ):
            result = get_growth_analytics({"from_date": "2026-01-01", "to_date": "2026-03-31"})

        self.assertEqual(result["summary"]["active_users"], 1)
        self.assertEqual(result["summary"]["current_mrr"], 599)
        self.assertEqual(result["summary"]["churned_users"], 0)
        self.assertEqual(result["monthly"][-1]["active_users"], 1)


class TestAnalyticsSummaryChurnBoundaries(TestCase):
    def test_future_churn_user_is_active_but_not_counted_as_churned_as_of_to_date(self):
        rows = [
            self.make_row(
                user_id="UG-AN-FUTURE-CHURN",
                service_status="Churned",
                signup_date="2026-01-01",
                churn_date="2026-04-01",
                monthly_revenue=599,
            )
        ]

        with (
            patch("user_growth.analytics.get_default_date_range", return_value=(frappe.utils.getdate("2026-01-01"), frappe.utils.getdate("2026-03-31"))),
            patch("user_growth.analytics.get_lifecycle_rows", return_value=rows),
        ):
            result = get_growth_analytics({"from_date": "2026-01-01", "to_date": "2026-03-31"})

        self.assertEqual(result["summary"]["active_users"], 1)
        self.assertEqual(result["summary"]["current_mrr"], 599)
        self.assertEqual(result["summary"]["churned_users"], 0)

    def test_churn_date_equal_to_date_is_churned_and_not_active_as_of_to_date(self):
        rows = [
            self.make_row(
                user_id="UG-AN-TO-DATE-CHURN",
                service_status="Churned",
                signup_date="2026-01-01",
                churn_date="2026-03-31",
                monthly_revenue=599,
            )
        ]

        with (
            patch("user_growth.analytics.get_default_date_range", return_value=(frappe.utils.getdate("2026-01-01"), frappe.utils.getdate("2026-03-31"))),
            patch("user_growth.analytics.get_lifecycle_rows", return_value=rows),
        ):
            result = get_growth_analytics({"from_date": "2026-01-01", "to_date": "2026-03-31"})

        self.assertEqual(result["summary"]["active_users"], 0)
        self.assertEqual(result["summary"]["current_mrr"], 0)
        self.assertEqual(result["summary"]["churned_users"], 1)

    def make_row(self, **overrides):
        values = {
            "user_id": "UG-AN-SUMMARY",
            "customer_name": "Summary Boundary Customer",
            "service_status": "Active",
            "signup_date": "2026-01-01",
            "churn_date": None,
            "province": "广东",
            "region": "华南",
            "acquisition_channel": "自然流量",
            "plan_type": "Pro",
            "monthly_revenue": 399,
            "industry": "互联网",
            "account_manager": "李明",
        }
        values.update(overrides)
        return frappe._dict(values)


class TestAnalyticsRecentRows(TestCase):
    def test_recent_signups_only_include_signups_inside_filter_range(self):
        rows = [
            self.make_row(
                user_id="UG-AN-RECENT-OLD-SIGNUP",
                customer_name="历史开通仍活跃客户",
                service_status="Active",
                signup_date="2025-12-15",
                churn_date=None,
            ),
            self.make_row(
                user_id="UG-AN-RECENT-JUNE-SIGNUP",
                customer_name="六月开通客户",
                service_status="Active",
                signup_date="2026-06-10",
                churn_date=None,
            ),
        ]

        with (
            patch("user_growth.analytics.get_default_date_range", return_value=(frappe.utils.getdate("2026-06-01"), frappe.utils.getdate("2026-06-30"))),
            patch("user_growth.analytics.get_lifecycle_rows", return_value=rows),
        ):
            result = get_growth_analytics({"from_date": "2026-06-01", "to_date": "2026-06-30"})

        recent_signup_ids = {row["user_id"] for row in result["recent_signups"]}
        self.assertNotIn("UG-AN-RECENT-OLD-SIGNUP", recent_signup_ids)
        self.assertIn("UG-AN-RECENT-JUNE-SIGNUP", recent_signup_ids)

    def test_recent_churns_only_include_churns_inside_filter_range(self):
        rows = [
            self.make_row(
                user_id="UG-AN-RECENT-JUNE-CHURN",
                customer_name="六月流失客户",
                service_status="Churned",
                signup_date="2026-05-01",
                churn_date="2026-06-20",
            ),
            self.make_row(
                user_id="UG-AN-RECENT-FUTURE-CHURN",
                customer_name="七月流失客户",
                service_status="Churned",
                signup_date="2026-05-01",
                churn_date="2026-07-01",
            ),
        ]

        with (
            patch("user_growth.analytics.get_default_date_range", return_value=(frappe.utils.getdate("2026-06-01"), frappe.utils.getdate("2026-06-30"))),
            patch("user_growth.analytics.get_lifecycle_rows", return_value=rows),
        ):
            result = get_growth_analytics({"from_date": "2026-06-01", "to_date": "2026-06-30"})

        recent_churn_ids = {row["user_id"] for row in result["recent_churns"]}
        self.assertIn("UG-AN-RECENT-JUNE-CHURN", recent_churn_ids)
        self.assertNotIn("UG-AN-RECENT-FUTURE-CHURN", recent_churn_ids)

    def make_row(self, **overrides):
        values = {
            "user_id": "UG-AN-RECENT",
            "customer_name": "最近列表客户",
            "service_status": "Active",
            "signup_date": "2026-06-01",
            "churn_date": None,
            "province": "广东",
            "region": "华南",
            "acquisition_channel": "自然流量",
            "plan_type": "Pro",
            "monthly_revenue": 399,
            "industry": "互联网",
            "account_manager": "李明",
        }
        values.update(overrides)
        return frappe._dict(values)


class TestMonthlyMetrics(TestCase):
    def test_partial_first_month_excludes_signups_before_from_date(self):
        rows = [
            frappe._dict(signup_date="2026-01-10", churn_date=None, monthly_revenue=100),
            frappe._dict(signup_date="2026-01-15", churn_date=None, monthly_revenue=200),
        ]

        monthly = get_monthly_metrics(
            rows,
            frappe.utils.getdate("2026-01-15"),
            frappe.utils.getdate("2026-01-31"),
        )

        self.assertEqual(monthly[0]["new_users"], 1)
        self.assertEqual(monthly[0]["new_mrr"], 200)

    def test_partial_first_month_counts_from_date_active_churned_user_in_churn_rate_denominator(self):
        rows = [
            frappe._dict(signup_date="2026-01-10", churn_date="2026-01-20", monthly_revenue=100),
        ]

        monthly = get_monthly_metrics(
            rows,
            frappe.utils.getdate("2026-01-15"),
            frappe.utils.getdate("2026-01-31"),
        )

        self.assertEqual(monthly[0]["churned_users"], 1)
        self.assertEqual(monthly[0]["churn_rate"], 100)

    def test_churn_date_equal_bucket_start_counts_in_period_start_denominator(self):
        rows = [
            frappe._dict(signup_date="2026-01-10", churn_date="2026-02-01", monthly_revenue=100),
            frappe._dict(signup_date="2026-01-10", churn_date=None, monthly_revenue=200),
        ]

        monthly = get_monthly_metrics(
            rows,
            frappe.utils.getdate("2026-02-01"),
            frappe.utils.getdate("2026-02-28"),
        )

        self.assertEqual(monthly[0]["churned_users"], 1)
        self.assertEqual(monthly[0]["churn_rate"], 50)
