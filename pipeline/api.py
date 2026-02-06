# -*- coding: utf-8 -*-
"""
统一 API：get_stats
支持增量缓存，数据未更新时直接返回缓存
"""

from typing import Any, Dict, Optional

from .cache import get_cached, get_data_fingerprints, set_cached
from .stats import compute_stats


def get_stats(
    school: Optional[str] = None,
    major: Optional[str] = None,
    region: Optional[str] = None,
    education_level: Optional[str] = None,
    started_time: Optional[int] = None,
    details_limit: int = 50,
    use_cache: bool = True,
) -> Dict[str, Any]:
    """
    获取统计数据与详情

    参数:
        school: 院校名称（可选）
        major: 专业名称或代码，如 婴幼儿托育服务与管理 / 520802
        region: 区域，省或市，如 广东省 / 广州市
        education_level: 学历层次，如 高职专科 / 本科
        started_time: 调研数据开始年份
        details_limit: 详情条数上限
        use_cache: 是否使用增量缓存

    返回:
        {
            "stats": {"region": {...}, "national": {...}},
            "details": {...},
            "meta": {"from_cache": bool, "fingerprints": {...}}
        }
    """
    cached = None
    if use_cache:
        cached = get_cached(school, major, region, education_level, started_time)
        if cached is not None:
            return {
                **cached,
                "meta": {
                    "from_cache": True,
                    "fingerprints": get_data_fingerprints(),
                },
            }

    result = compute_stats(
        school=school,
        major=major,
        region=region,
        education_level=education_level,
        started_time=started_time,
        details_limit=details_limit,
    )

    if use_cache:
        set_cached(school, major, region, education_level, started_time, result)

    return {
        **result,
        "meta": {
            "from_cache": False,
            "fingerprints": get_data_fingerprints(),
        },
    }
