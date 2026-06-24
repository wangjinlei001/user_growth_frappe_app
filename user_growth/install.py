import frappe

from user_growth.mock_data import seed_mock_data


def after_install():
	seed_mock_data(record_count=200)
	_ensure_workspace()
	_ensure_desktop_icons()


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


def _ensure_desktop_icons() -> None:
	"""Create Desktop Icons so User Growth shows up in Desk's app switcher and sidebar.

	Frappe's `create_desktop_icons_from_installed_apps` reads the App icon's
	`logo_url` via ``app_details[0]["logo"]`` without a fallback. If any app on
	the site lacks the `logo` key in its `add_to_apps_screen`, the whole
	auto-generation block aborts and User Growth's icons never get created.
	Re-running the helpers here is idempotent and guarantees our icons exist.
	"""
	from frappe.desk.doctype.desktop_icon.desktop_icon import (
		create_desktop_icons_from_installed_apps,
		create_desktop_icons_from_workspace,
	)

	try:
		create_desktop_icons_from_installed_apps()
	except Exception as exc:
		frappe.log_error(
			title="user_growth: create_desktop_icons_from_installed_apps failed",
			message=str(exc),
		)

	try:
		create_desktop_icons_from_workspace()
	except Exception as exc:
		frappe.log_error(
			title="user_growth: create_desktop_icons_from_workspace failed",
			message=str(exc),
		)

	frappe.cache.delete_value("desktop_icons")
