frappe.pages["user-growth-dashboard"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("User Growth Dashboard"),
		single_column: true,
	});

	page.main.addClass("user-growth-dashboard-page");
	const dashboard = new UserGrowthDashboard(page);
	dashboard.make();
};

class UserGrowthDashboard {
	constructor(page) {
		this.page = page;
		this.loading = false;
		this.charts = {};
	}

	make() {
		this.page.set_primary_action(__("Refresh"), () => this.refresh(), "refresh");
		this.$root = $(this.template()).appendTo(this.page.main);
		this.refresh();
		this.refresh_interval = setInterval(() => this.refresh(), 60000);
	}

	template() {
		return `
			<div class="ugd-screen">
				<div class="ugd-hero">
					<div>
						<div class="ugd-eyebrow">USER GROWTH COMMAND CENTER</div>
						<h1>用户增长数据大屏</h1>
						<p>基于用户服务开通与流失数据，展示增长、流失、分布和 MRR。</p>
					</div>
					<div class="ugd-time" data-field="updated_at">--</div>
				</div>
				<div class="ugd-alert" data-field="error" style="display:none"></div>
				<div class="ugd-kpis" data-field="kpis"></div>
				<div class="ugd-grid">
					<section class="ugd-panel ugd-panel-wide"><h3>近 12 个月增长 / 流失趋势</h3><div id="ugd-trend-chart"></div></section>
					<section class="ugd-panel"><h3>获客渠道分布</h3><div data-field="channels"></div></section>
					<section class="ugd-panel"><h3>区域分布</h3><div data-field="regions"></div></section>
					<section class="ugd-panel"><h3>省份 Top 10</h3><div data-field="provinces"></div></section>
					<section class="ugd-panel"><h3>套餐结构</h3><div data-field="plans"></div></section>
					<section class="ugd-panel ugd-panel-wide"><h3>高价值客户</h3><div data-field="top_customers"></div></section>
					<section class="ugd-panel"><h3>最近开通用户</h3><div data-field="recent_signups"></div></section>
					<section class="ugd-panel"><h3>最近流失用户</h3><div data-field="recent_churns"></div></section>
				</div>
			</div>
		`;
	}

	async refresh() {
		if (this.loading) return;
		this.loading = true;
		this.show_error("");
		try {
			const response = await frappe.call({
				method: "user_growth.user_growth.page.user_growth_dashboard.user_growth_dashboard.get_dashboard_data",
				args: { filters: {} },
			});
			this.render(response.message);
		} catch (error) {
			this.show_error(error.message || __("Failed to load dashboard data."));
		} finally {
			this.loading = false;
		}
	}

	render(data) {
		if (!data || !data.summary) {
			this.show_error(__("No dashboard data returned."));
			return;
		}
		this.$root.find('[data-field="updated_at"]').text(frappe.datetime.now_datetime());
		this.render_kpis(data.summary);
		this.render_trend(data.monthly || []);
		this.render_distribution("channels", data.channels || []);
		this.render_distribution("regions", data.regions || []);
		this.render_distribution("provinces", data.provinces || []);
		this.render_distribution("plans", data.plans || []);
		this.render_table("top_customers", data.top_customers || [], "monthly_revenue");
		this.render_table("recent_signups", data.recent_signups || [], "signup_date");
		this.render_table("recent_churns", data.recent_churns || [], "churn_date");
	}

	render_kpis(summary) {
		const cards = [
			[__("活跃用户"), summary.active_users, "green"],
			[__("本月新增"), summary.latest_month_new_users, "blue"],
			[__("本月流失"), summary.latest_month_churned_users, "red"],
			[__("净增长"), summary.latest_month_net_growth, "cyan"],
			[__("当前 MRR"), format_currency(summary.current_mrr || 0), "gold"],
			[__("本月流失率"), `${summary.latest_month_churn_rate || 0}%`, "orange"],
		];
		this.$root.find('[data-field="kpis"]').html(
			cards.map(([label, value, color]) => `<div class="ugd-kpi ${color}"><span>${label}</span><strong>${value}</strong></div>`).join("")
		);
	}

	render_trend(monthly) {
		const chart_data = {
			labels: monthly.map((row) => row.month),
			datasets: [
				{name: __("新增"), values: monthly.map((row) => row.new_users)},
				{name: __("流失"), values: monthly.map((row) => row.churned_users)},
				{name: __("净增长"), values: monthly.map((row) => row.net_growth)},
			],
		};
		if (this.charts.trend) {
			this.charts.trend.update(chart_data);
			return;
		}
		this.charts.trend = new frappe.Chart("#ugd-trend-chart", {
			data: chart_data,
			type: "line",
			height: 280,
			colors: ["#2ee6a6", "#ff5d73", "#4dabf7"],
			axisOptions: { xIsSeries: true },
		});
	}

	render_distribution(field, rows) {
		const total = rows.reduce((sum, row) => sum + row.value, 0) || 1;
		const html = rows.length
			? rows.map((row) => {
				const percent = Math.round((row.value / total) * 100);
				return `<div class="ugd-bar-row"><span>${frappe.utils.escape_html(row.label)}</span><div><i style="width:${percent}%"></i></div><strong>${row.value}</strong></div>`;
			}).join("")
			: `<div class="ugd-empty">暂无数据</div>`;
		this.$root.find(`[data-field="${field}"]`).html(html);
	}

	render_table(field, rows, value_field) {
		const html = rows.length
			? `<table class="ugd-table"><tbody>${rows.map((row) => `<tr><td>${frappe.utils.escape_html(row.customer_name || "-")}</td><td>${frappe.utils.escape_html(row.province || "-")}</td><td>${this.format_value(row[value_field], value_field)}</td></tr>`).join("")}</tbody></table>`
			: `<div class="ugd-empty">暂无数据</div>`;
		this.$root.find(`[data-field="${field}"]`).html(html);
	}

	format_value(value, field) {
		if (field === "monthly_revenue") return format_currency(value || 0);
		return value || "-";
	}

	show_error(message) {
		const $error = this.$root && this.$root.find('[data-field="error"]');
		if (!$error) return;
		if (!message) {
			$error.hide().text("");
			return;
		}
		$error.text(message).show();
	}
}
