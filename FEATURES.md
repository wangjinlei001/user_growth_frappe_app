# User Growth 功能说明

本文档说明本次交付的 User Growth 相关功能页面、访问地址和测试截图。

## 功能入口

本次完成并验证的功能包含以下三个页面：

| 功能 | 地址 | 说明 |
| --- | --- | --- |
| 用户服务生命周期 | <http://user-growth.localhost:8000/desk/user-service-lifecycle> | 管理和查看用户从服务开通、使用、续费到流失等阶段的生命周期数据。 |
| 用户增长分析报表 | <http://user-growth.localhost:8000/desk/query-report/User%20Growth%20Analytics> | 以 Query Report 形式展示用户增长分析数据，便于按报表维度查看增长指标。 |
| 用户增长仪表盘 | <http://user-growth.localhost:8000/desk/user-growth-dashboard> | 汇总展示用户增长核心指标、趋势和分析结果，作为运营观察入口。 |

## 页面说明

### 1. 用户服务生命周期

访问地址：<http://user-growth.localhost:8000/desk/user-service-lifecycle>

该页面用于查看和维护用户服务生命周期相关信息，支持在 Frappe Desk 中对用户服务阶段进行跟踪。

测试截图：

![用户服务生命周期](test/user-service-lifecycle.png)

### 2. 用户增长分析报表

访问地址：<http://user-growth.localhost:8000/desk/query-report/User%20Growth%20Analytics>

该页面是用户增长分析 Query Report，用于查看用户增长相关统计结果。报表适合用于数据核对、运营分析和周期性指标查看。

测试截图：

![用户增长分析报表](test/User_Growth_Analytics.png)

### 3. 用户增长仪表盘

访问地址：<http://user-growth.localhost:8000/desk/user-growth-dashboard>

该页面是用户增长仪表盘，集中展示用户增长核心数据和分析结果，便于快速了解当前用户增长情况。

测试截图：

![用户增长仪表盘](test/user-growth-dashboard.png)

## 测试说明

本次测试截图存放在仓库根目录的 `test/` 目录中：

```text
test/User_Growth_Analytics.png
test/user-growth-dashboard.png
test/user-service-lifecycle.png
```

这些截图对应上方三个功能页面，用于说明功能页面已经可以正常访问并展示。

## 本地访问前提

访问上述地址前，请确认：

1. bench 服务已启动。
2. 当前站点为 `user-growth.localhost`。
3. 已登录 Frappe Desk。
4. 浏览器可以访问 `http://user-growth.localhost:8000`。

如果前端静态资源更新后出现 CSS/JS 404，可在 bench 目录执行：

```bash
bench build
bench clear-cache
bench clear-website-cache
bench restart
```
