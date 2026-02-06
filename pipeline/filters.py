# -*- coding: utf-8 -*-
"""
筛选逻辑：按区域、专业、年份等条件过滤
"""

import re
from typing import Any, Dict, List, Optional, Set, Tuple

from .config import TUOYU_MAJOR_CODES, TUOYU_MAJOR_NAMES
from .loader import parse_zoning


def filter_institutions(
    data: List[Dict[str, Any]],
    region: Optional[str] = None,
    scope: str = "region",
) -> List[Dict[str, Any]]:
    """
    筛选机构
    scope='region': 仅保留 region 对应省/市的机构
    scope='national': 不按区域筛选
    region 可匹配省名或市名（如 广东省、广州市）
    """
    if scope == "national" or not region:
        return list(data)

    region = region.strip()
    result = []
    for item in data:
        zoning = item.get("zoning_name") or ""
        prov, city = parse_zoning(zoning)
        if region in (prov, city, zoning) or zoning.startswith(region):
            result.append(item)
    return result


def _match_major(开设专业: str, major: Optional[str], major_codes: Tuple[str, ...], major_names: Tuple[str, ...]) -> bool:
    """判断专业是否匹配（托育相关或指定 major）"""
    if not 开设专业:
        return False
    # 指定 major 时仅匹配该专业，不再匹配其他托育相关专业
    if major:
        if major in 开设专业:
            return True
        code_match = re.search(r"\((\d+[K]?)\)", 开设专业)
        if code_match and major == code_match.group(1):
            return True
        return False
    # 未指定 major 时，匹配托育相关专业
    for code in major_codes:
        if code in 开设专业:
            return True
    for name in major_names:
        if name in 开设专业:
            return True
    return False


def filter_schools(
    data: List[Dict[str, Any]],
    region: Optional[str] = None,
    major: Optional[str] = None,
    year_from: Optional[int] = None,
    education_level: Optional[str] = None,
    scope: str = "region",
    major_codes: Optional[Tuple[str, ...]] = None,
    major_names: Optional[Tuple[str, ...]] = None,
) -> List[Dict[str, Any]]:
    """
    筛选学校
    region: 省份（如 安徽省）
    major: 专业名称或代码
    year_from: 年份下限
    education_level: 高职专科/本科等，通过修业年限推断
    scope: region / national
    """
    major_codes = major_codes or TUOYU_MAJOR_CODES
    major_names = major_names or TUOYU_MAJOR_NAMES

    result = []
    for item in data:
        if scope == "region" and region:
            if item.get("省份") != region:
                continue
        if not _match_major(item.get("开设专业", ""), major, major_codes, major_names):
            continue
        try:
            y = int(item.get("年份", 0))
            if year_from is not None and y < year_from:
                continue
        except (ValueError, TypeError):
            pass
        if education_level:
            years = item.get("修业年限", "")
            if "本科" in education_level and str(years) not in ("4", "5"):
                continue
            if "专科" in education_level and str(years) not in ("2", "3"):
                continue
        result.append(item)
    return result


def unique_schools(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """按 (机构名称, 开设专业, 年份) 去重，返回培养点列表"""
    seen: Set[Tuple[str, str, str]] = set()
    out = []
    for item in data:
        key = (item.get("机构名称", ""), item.get("开设专业", ""), str(item.get("年份", "")))
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def unique_schools_by_institution(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    按 (机构名称, 年份) 去重：同一院校同一年不论学制(2/3/5年)只计 1
    用于 school_count：开设某专业的院校-年份培养点数
    （219 含同年多学制重复，本去重后约 182）
    """
    seen: Set[Tuple[str, str]] = set()
    out = []
    for item in data:
        name = item.get("机构名称", "").strip()
        year = str(item.get("年份", ""))
        if not name:
            continue
        key = (name, year)
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def filter_questionnaire_by_region(
    data: List[Dict[str, Any]],
    region: Optional[str],
    region_columns: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    按区域筛选问卷星（若存在区域相关列）
    region_columns: 可能包含省/市信息的列名，如 ['省份','城市','所在地区']
    匹配规则：region 与单元格值互相包含，或去除「省」「市」后匹配
    """
    if not region or not data:
        return data
    region_columns = region_columns or ["省份", "城市", "所在地区", "地区", "区域"]
    # 宽松匹配：广东省 / 广东、广州市 / 广州 互匹配
    region_norm = (region or "").replace("省", "").replace("市", "").strip()

    def _match(region: str, cell_val: str) -> bool:
        if not cell_val:
            return False
        s = str(cell_val).strip()
        if region in s or s in region:
            return True
        cell_norm = s.replace("省", "").replace("市", "").strip()
        if region_norm and (region_norm in cell_norm or cell_norm in region_norm):
            return True
        return False

    result = []
    for row in data:
        for col in region_columns:
            if col in row and _match(region, str(row[col] or "")):
                result.append(row)
                break
    return result if result else data
