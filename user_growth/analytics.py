from __future__ import annotations

from collections import Counter
from datetime import date

import frappe
from frappe.utils import add_months, flt, get_first_day, get_last_day, getdate, nowdate

DOCTYPE = "User Service Lifecycle"

OPTIONAL_FILTERS = (
    "region",
    "province",
    "acquisition_channel",
    "plan_type",
    "service_status",
)


def get_default_date_range(today: date | None = None) -> tuple[date, date]:
    to_date = getdate(today or nowdate())
    from_date = get_first_day(add_months(to_date, -11))
    return from_date, to_date


def build_filters(filters: dict | None) -> dict:
    filters = frappe._dict(filters or {})
    default_from, default_to = get_default_date_range()

    return {
        "from_date": getdate(filters.get("from_date") or default_from),
        "to_date": getdate(filters.get("to_date") or default_to),
        "region": filters.get("region"),
        "province": filters.get("province"),
        "acquisition_channel": filters.get("acquisition_channel"),
        "plan_type": filters.get("plan_type"),
        "service_status": filters.get("service_status"),
    }


def get_lifecycle_rows(filters: dict | None = None) -> list[frappe._dict]:
    normalized = build_filters(filters)
    query_filters = []

    for fieldname in OPTIONAL_FILTERS:
        if normalized.get(fieldname):
            query_filters.append([DOCTYPE, fieldname, "=", normalized[fieldname]])

    rows = frappe.get_all(
        DOCTYPE,
        filters=query_filters,
        fields=[
            "name",
            "user_id",
            "customer_name",
            "service_status",
            "signup_date",
            "churn_date",
            "province",
            "region",
            "acquisition_channel",
            "plan_type",
            "monthly_revenue",
            "industry",
            "account_manager",
        ],
        order_by="signup_date asc, user_id asc",
    )

    from_date = normalized["from_date"]
    to_date = normalized["to_date"]
    relevant_rows = []
    for row in rows:
        signup_date = getdate(row.signup_date)
        churn_date = getdate(row.churn_date) if row.churn_date else None
        signed_in_range = from_date <= signup_date <= to_date
        churned_in_range = bool(churn_date and from_date <= churn_date <= to_date)
        active_during_range = signup_date <= to_date and (not churn_date or churn_date >= from_date)
        if signed_in_range or churned_in_range or active_during_range:
            relevant_rows.append(row)

    return relevant_rows


def get_growth_analytics(filters: dict | None = None) -> dict:
    normalized = build_filters(filters)
    rows = get_lifecycle_rows(normalized)
    monthly = get_monthly_metrics(rows, normalized["from_date"], normalized["to_date"])

    active_rows = [row for row in rows if is_active_on_date(row, normalized["to_date"])]
    churned_rows = [row for row in rows if is_churned_on_or_before(row, normalized["to_date"])]
    latest_month = monthly[-1] if monthly else _empty_month("", date.today())

    summary = {
        "total_users": len(rows),
        "active_users": len(active_rows),
        "churned_users": len(churned_rows),
        "current_mrr": sum(flt(row.monthly_revenue) for row in active_rows),
        "latest_month_new_users": latest_month["new_users"],
        "latest_month_churned_users": latest_month["churned_users"],
        "latest_month_churn_rate": latest_month["churn_rate"],
        "latest_month_net_growth": latest_month["net_growth"],
    }

    return {
        "filters": normalized,
        "summary": summary,
        "monthly": monthly,
        "regions": count_by(rows, "region"),
        "provinces": count_by(rows, "province", limit=10),
        "channels": count_by(rows, "acquisition_channel"),
        "plans": count_by(rows, "plan_type"),
        "recent_signups": recent_rows(
            date_range_rows(rows, "signup_date", normalized["from_date"], normalized["to_date"]),
            "signup_date",
        ),
        "recent_churns": recent_rows(
            date_range_rows(rows, "churn_date", normalized["from_date"], normalized["to_date"]),
            "churn_date",
        ),
        "top_customers": top_customers(active_rows),
    }


def get_monthly_metrics(rows: list[frappe._dict], from_date: date, to_date: date) -> list[dict]:
    months = month_starts(from_date, to_date)
    data = []

    for month_start in months:
        bucket_start = max(month_start, from_date)
        bucket_end = min(get_last_day(month_start), to_date)
        month_key = month_start.strftime("%Y-%m")
        month_start_active = [
            row
            for row in rows
            if getdate(row.signup_date) <= bucket_start
            and (not row.churn_date or getdate(row.churn_date) >= bucket_start)
        ]
        new_rows = [row for row in rows if bucket_start <= getdate(row.signup_date) <= bucket_end]
        churned_rows = [
            row
            for row in rows
            if row.churn_date and bucket_start <= getdate(row.churn_date) <= bucket_end
        ]
        active_at_month_end = [
            row
            for row in rows
            if getdate(row.signup_date) <= bucket_end
            and (not row.churn_date or getdate(row.churn_date) > bucket_end)
        ]
        month_start_active_count = len(month_start_active)
        churn_rate = (len(churned_rows) / month_start_active_count * 100) if month_start_active_count else 0

        data.append(
            {
                "month": month_key,
                "new_users": len(new_rows),
                "churned_users": len(churned_rows),
                "net_growth": len(new_rows) - len(churned_rows),
                "active_users": len(active_at_month_end),
                "churn_rate": round(churn_rate, 2),
                "new_mrr": sum(flt(row.monthly_revenue) for row in new_rows),
                "churned_mrr": sum(flt(row.monthly_revenue) for row in churned_rows),
                "net_mrr_growth": sum(flt(row.monthly_revenue) for row in new_rows)
                - sum(flt(row.monthly_revenue) for row in churned_rows),
            }
        )

    return data


def month_starts(from_date: date, to_date: date) -> list[date]:
    current = get_first_day(from_date)
    months = []
    while current <= to_date:
        months.append(current)
        current = add_months(current, 1)
    return months


def is_active_on_date(row: frappe._dict, as_of_date: date) -> bool:
    signup_date = getdate(row.signup_date)
    churn_date = getdate(row.churn_date) if row.churn_date else None
    return signup_date <= as_of_date and (not churn_date or churn_date > as_of_date)


def is_churned_on_or_before(row: frappe._dict, as_of_date: date) -> bool:
    return bool(row.churn_date and getdate(row.churn_date) <= as_of_date)


def count_by(rows: list[frappe._dict], fieldname: str, limit: int | None = None) -> list[dict]:
    counts = Counter(row.get(fieldname) or "未设置" for row in rows)
    items = [{"label": label, "value": value} for label, value in counts.most_common(limit)]
    return items


def recent_rows(rows: list[frappe._dict], date_field: str, limit: int = 8) -> list[dict]:
    sorted_rows = sorted(rows, key=lambda row: getdate(row.get(date_field)), reverse=True)
    return [serialize_row(row) for row in sorted_rows[:limit]]


def date_range_rows(rows: list[frappe._dict], date_field: str, from_date: date, to_date: date) -> list[frappe._dict]:
    return [
        row
        for row in rows
        if row.get(date_field) and from_date <= getdate(row.get(date_field)) <= to_date
    ]


def top_customers(rows: list[frappe._dict], limit: int = 8) -> list[dict]:
    sorted_rows = sorted(rows, key=lambda row: flt(row.monthly_revenue), reverse=True)
    return [serialize_row(row) for row in sorted_rows[:limit]]


def serialize_row(row: frappe._dict) -> dict:
    return {
        "user_id": row.user_id,
        "customer_name": row.customer_name,
        "service_status": row.service_status,
        "signup_date": str(row.signup_date) if row.signup_date else None,
        "churn_date": str(row.churn_date) if row.churn_date else None,
        "province": row.province,
        "region": row.region,
        "acquisition_channel": row.acquisition_channel,
        "plan_type": row.plan_type,
        "monthly_revenue": flt(row.monthly_revenue),
        "industry": row.industry,
        "account_manager": row.account_manager,
    }


def _empty_month(month: str, fallback_date: date) -> dict:
    return {
        "month": month or fallback_date.strftime("%Y-%m"),
        "new_users": 0,
        "churned_users": 0,
        "net_growth": 0,
        "active_users": 0,
        "churn_rate": 0,
        "new_mrr": 0,
        "churned_mrr": 0,
        "net_mrr_growth": 0,
    }
