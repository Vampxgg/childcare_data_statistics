# -*- coding: utf-8 -*-
"""
增量缓存：基于数据源 fingerprint，数据未更新时直接返回缓存
"""

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from .config import CACHE_DIR, INSTITUTION_JSON, QUESTIONNAIRE_XLSX, SCHOOL_DIR, SCHOOL_FILE_PATTERN

CACHE_DB = "cache.json"
FINGERPRINT_DB = "fingerprints.json"


def _file_fingerprint(path: Path) -> str:
    """单文件 fingerprint = path + mtime + size"""
    if not path.exists():
        return ""
    st = path.stat()
    s = f"{path!s}|{st.st_mtime}|{st.st_size}"
    return hashlib.sha256(s.encode()).hexdigest()


def get_data_fingerprints() -> Dict[str, str]:
    """
    获取各数据源当前 fingerprint
    数据更新（文件变更）时 fingerprint 变化，需重新统计
    """
    fps: Dict[str, str] = {}

    if INSTITUTION_JSON.exists():
        fps["institution"] = _file_fingerprint(INSTITUTION_JSON)
    else:
        fps["institution"] = ""

    if QUESTIONNAIRE_XLSX.exists():
        fps["questionnaire"] = _file_fingerprint(QUESTIONNAIRE_XLSX)
    else:
        fps["questionnaire"] = ""

    if SCHOOL_DIR.exists():
        parts = []
        for f in sorted(SCHOOL_DIR.glob(SCHOOL_FILE_PATTERN)):
            parts.append(_file_fingerprint(f))
        fps["school"] = hashlib.sha256("|".join(parts).encode()).hexdigest() if parts else ""
    else:
        fps["school"] = ""

    return fps


def _query_key(school: Optional[str], major: Optional[str], region: Optional[str], 
               education_level: Optional[str], started_time: Optional[int]) -> str:
    """生成查询缓存键"""
    parts = [
        school or "",
        major or "",
        region or "",
        education_level or "",
        str(started_time) if started_time is not None else "",
    ]
    s = "|".join(parts)
    return hashlib.sha256(s.encode()).hexdigest()


def _load_cache() -> Dict[str, Any]:
    """加载缓存文件"""
    cache_path = CACHE_DIR / CACHE_DB
    if not cache_path.exists():
        return {}
    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_cache(data: Dict[str, Any]) -> None:
    """保存缓存文件"""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = CACHE_DIR / CACHE_DB
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_cached(
    school: Optional[str],
    major: Optional[str],
    region: Optional[str],
    education_level: Optional[str],
    started_time: Optional[int],
) -> Optional[Dict[str, Any]]:
    """
    若当前数据 fingerprint 与缓存一致，返回缓存结果；否则返回 None
    """
    key = _query_key(school, major, region, education_level, started_time)
    current_fps = get_data_fingerprints()
    cache = _load_cache()
    entry = cache.get(key)
    if not entry:
        return None
    cached_fps = entry.get("fingerprints", {})
    if cached_fps != current_fps:
        return None
    return entry.get("result")


def set_cached(
    school: Optional[str],
    major: Optional[str],
    region: Optional[str],
    education_level: Optional[str],
    started_time: Optional[int],
    result: Dict[str, Any],
) -> None:
    """写入缓存"""
    key = _query_key(school, major, region, education_level, started_time)
    current_fps = get_data_fingerprints()
    cache = _load_cache()
    cache[key] = {
        "fingerprints": current_fps,
        "result": result,
        "query": {
            "school": school,
            "major": major,
            "region": region,
            "education_level": education_level,
            "started_time": started_time,
        },
    }
    _save_cache(cache)


def clear_cache() -> None:
    """清空缓存（数据批量更新后可选调用）"""
    cache_path = CACHE_DIR / CACHE_DB
    if cache_path.exists():
        cache_path.unlink()
