# -*- coding: utf-8 -*-
"""
节点ID: 1761754543279
节点标题: planner
节点描述: 
节点类型: code
"""

import time
import json

def main() -> dict:
  """
  Dify Code Node Main Entry Point.
  This function waits for 2 minutes and then returns a predefined JSON string.
  
  :param input_str: The input string from the upstream node. (Even if not used, it's required for triggering).
  :return: A dictionary where the key 'result' contains the JSON string output.
  """
  
  # 1. 模板数据定义
  template_data = {
  "mockAnalysisSteps": [
    {
      "id": "step-1",
      "title": "宏观视角：湖北省智能网联汽车产业发展环境与关键政策解读"
    },
    {
      "id": "step-2",
      "title": "产业解构：湖北省智能网联汽车产业链图谱绘制与核心环节识别"
    },
    {
      "id": "step-3",
      "title": "空间布局：湖北省智能网联汽车重点企业与产业园区（武汉、襄阳等）分布研究"
    },
    {
      "id": "step-4",
      "title": "竞争力诊断：基于SWOT模型的湖北省智能网联汽车产业优势、劣势、机遇与挑战分析"
    },
    {
      "id": "step-5",
      "title": "就业导向：湖北省智能网联汽车产业人才需求画像与核心岗位技能要求分析"
    },
    {
      "id": "step-6",
      "title": "发展展望：湖北省智能网联汽车技术发展趋势与高职毕业生职业路径规划建议"
    }
  ],
  "confirm": -1
}

  # 2. 等待2分钟 (120秒)
  # 警告：请确保您的Dify环境执行超时时间 > 120秒
  time.sleep(5)

  # 3. 将数据结构转换为JSON字符串
  # ensure_ascii=False 保证中文字符正常显示
  output_string = json.dumps(template_data, ensure_ascii=False)

  # 4. 关键：以Dify要求的字典格式返回输出
  # 'result' 这个key必须与你在UI上定义的输出变量名完全一致
  return {
    'result': output_string
  }


