import os
import re

folder = r"c:\Users\admin\Desktop\ISP 年度目標（目標設定）"

files = [f for f in os.listdir(folder) if f.endswith('.md')]

data = []

for file in files:
    path = os.path.join(folder, file)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract Service User
    user_match = re.search(r'服務對象:\s*([^\(]+)', content)
    # Some files might not have 服務對象 formatted exactly like that
    user = user_match.group(1).strip() if user_match else "Unknown"
    
    if user == "Unknown":
        user_match = re.search(r'執行狀況說明:\s*([^\(]+)', content)
        user = user_match.group(1).strip() if user_match else "Unknown"
    
    # Extract Goal Number & Name
    goal_match = re.search(r'# (支持目標[^:]+):\n([^\n]+)', content)
    if goal_match:
        goal = f"{goal_match.group(1).strip()} {goal_match.group(2).strip()}"
    else:
        # Check if it starts with "# " and not 支持目標
        lines = content.split('\n')
        if lines and lines[0].startswith('# '):
            goal = lines[0][2:].strip()
            if len(lines) > 1 and lines[1].strip() and not lines[1].startswith('115年'):
                goal += " " + lines[1].strip()
        else:
            goal = file.replace('.md', '')
            goal = re.sub(r' [a-f0-9]{32}$', '', goal)
            
    # Remove # 支持目標1-1: \n
    goal = goal.replace(':', '')
    
    # Extract 115年達成狀態
    status_match = re.search(r'115年[^:]*:\s*([^\n]+)', content)
    status = "❌ 未標註"
    if status_match:
        val = status_match.group(1).strip()
        if '✅' in val or '達標' in val and '未' not in val:
            status = "✅"
        elif '❌' in val or '未達標' in val:
            status = "❌"
        else:
            if '✅' in val:
                status = "✅"
            else:
                status = val
                
    # Extract Core Support Strategy
    strategy_match = re.search(r'支持策略:\s*\n((?:[•\-*].*\n?)*)', content)
    if not strategy_match:
        strategy_match = re.search(r'支持策略:\s*(.*?)\n(?:支持領域|服務對象|狀態|生活品質|通過標準)', content, re.DOTALL)
        
    strategies = []
    if strategy_match:
        s_text = strategy_match.group(1).strip()
        for line in s_text.split('\n'):
            line = line.strip()
            if line:
                line = re.sub(r'^[•\-*]\s*', '', line)
                strategies.append(line)
    
    # Truncate to 3 points
    strategies = strategies[:3]
    strategy_str = "<br>".join([f"- {s}" for s in strategies])
    
    # Extract Quality of Life
    qol_match = re.search(r'生活品質:\s*([^\n]+)', content)
    qol = qol_match.group(1).strip() if qol_match else "-"
    
    # Extract Passing Criteria
    criteria_match = re.search(r'通過標準:\s*([^\n]+)', content)
    criteria = criteria_match.group(1).strip() if criteria_match else "-"
    
    # Skip duplicates if any (based on content/goal)
    data.append({
        'user': user,
        'goal': goal,
        'status': status,
        'strategy': strategy_str,
        'qol': qol,
        'criteria': criteria,
        'file': file
    })

# Deduplicate by goal and user
unique_data = []
seen = set()
for d in data:
    key = (d['user'], d['goal'])
    if key not in seen:
        seen.add(key)
        unique_data.append(d)

unique_data.sort(key=lambda x: (x['user'], x['goal']))

print(len(unique_data), "unique goals found.")

import json
with open('parsed_isp.json', 'w', encoding='utf-8') as f:
    json.dump(unique_data, f, ensure_ascii=False, indent=2)

