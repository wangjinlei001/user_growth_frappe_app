import json

import frappe

from user_growth.analytics import get_growth_analytics


@frappe.whitelist()
def get_dashboard_data(filters=None):
    if isinstance(filters, str):
        filters = json.loads(filters or "{}")
    return get_growth_analytics(filters or {})
