# -*- coding: utf-8 -*-
"""
托育数据统计管道 HTTP API 服务
供外部系统调用 pipeline.main 与 questionnaire_main 功能

启动: python -m pipeline.server
     uvicorn pipeline.server:app --host 0.0.0.0 --port 8000
"""

from typing import Any, Dict, Optional

try:
    from fastapi import FastAPI, Query
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
except ImportError:
    raise ImportError("请安装: pip install fastapi uvicorn")

from .api import get_stats
from .questionnaire_extract import get_talent_demand

app = FastAPI(
    title="托育数据统计管道 API",
    description="机构、学校、问卷星统计与人才需求提取",
    version="1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- 请求体模型 ---

class StatsRequest(BaseModel):
    school: Optional[str] = None
    major: Optional[str] = None
    region: Optional[str] = None
    education_level: Optional[str] = None
    started_time: Optional[int] = None
    details_limit: int = 50
    use_cache: bool = True
    no_questionnaire_details: bool = False


class JobDemandRequest(BaseModel):
    region: Optional[str] = None
    details_limit: int = 10
    filter_meaningless_postings: bool = True


# --- 接口 ---

@app.get("/")
def root() -> Dict[str, str]:
    return {
        "service": "托育数据统计管道 API",
        "docs": "/docs",
        "stats": "/stats",
        "job_demand": "/job_demand",
    }


@app.get("/stats", response_model=None)
def api_get_stats(
    school: Optional[str] = Query(None, description="院校名称"),
    major: Optional[str] = Query(None, description="专业，如 520802 或 婴幼儿托育服务与管理"),
    region: Optional[str] = Query(None, description="区域，如 广东省、广州市"),
    education_level: Optional[str] = Query(None, description="学历层次"),
    started_time: Optional[int] = Query(None, description="调研开始年份"),
    details_limit: int = Query(50, ge=0, le=500),
    use_cache: bool = Query(True),
    no_questionnaire_details: bool = Query(False, description="不返回问卷详情"),
) -> Dict[str, Any]:
    """机构、学校、问卷星综合统计（对应 pipeline.main）"""
    result = get_stats(
        school=school,
        major=major,
        region=region,
        education_level=education_level,
        started_time=started_time,
        details_limit=details_limit,
        use_cache=use_cache,
    )
    if no_questionnaire_details and "details" in result:
        for key in ("questionnaire_posting", "questionnaire_details_sample"):
            result["details"].pop(key, None)
    return result


@app.post("/stats", response_model=None)
def api_post_stats(req: StatsRequest) -> Dict[str, Any]:
    """机构、学校、问卷星综合统计（POST 请求体）"""
    result = get_stats(
        school=req.school,
        major=req.major,
        region=req.region,
        education_level=req.education_level,
        started_time=req.started_time,
        details_limit=req.details_limit,
        use_cache=req.use_cache,
    )
    if req.no_questionnaire_details and "details" in result:
        for key in ("questionnaire_posting", "questionnaire_details_sample"):
            result["details"].pop(key, None)
    return result


@app.get("/job_demand", response_model=None)
def api_get_job_demand(
    region: Optional[str] = Query(None, description="区域，如 广东省"),
    details_limit: int = Query(10, ge=0, le=100),
    filter_meaningless_postings: bool = Query(True, description="过滤无意义岗位，默认 True"),
) -> Dict[str, Any]:
    """问卷星人才需求提取：岗位及对应的学历、能力、证书要求（对应 questionnaire_main）"""
    return get_talent_demand(
        region=region,
        details_limit=details_limit,
        filter_meaningless_postings=filter_meaningless_postings,
    )


@app.post("/job_demand", response_model=None)
def api_post_job_demand(req: JobDemandRequest) -> Dict[str, Any]:
    """问卷星人才需求提取（POST 请求体）"""
    return get_talent_demand(
        region=req.region,
        details_limit=req.details_limit,
        filter_meaningless_postings=req.filter_meaningless_postings,
    )


def run_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    """启动服务"""
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--host", default="0.0.0.0", help="监听地址")
    p.add_argument("--port", type=int, default=8000, help="监听端口")
    args = p.parse_args()
    run_server(host=args.host, port=args.port)
