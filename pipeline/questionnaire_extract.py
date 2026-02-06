# -*- coding: utf-8 -*-
"""
问卷星人才需求提取：岗位、薪酬、学历、能力、证书、人才能力类型
用于产业区域分析报告、人才需求分析报告中的图表生成与实时数据
"""

import re
from typing import Any, Dict, List, Optional, Tuple

from .filters import filter_questionnaire_by_region
from .loader import load_questionnaire


# 列名映射：仅招聘岗位相关，排除本人情况（如您的学历、您当前的岗位等）
# 优先匹配含「机构」「招聘」「紧缺」「人才」等招聘语境的列
COLUMN_MAPS = {
    "posting": [
        "机构当前最紧缺的岗位",
        "最紧缺的岗位",
        "最缺岗位",
        "紧缺岗位",
        "需求岗位",
        "岗位需求",
        "招聘岗位",
    ],
    "salary": [
        "岗位薪酬",
        "招聘薪酬",
        "人才薪酬",
        "薪资水平",
        "薪酬水平",
    ],
    "education": [
        "托育人才的学历结构中",
        "学历结构中占比最高",
        "招聘学历",
        "岗位学历要求",
        "学历要求",
    ],
    "competency": [
        "毕业生最欠缺的能力",
        "岗位能力要求",
        "能力要求",
        "技能要求",
    ],
    "certificate": [
        "证书/资质要求",
        "对托育人才的证书",
        "资质要求",
        "所需证书",
        "职业资格",
    ],
    "talent_type": [
        "优先考虑的因素",
        "招聘时优先考虑",
        "人才能力类型",
        "能力类型",
    ],
}

# 排除本人/受访者相关列（您的、本人、您当前等）
EXCLUDE_COL_PATTERNS = ("您的最高学历", "您最高学历", "您当前的岗位", "您当前岗位", "您当前的薪资", "您对当前岗位")

# 无意义岗位过滤：含以下任一关键字的岗位将被排除
MEANINGLESS_POSTING_KEYWORDS = (
    "其他（请注明）",  # 其他（请注明）〖无〗、其他（请注明）〖行政〗 等
    "会上课会营销会管理会沟通",  #  vague 营销型描述
    "综合人才",  # vague
    "〗",  # 拆分残留，如 会上课会营销会管理会沟通的综合人才〗
)
MEANINGLESS_POSTING_EXACT = ("无",)  # 精确匹配排除


def _first_existing(cols: List[str], row: Dict[str, Any]) -> Any:
    """从行中取第一个存在的列值"""
    for c in cols:
        if c in row:
            v = row[c]
            if v is not None and str(v).strip():
                return str(v).strip()
    return None


def _detect_column(data: List[Dict], candidates: List[str], all_columns: List[str]) -> Optional[str]:
    """
    检测招聘岗位相关列：排除本人情况列，优先匹配招聘语境
    """
    def _is_excluded(col: str) -> bool:
        for pat in EXCLUDE_COL_PATTERNS:
            if pat in col:
                return True
        # 排除纯本人语境：您的学历、您当前、本人
        if col.startswith("您的") and "机构" not in col and "招聘" not in col:
            if any(x in col for x in ["学历", "岗位", "薪资", "满意度"]):
                return True
        return False

    for c in candidates:
        if c in all_columns and not _is_excluded(c):
            return c
    for cand in candidates:
        for col in all_columns:
            if _is_excluded(col):
                continue
            if cand in col or col in cand:
                return col
    return None


def _normalize_value(val: str, field: str) -> str:
    """规范化值，便于聚合（去多余空格、统一分隔）"""
    if not val:
        return ""
    s = re.sub(r"\s+", " ", str(val).strip())
    # 多选可能用分号、顿号、逗号分隔
    return s


def _raw_sample_recruitment_only(
    rows: List[Dict], cols_used: Dict[str, Optional[str]], all_columns: List[str]
) -> List[Dict[str, Any]]:
    """仅保留招聘岗位相关列，排除本人情况"""
    include_cols = {"机构名称", "机构所在城市", "您的机构所在城市"}
    for col in cols_used.values():
        if col:
            include_cols.add(col)
    for col in all_columns:
        if any(k in col for k in ("机构", "招聘", "紧缺", "人才", "岗位", "证书", "学历", "能力")) and not any(
            ex in col for ex in ("您的最高", "您最高学历", "您当前的岗位", "您当前岗位", "您当前的薪资", "您对当前")
        ):
            include_cols.add(col)
    return [
        {k: v for k, v in row.items() if k in include_cols and v and str(v).strip()}
        for row in rows
    ]


def _is_meaningless_posting(posting: str) -> bool:
    """判断岗位是否为无意义项（需过滤）"""
    if not posting or not posting.strip():
        return True
    s = posting.strip()
    if s in MEANINGLESS_POSTING_EXACT:
        return True
    return any(kw in s for kw in MEANINGLESS_POSTING_KEYWORDS)


def _split_multi(val: str) -> List[str]:
    """拆分多选值（分号、顿号、逗号、┋ 等），过滤无效项"""
    if not val or not str(val).strip():
        return []
    s = str(val).strip()
    # 问卷星多选用 ┋ 分隔
    parts = re.split(r"[;；,，、\n┋]", s)
    result = []
    for p in parts:
        item = p.strip()
        if not item or item == "(跳过)":
            continue
        result.append(item)
    return result


def extract_talent_demand(
    data: Optional[List[Dict[str, Any]]] = None,
    region: Optional[str] = None,
    columns_override: Optional[Dict[str, str]] = None,
    raw_sample_limit: int = 10,
    filter_meaningless_postings: bool = True,
) -> Dict[str, Any]:
    """
    从问卷星数据提取人才需求统计

    参数:
        data: 问卷星行列表，若为 None 则自动加载
        region: 区域筛选（省/市），同 pipeline.main --region
        columns_override: 自定义列名映射 { field: "实际列名" }

    返回:
        {
            "sample_count": 有效样本数,
            "region": 区域,
            "posting_requirements": {
                岗位名: {
                    "count": 提及次数,
                    "education": { 学历: 次数 },
                    "competency": { 能力: 次数 },
                    "certificate": { 证书: 次数 }
                }
            },
            "columns_used": { 实际使用的列名 },
            "raw_sample": 前若干条原始记录
        }
    """
    if data is None:
        data = load_questionnaire()
    if not data:
        return _empty_result(region=region)

    # 区域筛选
    if region:
        data = filter_questionnaire_by_region(data, region)
    if not data:
        return _empty_result(region=region)

    all_cols = list(data[0].keys()) if data else []
    cols_used: Dict[str, Optional[str]] = {}

    def _resolve(field: str) -> Optional[str]:
        if columns_override and field in columns_override:
            return columns_override[field]
        return _detect_column(data, COLUMN_MAPS[field], all_cols)

    for field in COLUMN_MAPS:
        cols_used[field] = _resolve(field)

    # 按岗位关联统计：每个岗位对应学历、能力、证书要求及数量
    posting_requirements: Dict[str, Dict[str, Any]] = {}

    def _ensure_posting(p: str) -> None:
        if p not in posting_requirements:
            posting_requirements[p] = {
                "count": 0,
                "education": {},
                "competency": {},
                "certificate": {},
            }

    col_p, col_e, col_c, col_cert = (
        cols_used.get("posting"),
        cols_used.get("education"),
        cols_used.get("competency"),
        cols_used.get("certificate"),
    )

    for row in data:
        postings = _split_multi((_first_existing([col_p], row) if col_p else None) or "")
        educations = _split_multi((_first_existing([col_e], row) if col_e else None) or "")
        competencies = _split_multi((_first_existing([col_c], row) if col_c else None) or "")
        certificates = _split_multi((_first_existing([col_cert], row) if col_cert else None) or "")

        if not postings:
            continue

        for posting in postings:
            if filter_meaningless_postings and _is_meaningless_posting(posting):
                continue
            _ensure_posting(posting)
            posting_requirements[posting]["count"] += 1
            for e in educations:
                posting_requirements[posting]["education"][e] = (
                    posting_requirements[posting]["education"].get(e, 0) + 1
                )
            for c in competencies:
                posting_requirements[posting]["competency"][c] = (
                    posting_requirements[posting]["competency"].get(c, 0) + 1
                )
            for z in certificates:
                posting_requirements[posting]["certificate"][z] = (
                    posting_requirements[posting]["certificate"].get(z, 0) + 1
                )

    # 按 count 排序岗位，子字典按频次排序
    def _sort_dist(d: Dict[str, int]) -> Dict[str, int]:
        return dict(sorted(d.items(), key=lambda x: -x[1]))

    result_req: Dict[str, Dict[str, Any]] = {}
    for posting in sorted(posting_requirements.keys(), key=lambda p: -posting_requirements[p]["count"]):
        pr = posting_requirements[posting]
        result_req[posting] = {
            "count": pr["count"],
            "education": _sort_dist(pr["education"]),
            "competency": _sort_dist(pr["competency"]),
            "certificate": _sort_dist(pr["certificate"]),
        }

    return {
        "sample_count": len(data),
        "region": region,
        "posting_requirements": result_req,
        "columns_used": cols_used,
        "raw_sample": _raw_sample_recruitment_only(
            data[:raw_sample_limit], cols_used, all_cols
        ),
    }


def _empty_result(region: Optional[str] = None) -> Dict[str, Any]:
    return {
        "sample_count": 0,
        "region": region,
        "posting_requirements": {},
        "columns_used": {},
        "raw_sample": [],
    }


def get_talent_demand(
    region: Optional[str] = None,
    use_cache: bool = False,
    details_limit: int = 10,
    filter_meaningless_postings: bool = True,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    获取人才需求提取结果（可与 api.get_stats 配合使用）
    use_cache: 暂未实现，保留接口兼容
    details_limit: raw_sample 条数上限
    filter_meaningless_postings: 是否过滤无意义岗位（默认 True）
    """
    return extract_talent_demand(
        data=None,
        region=region,
        raw_sample_limit=details_limit,
        filter_meaningless_postings=filter_meaningless_postings,
    )
