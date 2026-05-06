import json
import re

def generate_separated():
    # 1. Generate data logic (isp_data.js) from parsed_isp.json
    with open('parsed_isp.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    formatted_data = {}
    for i, item in enumerate(data):
        user = item['user']
        if user not in formatted_data:
            formatted_data[user] = {"midTerm": "", "endTerm": "", "goals": []}
        
        status = "未紀錄"
        if "✅" in item['status']: status = "達標"
        elif "❌" in item['status']: status = "未達標"
        
        strategy = item.get('strategy', '').replace('<br>', '\n')
        
        formatted_data[user]["goals"].append({
            "id": f"g_{user}_{i}",
            "domain": item.get('qol', '未指定'),
            "target": item.get('goal', ''),
            "strategy": strategy,
            "standard": item.get('criteria', ''),
            "status": status,
            "records": [{"month": j, "desc": "", "strategy": "", "rate": 0} for j in range(1, 13)]
        })

    json_str = json.dumps(formatted_data, ensure_ascii=False)
    
    with open('isp_data.js', 'w', encoding='utf-8') as f:
        f.write(f"const defaultData = {json_str};\n")

    # 2. Extract CSS from generate_dashboard.py
    with open('generate_dashboard.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    css_match = re.search(r'<style>(.*?)</style>', content, re.DOTALL)
    css = css_match.group(1).strip() if css_match else ""
    with open('isp_styles.css', 'w', encoding='utf-8') as f:
        f.write(css)

    # 3. Extract HTML body
    body_match = re.search(r'<body>(.*?)<script>', content, re.DOTALL)
    body_html = body_match.group(1).strip() if body_match else ""
    
    html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ANTIGRAVITY ISP Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/sortablejs@latest/Sortable.min.js"></script>
    <link rel="stylesheet" href="isp_styles.css">
</head>
<body>
{body_html}
    <!-- 1. 資料邏輯分離：先載入預設資料 -->
    <script src="isp_data.js"></script>
    <!-- 2. UI 操作與 LocalStorage 邏輯分離：再載入應用程式邏輯 -->
    <script src="isp_app.js"></script>
</body>
</html>"""
    with open('isp_dashboard_separated.html', 'w', encoding='utf-8') as f:
        f.write(html)

    # 4. Extract JS functions and rewrite init/saveData for LocalStorage
    new_init = """let currentData = {};
let currentUser = "";
let editingGoalId = null;

function init() {
    // 確保所有目標資料都是從 LocalStorage 讀取
    const savedData = localStorage.getItem('ispDashboardDataV2');
    
    if (savedData) {
        currentData = JSON.parse(savedData);
    } else {
        // 如果 LocalStorage 為空（首次載入），則載入外部資料檔
        if (typeof defaultData !== 'undefined') {
            currentData = defaultData;
            localStorage.setItem('ispDashboardDataV2', JSON.stringify(currentData));
        }
    }
    
    const users = Object.keys(currentData);
    if(users.length > 0 && !currentUser) {
        currentUser = users[0];
    }
    
    renderTabs();
    renderDashboard();
}

function saveData() {
    localStorage.setItem('ispDashboardDataV2', JSON.stringify(currentData));
}
"""
    # Grab from renderTabs to the end
    render_tabs_match = re.search(r'function renderTabs\(\) \{.*', content, re.DOTALL)
    if render_tabs_match:
        rest_of_js = render_tabs_match.group(0)
        # Remove trailing HTML tags and python string quotes
        rest_of_js = rest_of_js.replace('</script>', '').replace('</body>', '').replace('</html>', '').replace('window.onload = init;', '').replace('\"\"\"', '').strip()
    else:
        rest_of_js = ""
    
    with open('isp_app.js', 'w', encoding='utf-8') as f:
        f.write(new_init + "\n" + rest_of_js + "\n\nwindow.onload = init;\n")

if __name__ == '__main__':
    generate_separated()
