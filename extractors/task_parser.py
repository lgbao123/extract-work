from typing import List, Dict
import pandas as pd
from utils.parsers import parse_stt, parse_date, parse_cost
from config.settings import DEFAULT_COST_UNIT


def parse_tasks_from_dataframe(df: pd.DataFrame, task_type: str = "actual", prefix: str = "T") -> List[Dict]:
    """
    Parse tasks từ DataFrame
    
    Args:
        df: DataFrame chứa dữ liệu tasks
        task_type: "actual" hoặc "planned"
        prefix: Prefix cho taskId ("T" hoặc "PT")
        
    Returns:
        List các task dict với hasSubtasks flag
    """
    tasks = []
    task_id_counter = 1
    stt_to_task_id = {}
    print(df.columns)
    df.to_csv("output.csv", index=False, encoding='utf-16') 
    print(len(df))
    # Pass 1: Parse tất cả tasks
    for idx, row in df.iterrows():
        if pd.isna(row.get('Công việc', '')) or str(row.get('Công việc', '')).strip() == '':
            continue
        
        stt = str(row.get('Stt', '')).strip()
        level, parent_stt = parse_stt(stt)
        # print(level, parent_stt)
        # break
        task_id = f"{prefix}{task_id_counter:03d}"
        task_id_counter += 1
        
        parent_task_id = stt_to_task_id.get(parent_stt) if parent_stt else None
        stt_to_task_id[stt] = task_id
        
        task = {
            "taskId": task_id,
            "stt": stt,
            "parentTaskId": parent_task_id,
            "level": level,
            "taskName": str(row.get('Công việc', '')).strip(),
            "taskType": str(row.get('Loại công việc', '')).strip(),
            "startDate": parse_date(row.get('Từ', '')),
            "endDate": parse_date(row.get('Đến', '')),
            "description": str(row.get('Mô tả yêu cầu, giải pháp để thực hiện', '')).strip(),
            "solution": str(row.get('Mô tả yêu cầu, giải pháp để thực hiện', '')).strip(),
            "notes": "",
            "hasSubtasks": False,
            "subtaskCount": 0,
            "children": []
        }
        
        if task_type == "actual":
            task["evaluation"] = str(row.get('Đ/G KQ', '')).strip()
            task["actualStartDate"] = task["startDate"]
            task["actualEndDate"] = task["endDate"] if task["evaluation"] == "Hoàn thành" else None
            task["completionRate"] = 100 if task["evaluation"] == "Hoàn thành" else 0
        else:
            task["estimatedCost"] = parse_cost(row.get('Chi phí thực hiện (VNĐ)', '0'))
            task["costUnit"] = DEFAULT_COST_UNIT
        
        tasks.append(task)

    # Pass 2: Update hasSubtasks
    for task in tasks:
        if task['parentTaskId']:
            parent = next((t for t in tasks if t['taskId'] == task['parentTaskId']), None)
            if parent:
                parent['hasSubtasks'] = True
                parent['subtaskCount'] += 1
                parent['children'].append(task['taskId'])
    
    return tasks