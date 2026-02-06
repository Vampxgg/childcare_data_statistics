# 托育数据统计管道

从机构备案、学校备案、问卷星数据中抽取统计数与详情，支持增量缓存。

## 安装

```bash
pip install -r requirements.txt
```

## 脚本一：pipeline.main

机构、学校、问卷星综合统计。

### 入参

| 参数                         | 类型 | 说明                                                                  |
| ---------------------------- | ---- | --------------------------------------------------------------------- |
| `--school`                   | str  | 院校名称，筛选学校详情                                                |
| `--major`                    | str  | 专业名称或代码，如 `520802`、`婴幼儿托育服务与管理`                   |
| `--region`                   | str  | 区域（省/市），如 `广东省`、`广州市`，筛选区域内机构与学校            |
| `--education_level`          | str  | 学历层次，如 `高职专科`、`本科`，按修业年限筛选学校                   |
| `--started_time`             | int  | 调研开始年份，学校年份下限                                            |
| `--no-cache`                 | flag | 禁用缓存，强制重新统计                                                |
| `--details-limit`            | int  | 详情条数上限，默认 10                                                 |
| `--no-questionnaire-details` | flag | 不输出问卷详情（questionnaire_posting、questionnaire_details_sample） |

### 返回值

| 字段                                     | 含义                                             |
| ---------------------------------------- | ------------------------------------------------ |
| `stats.region`                           | 区域内统计                                       |
| `stats.region.institution_count`         | 区域托育机构数量                                 |
| `stats.region.city_distribution`         | 机构按省 → 市分布 `{省: {市: 数量}}`             |
| `stats.region.host_type_distribution`    | 举办主体分布（公办/民办）                        |
| `stats.region.puhui_distribution`        | 是否普惠分布（按名称关键词推断）                 |
| `stats.region.service_mode_distribution` | 服务模式分布（全日托/半月托/小时托，按名称推断） |
| `stats.region.school_count`              | 区域内开设指定专业的培养点数量                   |
| `stats.region.school_distribution`       | 学校按省份分布                                   |
| `stats.region.posting_sample_count`      | 问卷星有效样本数                                 |
| `stats.region.matched_institution_count` | 问卷星与机构备案匹配数                           |
| `stats.national`                         | 全国统计，字段同 `region`                        |
| `details.institutions`                   | 机构详情（名称、区划、类型等）                   |
| `details.schools`                        | 学校详情（机构名、省份、专业、年份等）           |
| `details.questionnaire_posting`          | 问卷星岗位分布                                   |
| `details.cross_validation`               | 问卷星与机构交叉验证结果                         |
| `meta.from_cache`                        | 是否命中缓存                                     |
| `meta.fingerprints`                      | 数据源指纹                                       |

### 使用

```bash
python -m pipeline.main --region 安徽省 --major 520802
python -m pipeline.main --region 广东省 --major 婴幼儿托育服务与管理 --no-cache
```

---

## 脚本二：pipeline.questionnaire_main

从问卷星提取**招聘岗位相关**人才需求（不包含本人情况），供产业区域分析、人才需求分析报告图表使用。

### 入参

| 参数                      | 类型 | 说明                                                                  |
| ------------------------- | ---- | --------------------------------------------------------------------- |
| `--school`                | str  | 保留，与 pipeline.main 对齐，当前未使用                               |
| `--major`                 | str  | 保留，与 pipeline.main 对齐，当前未使用                               |
| `--region`                | str  | 区域（省/市），如 `广东省`，筛选问卷星区域                            |
| `--education_level`       | str  | 保留参数                                                              |
| `--started_time`          | int  | 保留参数                                                              |
| `--no-cache`              | flag | 保留参数                                                              |
| `--details-limit`         | int  | `raw_sample` 条数上限，默认 10                                        |
| `--no-filter-meaningless` | flag | 不过滤无意义岗位（默认过滤 其他（请注明）、会上课会营销…综合人才 等） |

### 返回值

| 字段                   | 含义                                                                                                                                                      |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `sample_count`         | 有效问卷样本数（按区域筛选后）                                                                                                                            |
| `region`               | 请求的区域参数                                                                                                                                            |
| `posting_requirements` | 按岗位展示：每个岗位对应学历、能力、证书要求及数量。结构：`{岗位: {count, education: {学历: 次数}, competency: {能力: 次数}, certificate: {证书: 次数}}}` |
| `columns_used`         | 实际使用的问卷列名                                                                                                                                        |
| `raw_sample`           | 前 N 条原始记录（仅招聘相关列，不含本人情况）                                                                                                             |

### 使用

```bash
python -m pipeline.questionnaire_main --region 广东省
python -m pipeline.questionnaire_main --region 安徽省 --details-limit=5
```

依赖：`pip install pandas openpyxl`（至少其一）

---

## HTTP API（外部调用）

提供 REST 接口供外部系统调用，基于 FastAPI。

### 启动服务

```bash
python -m pipeline.server
# 或指定端口
python -m pipeline.server --host 0.0.0.0 --port 7806

# 或使用 uvicorn
uvicorn pipeline.server:app --host 0.0.0.0 --port 7806
```

### 接口列表

| 方法     | 路径          | 说明                                             |
| -------- | ------------- | ------------------------------------------------ |
| GET      | `/`           | 服务说明                                         |
| GET/POST | `/stats`      | 机构、学校、问卷星综合统计（对应 pipeline.main） |
| GET/POST | `/job_demand` | 问卷星人才需求提取（对应 questionnaire_main）    |
| GET      | `/docs`       | Swagger 文档                                     |

### 示例

```bash
# 综合统计
curl "http://localhost:7806/stats?region=%E5%B9%BF%E4%B8%9C%E7%9C%81&major=520802"

# 人才需求提取（默认过滤无意义岗位）
curl "http://localhost:7806/job_demand?region=%E5%B9%BF%E4%B8%9C%E7%9C%81"
# 不过滤：filter_meaningless_postings=false
curl "http://localhost:7806/job_demand?region=%E5%B9%BF%E4%B8%9C%E7%9C%81&filter_meaningless_postings=false"

# POST
curl -X POST http://localhost:7806/stats \
  -H "Content-Type: application/json" \
  -d '{"region":"广东省","major":"520802","no_questionnaire_details":true}'
```

---

## 增量更新

- 数据源通过 `path + mtime + size` 生成 fingerprint
- 数据未变更时直接返回缓存，不重新统计
- 缓存存放在 `db/_stats_cache/cache.json`
- 数据更新后首次查询会重新计算并更新缓存
