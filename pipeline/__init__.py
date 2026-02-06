# -*- coding: utf-8 -*-
"""
托育专业数据统计管道
支持机构、学校、问卷星数据抽取与统计，含增量缓存
"""

from .api import get_stats

__all__ = ["get_stats"]
