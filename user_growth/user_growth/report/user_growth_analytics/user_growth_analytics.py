from frappe import _

from user_growth.analytics import get_growth_analytics


def execute(filters=None):
    result = get_growth_analytics(filters)
    columns = get_columns()
    data = get_data(result)
    chart = get_chart(result)
    summary = get_report_summary(result)
    message = _("Showing user growth, churn, net growth, and MRR for the selected period.")
    return columns, data, message, chart, summary


def get_columns():
    return [
        {"label": _("Month"), "fieldname": "month", "fieldtype": "Data", "width": 110},
        {"label": _("New Users"), "fieldname": "new_users", "fieldtype": "Int", "width": 110},
        {"label": _("Churned Users"), "fieldname": "churned_users", "fieldtype": "Int", "width": 130},
        {"label": _("Net Growth"), "fieldname": "net_growth", "fieldtype": "Int", "width": 110},
        {"label": _("Active Users"), "fieldname": "active_users", "fieldtype": "Int", "width": 120},
        {"label": _("Churn Rate"), "fieldname": "churn_rate", "fieldtype": "Percent", "width": 110},
        {"label": _("New MRR"), "fieldname": "new_mrr", "fieldtype": "Currency", "width": 120},
        {"label": _("Churned MRR"), "fieldname": "churned_mrr", "fieldtype": "Currency", "width": 130},
        {"label": _("Net MRR Growth"), "fieldname": "net_mrr_growth", "fieldtype": "Currency", "width": 150},
    ]


def get_data(result):
    return result["monthly"]


def get_chart(result):
    monthly = result["monthly"]
    return {
        "data": {
            "labels": [row["month"] for row in monthly],
            "datasets": [
                {"name": _("New Users"), "values": [row["new_users"] for row in monthly]},
                {"name": _("Churned Users"), "values": [row["churned_users"] for row in monthly]},
                {"name": _("Net Growth"), "values": [row["net_growth"] for row in monthly]},
            ],
        },
        "type": "line",
        "height": 280,
        "colors": ["#21c7a8", "#ff6b6b", "#4dabf7"],
    }


def get_report_summary(result):
    summary = result["summary"]
    return [
        {"label": _("Active Users"), "value": summary["active_users"], "indicator": "Green", "datatype": "Int"},
        {"label": _("Churned Users"), "value": summary["churned_users"], "indicator": "Red", "datatype": "Int"},
        {"label": _("Total Users"), "value": summary["total_users"], "indicator": "Blue", "datatype": "Int"},
        {"label": _("Current MRR"), "value": summary["current_mrr"], "indicator": "Green", "datatype": "Currency"},
        {"label": _("Latest New Users"), "value": summary["latest_month_new_users"], "indicator": "Blue", "datatype": "Int"},
        {"label": _("Latest Churn Rate"), "value": summary["latest_month_churn_rate"], "indicator": "Orange", "datatype": "Percent"},
    ]
