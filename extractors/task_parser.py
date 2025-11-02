import json
from typing import List, Dict
import pandas as pd
from utils.cleaner import clean_frequency
from utils.parsers import parse_emty_string, parse_stt, parse_date, parse_cost
from config.settings import DEFAULT_COST_UNIT
import re

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
    # df.to_csv("output.csv", index=False, encoding='utf-16') 
    # print(df.columns.tolist())
    
    # clean data
    
    df['frequency'] = df['Từ'].apply(clean_frequency)
    columns_to_clean = ['Đánh giá khó khăn thuận lợi/Tồn đọng', 'Kết quả thực hiện', 'Đ/G KQ','Loại công việc','Chi phí thực hiện (VNĐ)']
    for col in columns_to_clean:
        if col in df.columns:
            df[col] = df[col].apply(parse_emty_string)
        
    pass
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
            "frequency": str(row.get('frequency', '')).strip(),
            "startDate": parse_date(row.get('Từ', '')),
            "endDate": parse_date(row.get('Đến', '')),
            # "notes": "",
            "hasSubtasks": False,
            "subtaskCount": 0,
            # "children": []
        }
        
        if task_type == "actual":
            task["result"] = str(row.get('Kết quả thực hiện', '')).strip()
            task["challenges"] = str(row.get('Đánh giá khó khăn thuận lợi/Tồn đọng', '')).strip()
            task["evaluation"] = str(row.get('Đ/G KQ', '')).strip()
            # task["actualStartDate"] = task["startDate"]
            # task["actualEndDate"] = task["endDate"] if task["evaluation"] == "Hoàn thành" else None
            # task["completionRate"] = 100 if task["evaluation"] == "Hoàn thành" else 0
        else:
            task["desc"] = str(row.get('Mô tả yêu cầu, giải pháp để thực hiện', '')).strip()
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
                # parent['children'].append(task['taskId'])
    # for task in tasks:
    #     print(f"{task['stt']}: {task['taskName']}-{task['frequency']}")

    return tasks