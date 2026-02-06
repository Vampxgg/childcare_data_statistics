# -*- coding: utf-8 -*-
"""管道配置：数据路径与常量"""

from pathlib import Path

# 工作区根目录（pipeline 的父目录）
ROOT = Path(__file__).resolve().parent.parent

# 数据路径
DB_DIR = ROOT / "db"
INSTITUTION_JSON = DB_DIR / "托育机构平台注册备案数据.json"
QUESTIONNAIRE_XLSX = DB_DIR / "问卷星统计_托育机构人才需求专项调查_20260120.xlsx"
SCHOOL_DIR = DB_DIR / "托育学校注册备案数据"
CACHE_DIR = DB_DIR / "_stats_cache"
MANIFEST_DIR = DB_DIR / "_manifest"

# 托育相关专业代码（用于学校筛选）
# 520802=婴幼儿托育服务与管理, 570101K=早期教育, 660225=早期教育(部分目录)
TUOYU_MAJOR_CODES = ("520802", "570101K", "660225")
TUOYU_MAJOR_NAMES = ("婴幼儿托育服务与管理", "早期教育", "托育")

# 学校文件命名 pattern: moe_majors_{省}_{年}.txt
SCHOOL_FILE_PATTERN = "moe_majors_*.txt"
