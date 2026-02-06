# -*- coding: utf-8 -*-
"""
命令行入口：测试统计管道
用法: python -m pipeline.main
     python -m pipeline.main --region 安徽省 --major 520802
"""

import argparse
import json
import sys


def main():
    parser = argparse.ArgumentParser(description="托育数据统计管道")
    parser.add_argument("--school", type=str, help="院校名称")
    parser.add_argument("--major", type=str, help="专业，如 520802 或 婴幼儿托育服务与管理")
    parser.add_argument("--region", type=str, help="区域，如 安徽省、广东省")
    parser.add_argument("--education_level", type=str, help="学历层次")
    parser.add_argument("--started_time", type=int, help="调研开始年份")
    parser.add_argument("--no-cache", action="store_true", help="禁用缓存，强制重新统计")
    parser.add_argument("--details-limit", type=int, default=10, help="详情条数上限")
    parser.add_argument(
        "--no-questionnaire-details",
        action="store_true",
        help="不输出问卷详情（questionnaire_posting、questionnaire_details_sample）",
    )
    args = parser.parse_args()

    from .api import get_stats

    result = get_stats(
        school=args.school,
        major=args.major,
        region=args.region,
        education_level=args.education_level,
        started_time=args.started_time,
        details_limit=args.details_limit,
        use_cache=not args.no_cache,
    )
    if args.no_questionnaire_details and "details" in result:
        for key in ("questionnaire_posting", "questionnaire_details_sample"):
            result["details"].pop(key, None)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
