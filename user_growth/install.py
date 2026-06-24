import frappe

from user_growth.mock_data import seed_mock_data


def after_install():
	seed_mock_data(record_count=200)
	_ensure_workspace()


def _ensure_workspace() -> None:
	"""Create the "User Growth" Desk workspace so the app shows up in the sidebar."""
	name = "User Growth"
	if frappe.db.exists("Workspace", name):
		return

	workspace = frappe.get_doc(
		{
			"doctype": "Workspace",
			"name": name,
			"title": name,
			"label": name,
			"public": 1,
			"is_hidden": 0,
			"module": "User Growth",
			"icon": "users",
			"shortcuts": [
				{
					"label": "用户服务生命周期",
					"link_to": "User Service Lifecycle",
					"type": "DocType",
				},
				{
					"label": "用户增长分析报表",
					"link_to": "User Growth Analytics",
					"type": "Report",
				},
				{
					"label": "用户增长仪表盘",
					"link_to": "user-growth-dashboard",
					"type": "Page",
				},
			],
			"links": [
				{
					"label": "User Growth",
					"type": "Card Break",
					"hidden": 0,
				},
				{
					"label": "用户服务生命周期",
					"link_type": "DocType",
					"link_to": "User Service Lifecycle",
					"type": "Link",
					"hidden": 0,
					"onboard": 0,
				},
				{
					"label": "用户增长分析报表",
					"link_type": "Report",
					"link_to": "User Growth Analytics",
					"type": "Link",
					"hidden": 0,
					"onboard": 0,
					"is_query_report": 1,
				},
				{
					"label": "用户增长仪表盘",
					"link_type": "Page",
					"link_to": "user-growth-dashboard",
					"type": "Link",
					"hidden": 0,
					"onboard": 0,
				},
			],
		}
	)
	workspace.insert(ignore_permissions=True)
