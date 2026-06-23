frappe.query_reports["User Growth Analytics"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.month_start(), -11),
			reqd: 1,
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1,
		},
		{
			fieldname: "region",
			label: __("Region"),
			fieldtype: "Select",
			options: "\n华东\n华南\n华北\n华中\n西南\n西北\n东北",
		},
		{
			fieldname: "province",
			label: __("Province"),
			fieldtype: "Data",
		},
		{
			fieldname: "acquisition_channel",
			label: __("Acquisition Channel"),
			fieldtype: "Select",
			options: "\n自然流量\n广告投放\n渠道合作\n活动转化\n老客推荐",
		},
		{
			fieldname: "plan_type",
			label: __("Plan Type"),
			fieldtype: "Select",
			options: "\nFree\nBasic\nPro\nEnterprise",
		},
		{
			fieldname: "service_status",
			label: __("Service Status"),
			fieldtype: "Select",
			options: "\nActive\nChurned",
		},
	],
};
