# -*- coding: utf-8 -*-
"""
统计计算：统计数 + 详情，机构与问卷星交叉验证
"""

from typing import Any, Dict, List, Optional

from .filters import (
    filter_institutions,
    filter_questionnaire_by_region,
    filter_schools,
)
from .loader import (
    infer_host_type,
    infer_is_puhui,
    infer_service_modes,
    load_institutions,
    load_questionnaire,
    load_schools,
    parse_zoning,
)


def _institution_detail(item: Dict[str, Any]) -> Dict[str, Any]:
    """机构详情精简字段"""
    return {
        "institution_name": item.get("institution_name"),
        "institution_other_name": item.get("institution_other_name"),
        "zoning_name": item.get("zoning_name"),
        "institution_type": item.get("institution_type"),
        "address": item.get("address"),
    }


def _school_detail(item: Dict[str, Any]) -> Dict[str, Any]:
    """学校详情精简字段"""
    return {
        "机构名称": item.get("机构名称"),
        "省份": item.get("省份"),
        "开设专业": item.get("开设专业"),
        "修业年限": item.get("修业年限"),
        "年份": item.get("年份"),
    }


def cross_validate_institutions(
    inst_data: List[Dict[str, Any]],
    questionnaire_data: List[Dict[str, Any]],
    name_columns: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    机构备案数据与问卷星交叉验证
    通过机构名称匹配，返回匹配数、匹配详情、未匹配问卷
    """
    name_columns = name_columns or [
        "机构名称",
        "单位名称",
        "机构名",
        "单位",
        "名称",
    ]
    inst_names: set = set()
    inst_other: set = set()
    for x in inst_data:
        n = x.get("institution_name")
        o = x.get("institution_other_name")
        if n:
            inst_names.add(str(n).strip())
        if o:
            inst_other.add(str(o).strip())
    all_names = inst_names | inst_other

    matched: List[Dict[str, Any]] = []
    unmatched: List[Dict[str, Any]] = []
    for row in questionnaire_data:
        found = False
        for col in name_columns:
            if col in row:
                val = str(row[col]).strip()
                if val and val in all_names:
                    found = True
                    break
        if found:
            matched.append(row)
        else:
            unmatched.append(row)

    return {
        "matched_count": len(matched),
        "unmatched_count": len(unmatched),
        "matched_details": matched[:100],
        "unmatched_sample": unmatched[:20],
    }


def _compute_school_distribution(school_data: List[Dict[str, Any]]) -> Dict[str, int]:
    """学校按省份分布（学校数据仅有省份字段）"""
    dist: Dict[str, int] = {}
    for item in school_data:
        prov = (item.get("省份") or "").strip()
        if prov:
            dist[prov] = dist.get(prov, 0) + 1
    return dist


def _compute_institution_distributions(
    inst_data: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    计算机构分布：城市、举办主体、普惠、服务模式
    """
    city_dist: Dict[str, Dict[str, int]] = {}
    host_dist: Dict[str, int] = {}
    puhui_dist: Dict[str, int] = {}
    service_dist: Dict[str, int] = {}

    for item in inst_data:
        # 城市分布
        prov, city = parse_zoning(item.get("zoning_name") or "")
        if prov:
            if prov not in city_dist:
                city_dist[prov] = {}
            c = city or prov  # 直辖市或仅省
            city_dist[prov][c] = city_dist[prov].get(c, 0) + 1

        # 举办主体
        h = infer_host_type(item)
        host_dist[h] = host_dist.get(h, 0) + 1

        # 普惠
        p = infer_is_puhui(item)
        puhui_dist[p] = puhui_dist.get(p, 0) + 1

        # 服务模式（可多选）
        modes = infer_service_modes(item)
        for m in modes:
            service_dist[m] = service_dist.get(m, 0) + 1

    return {
        "city_distribution": city_dist,
        "host_type_distribution": host_dist,
        "puhui_distribution": puhui_dist,
        "service_mode_distribution": service_dist,
    }


def _questionnaire_posting_stats(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """问卷星岗位/薪酬/证书等聚合统计"""
    posting_cols = ["最缺岗位", "岗位", "紧缺岗位", "需求岗位", "岗位需求"]
    salary_cols = ["薪酬", "薪资", "工资", "薪酬水平"]
    cert_cols = ["证书", "资质", "资格证书"]

    def _first_existing(cols: List[str], row: Dict) -> Any:
        for c in cols:
            if c in row and row[c]:
                return row[c]
        return None

    posting_dist: Dict[str, int] = {}
    for row in data:
        v = _first_existing(posting_cols, row)
        if v:
            v = str(v).strip()
            posting_dist[v] = posting_dist.get(v, 0) + 1

    sample_details = []
    for row in data[:50]:
        sample_details.append({k: v for k, v in row.items() if v and str(v).strip()})

    return {
        "posting_distribution": posting_dist,
        "sample_count": len(data),
        "details_sample": sample_details,
    }


def compute_stats(
    school: Optional[str] = None,
    major: Optional[str] = None,
    region: Optional[str] = None,
    education_level: Optional[str] = None,
    started_time: Optional[int] = None,
    details_limit: int = 50,
) -> Dict[str, Any]:
    """
    计算统计数与详情
    返回：stats (region + national) + details
    """
    inst_all = load_institutions()
    questionnaire = load_questionnaire()

    # 机构
    inst_region = filter_institutions(inst_all, region, "region")
    inst_national = inst_all

    # 学校：region 时只加载该省文件以加速，national 需加载全部
    if region:
        schools_region_raw = filter_schools(
            load_schools(region_filter=region), region, major, started_time, education_level, "region"
        )
        schools_national_raw = filter_schools(
            load_schools(), None, major, started_time, education_level, "national"
        )
    else:
        schools_all = load_schools()
        schools_region_raw = filter_schools(
            schools_all, region, major, started_time, education_level, "region"
        )
        schools_national_raw = filter_schools(
            schools_all, None, major, started_time, education_level, "national"
        )
    # school_count = 开设某专业的培养点记录数（婴幼儿托育 189 条）
    schools_region = schools_region_raw
    schools_national = schools_national_raw

    # 问卷星
    q_region = filter_questionnaire_by_region(questionnaire, region)
    q_national = questionnaire
    posting_region = _questionnaire_posting_stats(q_region)
    posting_national = _questionnaire_posting_stats(q_national)

    # 交叉验证
    cross_region = cross_validate_institutions(inst_region, q_region)
    cross_national = cross_validate_institutions(inst_national, q_national)

    # 机构分布统计（城市、举办主体、普惠、服务模式）
    inst_dists_region = _compute_institution_distributions(inst_region)
    inst_dists_national = _compute_institution_distributions(inst_national)

    # 学校按省份分布
    school_dist_region = _compute_school_distribution(schools_region)
    school_dist_national = _compute_school_distribution(schools_national)

    return {
        "stats": {
            "region": {
                "institution_count": len(inst_region),
                "city_distribution": inst_dists_region["city_distribution"],
                "host_type_distribution": inst_dists_region["host_type_distribution"],
                "puhui_distribution": inst_dists_region["puhui_distribution"],
                "service_mode_distribution": inst_dists_region["service_mode_distribution"],
                "_inferred_note": "普惠、服务模式按名称关键词推断，仅供参考",
                "school_count": len(schools_region),
                "school_distribution": school_dist_region,
                "posting_sample_count": posting_region["sample_count"],
                "matched_institution_count": cross_region["matched_count"],
            },
            "national": {
                "institution_count": len(inst_national),
                "city_distribution": inst_dists_national["city_distribution"],
                "host_type_distribution": inst_dists_national["host_type_distribution"],
                "puhui_distribution": inst_dists_national["puhui_distribution"],
                "service_mode_distribution": inst_dists_national["service_mode_distribution"],
                "_inferred_note": "普惠、服务模式按名称关键词推断，仅供参考",
                "school_count": len(schools_national),
                "school_distribution": school_dist_national,
                "posting_sample_count": posting_national["sample_count"],
                "matched_institution_count": cross_national["matched_count"],
            },
        },
        "details": {
            "institutions": [_institution_detail(x) for x in inst_region[:details_limit]],
            "schools": [_school_detail(x) for x in schools_region[:details_limit]],
            "questionnaire_posting": posting_region.get("posting_distribution", {}),
            "questionnaire_details_sample": posting_region.get("details_sample", []),
            "cross_validation": {
                "region_matched_count": cross_region["matched_count"],
                "national_matched_count": cross_national["matched_count"],
            },
        },
    }
