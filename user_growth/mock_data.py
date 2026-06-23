from __future__ import annotations

from datetime import date

import frappe
from frappe.utils import add_days, add_months, flt, getdate, nowdate

PROVINCE_REGIONS = {
    "北京": "华北",
    "天津": "华北",
    "河北": "华北",
    "山西": "华北",
    "内蒙古": "华北",
    "上海": "华东",
    "江苏": "华东",
    "浙江": "华东",
    "安徽": "华东",
    "福建": "华东",
    "江西": "华东",
    "山东": "华东",
    "广东": "华南",
    "广西": "华南",
    "海南": "华南",
    "河南": "华中",
    "湖北": "华中",
    "湖南": "华中",
    "重庆": "西南",
    "四川": "西南",
    "贵州": "西南",
    "云南": "西南",
    "陕西": "西北",
    "甘肃": "西北",
    "青海": "西北",
    "宁夏": "西北",
    "新疆": "西北",
    "辽宁": "东北",
    "吉林": "东北",
    "黑龙江": "东北",
}

CHANNELS = ["自然流量", "广告投放", "渠道合作", "活动转化", "老客推荐"]
PLANS = ["Free", "Basic", "Pro", "Enterprise"]
INDUSTRIES = ["电商", "教育", "制造", "金融", "医疗", "互联网"]
MANAGERS = ["李明", "王芳", "赵强", "陈晨", "刘洋", "周敏"]
CUSTOMER_SUFFIXES = ["科技", "数据", "云联", "智造", "未来", "启航", "星河", "蓝海"]

PLAN_REVENUE = {
    "Free": 0,
    "Basic": 199,
    "Pro": 599,
    "Enterprise": 2999,
}


def seed_mock_data(record_count: int = 200) -> int:
    existing = frappe.db.count("User Service Lifecycle", {"user_id": ["like", "UG-%"]})
    if existing:
        return 0

    today = getdate(nowdate())
    start_date = add_months(today, -11)
    provinces = list(PROVINCE_REGIONS.keys())
    inserted = 0

    for index in range(1, record_count + 1):
        user_id = f"UG-{index:04d}"
        province = provinces[(index * 7) % len(provinces)]
        region = PROVINCE_REGIONS[province]
        plan_type = weighted_plan(index)
        signup_date = add_days(start_date, (index * 11) % 335)
        service_status = "Churned" if index % 10 in (0, 3, 7) else "Active"
        churn_date = None
        if service_status == "Churned":
            churn_date = min(add_days(signup_date, 30 + ((index * 13) % 180)), today)

        doc = frappe.get_doc(
            {
                "doctype": "User Service Lifecycle",
                "user_id": user_id,
                "customer_name": build_customer_name(index),
                "service_status": service_status,
                "signup_date": signup_date,
                "churn_date": churn_date,
                "province": province,
                "region": region,
                "acquisition_channel": CHANNELS[index % len(CHANNELS)],
                "plan_type": plan_type,
                "monthly_revenue": revenue_for_plan(plan_type, index),
                "industry": INDUSTRIES[(index * 3) % len(INDUSTRIES)],
                "account_manager": MANAGERS[(index * 5) % len(MANAGERS)],
                "notes": "演示数据：用于用户增长、流失和大屏展示。",
            }
        )
        doc.insert(ignore_permissions=True)
        inserted += 1

    frappe.db.commit()
    return inserted


def weighted_plan(index: int) -> str:
    remainder = index % 20
    if remainder in (0, 11):
        return "Enterprise"
    if remainder in (1, 2, 3):
        return "Free"
    if remainder in (4, 5, 6, 7, 8, 9, 10):
        return "Basic"
    return "Pro"


def revenue_for_plan(plan_type: str, index: int) -> float:
    base = PLAN_REVENUE[plan_type]
    if plan_type == "Free":
        return 0
    multiplier = 1 + ((index % 5) * 0.08)
    return flt(base * multiplier, 2)


def build_customer_name(index: int) -> str:
    suffix = CUSTOMER_SUFFIXES[index % len(CUSTOMER_SUFFIXES)]
    return f"{suffix}{index:03d}客户"
