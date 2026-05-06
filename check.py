import os
import re
import json

folder = r"c:\Users\admin\Desktop\ISP 年度目標（目標設定）"
files = [f for f in os.listdir(folder) if f.endswith('.md')]

data = []
for file in files:
    path = os.path.join(folder, file)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    goal_match = re.search(r'# (支持目標[^:]+):\n([^\n]+)', content)
    if not goal_match:
        goal_match = re.search(r'# (.*?)\n', content)
        goal = goal_match.group(1).strip() if goal_match else file
    else:
        goal = f"{goal_match.group(1).strip()} {goal_match.group(2).strip()}"
        
    status_match = re.search(r'115年[^:]*:\s*([^\n]+)', content)
    status = status_match.group(1).strip() if status_match else "未標註"
    
    exec_status_match = re.search(r'執行狀況說明:\s*([^\n]+)', content)
    exec_status = exec_status_match.group(1).strip() if exec_status_match else ""
    
    exec_summary_match = re.search(r'執行成效總結:\s*([^\n]+)', content)
    exec_summary = exec_summary_match.group(1).strip() if exec_summary_match else ""
    
    print(f"Goal: {goal}")
    if exec_summary:
        print(f"  Summary: {exec_summary}")
    if exec_status:
        print(f"  Status: {exec_status}")

