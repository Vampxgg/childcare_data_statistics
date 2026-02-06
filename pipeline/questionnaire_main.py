# -*- coding: utf-8 -*-
"""
问卷星人才需求提取命令行入口
用途：从问卷星中提取最短缺岗位、岗位薪酬、学历要求、能力、证书、人才能力类型等，
     供产业区域分析报告、人才需求分析报告生成图表与实时数据。

用法（参数与 pipeline.main 一致）:
    python -m pipeline.questionnaire_main
    python -m pipeline.questionnaire_main --region 广东省
    python -m pipeline.questionnaire_main --region 安徽省 --no-cache

依赖: pip install pandas openpyxl（至少其一，用于读取 xlsx）
"""

import argparse
import json
import sys

from .loader import load_questionnaire
from .questionnaire_extract import get_talent_demand


def main() -> int:
    parser = argparse.ArgumentParser(
        description="问卷星人才需求提取：岗位、薪酬、学历、能力、证书、人才能力类型"
    )
    parser.add_argument("--school", type=str, help="院校名称（保留，与 pipeline.main 对齐）")
    parser.add_argument("--major", type=str, help="专业（保留，与 pipeline.main 对齐）")
    parser.add_argument("--region", type=str, help="区域，如 安徽省、广东省")
    parser.add_argument("--education_level", type=str, help="学历层次（保留参数）")
    parser.add_argument("--started_time", type=int, help="调研开始年份（保留参数）")
    parser.add_argument("--no-cache", action="store_true", help="禁用缓存（保留参数）")
    parser.add_argument("--details-limit", type=int, default=10, help="raw_sample 条数上限")
    parser.add_argument(
        "--no-filter-meaningless",
        action="store_true",
        help="不过滤无意义岗位（默认过滤）",
    )
    args = parser.parse_args()

    result = get_talent_demand(
        region=args.region,
        use_cache=not args.no_cache,
        details_limit=args.details_limit,
        filter_meaningless_postings=not args.no_filter_meaningless,
    )

    # 数据为空时提示
    if result.get("sample_count", 0) == 0:
        raw = load_questionnaire()
        if not raw:
            print(
                "# 提示：问卷星数据未加载成功，请安装依赖: pip install pandas openpyxl",
                file=sys.stderr,
            )

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
