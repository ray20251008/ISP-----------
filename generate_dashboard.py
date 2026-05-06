import json
import os

def generate():
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

    html_content = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ANTIGRAVITY ISP Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/sortablejs@latest/Sortable.min.js"></script>
    <!-- Firebase SDK -->
    <script src="https://www.gstatic.com/firebasejs/10.9.0/firebase-app-compat.js"></script>
    <script src="https://www.gstatic.com/firebasejs/10.9.0/firebase-database-compat.js"></script>
    <style>
        :root {
            /* Updated to Soft Purple/Blue Gradient */
            --primary-gradient: linear-gradient(135deg, #E0C3FC 0%, #8EC5FC 100%);
            --bg-color: #f4f7fb;
            --card-bg: rgba(255, 255, 255, 0.85);
            --text-main: #1a202c;
            --text-muted: #4a5568;
            --border-radius: 32px; /* 3xl border radius */
            --shadow: 0 20px 50px rgba(142, 197, 252, 0.15); /* Stronger shadow */
            
            /* Status Tag Colors */
            --status-red-bg: rgba(252, 129, 129, 0.15);
            --status-red-text: #c53030;
            --status-green-bg: rgba(104, 211, 145, 0.15);
            --status-green-text: #276749;
            --status-gray-bg: rgba(203, 213, 224, 0.3);
            --status-gray-text: #4a5568;
            
            --btn-blue: #8EC5FC;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        body {
            background: var(--bg-color);
            color: var(--text-main);
            min-height: 100vh;
            padding-bottom: 50px;
        }

        header {
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(10px);
            padding: 20px 40px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.03);
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 100;
        }

        h1 {
            font-size: 28px;
            font-weight: 800; /* Bolder */
            letter-spacing: -0.5px;
            background: var(--primary-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .header-actions {
            display: flex;
            align-items: center;
            gap: 20px;
        }

        .tabs {
            display: flex;
            gap: 12px;
            background: #edf2f7;
            padding: 5px;
            border-radius: 40px;
        }

        .tab-btn {
            padding: 10px 24px;
            border: none;
            background: transparent;
            border-radius: 30px;
            cursor: pointer;
            font-weight: 700;
            color: var(--text-muted);
            transition: all 0.3s ease;
            letter-spacing: 0.5px;
        }

        .tab-btn.active {
            background: white;
            color: #6b46c1; /* Match purple theme */
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        }

        .btn-add-goal {
            padding: 12px 24px;
            border: none;
            background: var(--primary-gradient);
            color: white;
            border-radius: 30px;
            font-weight: 700;
            font-size: 15px;
            cursor: pointer;
            box-shadow: 0 10px 20px rgba(142, 197, 252, 0.3);
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .btn-add-goal:hover {
            transform: translateY(-2px);
            box-shadow: 0 15px 25px rgba(142, 197, 252, 0.4);
        }

        .container {
            max-width: 1300px;
            margin: 40px auto;
            padding: 0 20px;
        }

        .cards-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
            gap: 35px;
        }

        .card {
            background: var(--card-bg);
            border-radius: var(--border-radius);
            padding: 30px;
            box-shadow: var(--shadow);
            position: relative;
            border: 1px solid rgba(255,255,255,0.6);
            backdrop-filter: blur(20px);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            display: flex;
            flex-direction: column;
        }

        .card:hover {
            transform: translateY(-8px);
            box-shadow: 0 25px 60px rgba(142, 197, 252, 0.25);
        }

        .status-badge {
            position: absolute;
            top: 25px;
            right: 25px;
            padding: 6px 14px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.5px;
            display: flex;
            align-items: center;
            gap: 4px;
        }
        
        .status-badge::before {
            content: '';
            display: inline-block;
            width: 6px;
            height: 6px;
            border-radius: 50%;
        }

        .status-red { background: var(--status-red-bg); color: var(--status-red-text); }
        .status-red::before { background: var(--status-red-text); }
        .status-green { background: var(--status-green-bg); color: var(--status-green-text); }
        .status-green::before { background: var(--status-green-text); }
        .status-gray { background: var(--status-gray-bg); color: var(--status-gray-text); }
        .status-gray::before { background: var(--status-gray-text); }

        .card-header {
            margin-bottom: 25px;
            padding-right: 80px;
            padding-left: 30px;
        }

        .domain-tag {
            display: inline-block;
            padding: 6px 14px;
            background: #f1f5f9;
            border-radius: 12px;
            font-size: 13px;
            font-weight: 600;
            color: #64748b;
            margin-bottom: 12px;
            letter-spacing: 0.5px;
        }

        .goal-title {
            font-size: 20px;
            font-weight: 800;
            line-height: 1.4;
            color: #1a202c;
            letter-spacing: -0.3px;
        }

        .section-title {
            font-size: 14px;
            color: #718096;
            margin-bottom: 8px;
            margin-top: 20px;
            font-weight: 700;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }

        .content-text {
            font-size: 15px;
            line-height: 1.7;
            color: #2d3748;
            background: rgba(247, 250, 252, 0.6);
            padding: 15px 20px;
            border-radius: 16px;
            border: 1px solid rgba(226, 232, 240, 0.5);
            flex-grow: 1;
        }

        .progress-section {
            margin-top: 25px;
            padding-top: 25px;
            border-top: 1px solid rgba(226, 232, 240, 0.8);
        }

        .progress-bar-bg {
            height: 10px;
            background: #edf2f7;
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 8px;
        }

        .progress-bar-fill {
            height: 100%;
            background: var(--primary-gradient);
            width: 0%;
            transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
            border-radius: 10px;
        }

        .progress-text {
            display: flex;
            justify-content: space-between;
            font-size: 13px;
            font-weight: 600;
            color: var(--text-muted);
        }

        .actions {
            margin-top: 25px;
            display: flex;
            justify-content: space-between;
            gap: 15px;
        }

        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            font-weight: 700;
            transition: all 0.2s;
            font-size: 14px;
            letter-spacing: 0.5px;
            flex: 1;
        }

        .btn:hover {
            transform: translateY(-2px);
        }

        .btn-edit {
            background: #f1f5f9;
            color: #334155;
        }
        
        .btn-edit:hover { background: #e2e8f0; }

        .btn-records {
            background: white;
            color: #6b46c1;
            border: 1px solid #e9d8fd;
        }
        
        .btn-records:hover { background: #faf5ff; }

        .btn-delete {
            background: #fff5f5;
            color: #c53030;
            border: 1px solid #fed7d7;
            padding: 10px;
            flex: 0 0 auto;
        }
        
        .btn-delete:hover {
            background: #fed7d7;
            color: #9b2c2c;
        }

        .drag-handle {
            position: absolute;
            top: 25px;
            left: 20px;
            cursor: grab;
            color: #cbd5e0;
            font-size: 20px;
            padding: 5px;
            line-height: 1;
            transition: color 0.2s;
        }
        
        .drag-handle:hover {
            color: #718096;
        }
        
        .drag-handle:active {
            cursor: grabbing;
        }

        .sortable-ghost {
            opacity: 0.4;
            background: #edf2f7;
            border: 2px dashed #cbd5e0;
            box-shadow: none !important;
            transform: none !important;
        }

        /* Expanded Records */
        .records-area {
            display: none;
            margin-top: 20px;
            max-height: 400px;
            overflow-y: auto;
            background: rgba(247, 250, 252, 0.8);
            border-radius: 20px;
            padding: 20px;
            border: 1px solid rgba(226, 232, 240, 0.8);
        }

        .records-area.active {
            display: block;
            animation: fadeIn 0.3s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .month-record {
            margin-bottom: 20px;
            padding-bottom: 20px;
            border-bottom: 1px dashed #cbd5e0;
        }

        .month-record:last-child {
            border-bottom: none;
            margin-bottom: 0;
            padding-bottom: 0;
        }

        .month-title {
            font-weight: 800;
            font-size: 15px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            color: #2d3748;
        }

        .month-desc-label {
            font-size: 12px;
            font-weight: 700;
            color: #718096;
            margin-bottom: 4px;
            text-transform: uppercase;
        }
        
        .month-desc {
            font-size: 14px;
            color: #4a5568;
            margin-bottom: 10px;
            line-height: 1.5;
            background: white;
            padding: 10px;
            border-radius: 8px;
        }

        /* Evaluation Section */
        .evaluation-section {
            margin-top: 60px;
            background: var(--card-bg);
            padding: 40px;
            border-radius: var(--border-radius);
            box-shadow: var(--shadow);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255,255,255,0.6);
        }

        .evaluation-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 40px;
        }

        textarea {
            width: 100%;
            padding: 20px;
            border: 2px solid #e2e8f0;
            border-radius: 16px;
            resize: vertical;
            font-family: inherit;
            font-size: 15px;
            line-height: 1.6;
            transition: all 0.3s;
            background: #f8fafc;
        }

        textarea:focus {
            outline: none;
            border-color: #b794f4;
            background: white;
            box-shadow: 0 0 0 4px rgba(183, 148, 244, 0.1);
        }

        /* Modal */
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(15, 23, 42, 0.4);
            backdrop-filter: blur(8px);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 1000;
            padding: 20px;
        }

        .modal {
            background: white;
            padding: 40px;
            border-radius: 32px;
            width: 100%;
            max-width: 700px;
            max-height: 90vh;
            overflow-y: auto;
            box-shadow: 0 25px 50px rgba(0,0,0,0.15);
            position: relative;
        }

        .modal.active {
            display: block;
            animation: modalIn 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        }

        @keyframes modalIn {
            from { opacity: 0; transform: scale(0.95) translateY(20px); }
            to { opacity: 1; transform: scale(1) translateY(0); }
        }
        
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
        }
        
        .modal-title {
            font-size: 24px;
            font-weight: 800;
            color: #1a202c;
        }
        
        .btn-close-icon {
            background: #f1f5f9;
            border: none;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            font-size: 18px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background 0.2s;
        }
        
        .btn-close-icon:hover { background: #e2e8f0; }

        .form-group {
            margin-bottom: 25px;
        }

        .form-group label {
            display: block;
            margin-bottom: 10px;
            font-weight: 700;
            font-size: 14px;
            color: #4a5568;
        }

        .form-group input, .form-group textarea, .form-group select {
            width: 100%;
            padding: 14px 18px;
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            font-family: inherit;
            font-size: 15px;
            transition: all 0.2s;
            background: #f8fafc;
        }
        
        .form-group input:focus, .form-group textarea:focus, .form-group select:focus {
            outline: none;
            border-color: #b794f4;
            background: white;
            box-shadow: 0 0 0 3px rgba(183, 148, 244, 0.1);
        }

        .modal-actions {
            display: flex;
            justify-content: flex-end;
            gap: 15px;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #edf2f7;
        }

        .btn-save { 
            background: var(--primary-gradient); 
            color: white; 
            padding: 12px 28px;
            border-radius: 12px;
            font-size: 15px;
        }
        .btn-save:hover { box-shadow: 0 10px 20px rgba(183, 148, 244, 0.3); transform: translateY(-2px); }
        
        .btn-cancel { 
            background: #f1f5f9; 
            color: #4a5568; 
            padding: 12px 28px;
            border-radius: 12px;
            font-size: 15px;
        }
        
        .month-inputs {
            display: grid;
            gap: 20px;
        }
        
        .month-input-card {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 20px;
        }
        
        .month-input-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            font-weight: 800;
            font-size: 16px;
        }
        
        .rate-input-group {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .rate-input-group input {
            width: 80px;
            padding: 8px 12px;
        }

        @media (max-width: 768px) {
            .evaluation-grid {
                grid-template-columns: 1fr;
            }
            header {
                flex-direction: column;
                gap: 20px;
            }
        }
    </style>
</head>
<body>

    <header>
        <h1>ANTIGRAVITY ISP</h1>
        <div class="header-actions">
            <div class="tabs" id="userTabs">
                <!-- Tabs injected by JS -->
            </div>
            <button class="btn-add-goal" onclick="openModal()">
                <span>＋</span> 新增 ISP 目標
            </button>
        </div>
    </header>

    <div class="container">
        <div class="cards-grid" id="cardsContainer">
            <!-- Cards injected by JS -->
        </div>

        <div class="evaluation-section">
            <h2 style="margin-bottom: 25px; font-size: 24px; font-weight: 800; color: #1a202c;">期中/期末評估與統整</h2>
            <div class="evaluation-grid">
                <div>
                    <label class="section-title" style="display: block; margin-top: 0; margin-bottom: 12px;">期中修改</label>
                    <textarea id="midTermText" placeholder="請輸入期中修改內容..." oninput="saveEvaluation()"></textarea>
                </div>
                <div>
                    <label class="section-title" style="display: block; margin-top: 0; margin-bottom: 12px;">期末總結</label>
                    <textarea id="endTermText" placeholder="請輸入期末總結內容..." oninput="saveEvaluation()"></textarea>
                </div>
            </div>
        </div>
    </div>

    <!-- Edit/Add Modal -->
    <div class="modal-overlay" id="editModalOverlay">
        <div class="modal">
            <div class="modal-header">
                <h2 class="modal-title" id="modalTitle">編輯 ISP 目標</h2>
                <button class="btn-close-icon" onclick="closeModal()">✕</button>
            </div>
            
            <div class="form-group">
                <label>支持領域</label>
                <input type="text" id="editDomain" placeholder="例如：生活自理、社會參與">
            </div>
            <div class="form-group">
                <label>支持目標</label>
                <input type="text" id="editTarget" placeholder="具體的目標名稱">
            </div>
            <div class="form-group">
                <label>支持策略</label>
                <textarea id="editStrategy" rows="4" placeholder="達到目標的方法與策略"></textarea>
            </div>
            <div class="form-group">
                <label>通過標準</label>
                <textarea id="editStandard" rows="3" placeholder="評估達標的具體標準"></textarea>
            </div>
            <div class="form-group">
                <label>目前狀態</label>
                <select id="editStatus">
                    <option value="未達標">未達標</option>
                    <option value="達標">達標</option>
                    <option value="未紀錄">未紀錄</option>
                </select>
            </div>
            
            <h3 style="margin: 35px 0 20px; font-size: 18px; font-weight: 800; border-bottom: 2px solid #edf2f7; padding-bottom: 10px;">每月執行紀錄</h3>
            <div class="month-inputs" id="monthInputsContainer">
                <!-- Month inputs injected by JS -->
            </div>

            <div class="modal-actions">
                <button class="btn btn-cancel" onclick="closeModal()">取消</button>
                <button class="btn btn-save" onclick="saveChanges()">儲存變更</button>
            </div>
        </div>
    </div>

    <script>
        // Firebase Configuration
        // 請將以下內容替換為您的 Firebase 專案設定
        const firebaseConfig = {
            apiKey: "YOUR_API_KEY",
            authDomain: "YOUR_PROJECT_ID.firebaseapp.com",
            databaseURL: "https://YOUR_PROJECT_ID-default-rtdb.firebaseio.com",
            projectId: "YOUR_PROJECT_ID",
            storageBucket: "YOUR_PROJECT_ID.appspot.com",
            messagingSenderId: "YOUR_SENDER_ID",
            appId: "YOUR_APP_ID"
        };
        
        // Initialize Firebase
        firebase.initializeApp(firebaseConfig);
        const db = firebase.database();

        // Generated from JSON
        const importedData = """ + json_str + """;

        let currentData = {};
        let currentUser = "";
        let editingGoalId = null; // null means adding new goal

        function init() {
            const dbRef = db.ref('ispDashboardDataV2');
            dbRef.on('value', (snapshot) => {
                const data = snapshot.val();
                
                if (data) {
                    currentData = data;
                } else {
                    currentData = importedData;
                    saveData(); // Save default data to Firebase
                }
                
                // Set initial user
                const users = Object.keys(currentData);
                if(users.length > 0 && !currentUser) {
                    currentUser = users[0];
                }
                
                renderTabs();
                renderDashboard();
            });
        }

        function saveData() {
            db.ref('ispDashboardDataV2').set(currentData);
        }

        function renderTabs() {
            const tabsContainer = document.getElementById('userTabs');
            tabsContainer.innerHTML = '';
            
            const users = Object.keys(currentData);
            users.forEach(user => {
                const btn = document.createElement('button');
                btn.className = `tab-btn ${user === currentUser ? 'active' : ''}`;
                btn.textContent = user;
                btn.onclick = () => {
                    currentUser = user;
                    renderTabs();
                    renderDashboard();
                };
                tabsContainer.appendChild(btn);
            });
            
            // Allow adding new user dynamically if needed, but not required yet
        }

        function renderDashboard() {
            const container = document.getElementById('cardsContainer');
            container.innerHTML = '';
            
            if (!currentData[currentUser]) return;
            const userData = currentData[currentUser];
            
            userData.goals.forEach(goal => {
                let statusClass = 'status-gray';
                if (goal.status === '未達標') statusClass = 'status-red';
                if (goal.status === '達標') statusClass = 'status-green';
                
                let totalRate = 0;
                let recordedMonths = 0;
                goal.records.forEach(r => {
                    if (r.rate > 0 || r.desc !== "" || r.strategy !== "") {
                        totalRate += parseInt(r.rate) || 0;
                        recordedMonths++;
                    }
                });
                const avgRate = recordedMonths > 0 ? Math.round(totalRate / recordedMonths) : 0;

                const strategyFormatted = goal.strategy ? goal.strategy.replace(/\\n/g, '<br>') : '無紀錄';
                const standardFormatted = goal.standard ? goal.standard.replace(/\\n/g, '<br>') : '無紀錄';

                const cardHTML = `
                    <div class="card" data-id="${goal.id}">
                        <div class="drag-handle" title="拖曳排序">⋮⋮</div>
                        <div class="status-badge ${statusClass}">${goal.status}</div>
                        <div class="card-header">
                            <span class="domain-tag">${goal.domain}</span>
                            <div class="goal-title">${goal.target || '未命名目標'}</div>
                        </div>
                        
                        <div class="section-title">支持策略</div>
                        <div class="content-text" style="margin-bottom: 15px;">${strategyFormatted}</div>
                        
                        <div class="section-title">通過標準</div>
                        <div class="content-text">${standardFormatted}</div>

                        <div class="progress-section">
                            <div class="progress-text">
                                <span>當前平均達成率</span>
                                <span>${avgRate}%</span>
                            </div>
                            <div class="progress-bar-bg">
                                <div class="progress-bar-fill" style="width: ${avgRate}%"></div>
                            </div>
                        </div>

                        <div class="actions">
                            <button class="btn btn-records" onclick="toggleRecords('${goal.id}')">每月紀錄</button>
                            <button class="btn btn-edit" onclick="openModal('${goal.id}')">編輯</button>
                            <button class="btn btn-delete" onclick="deleteGoal('${goal.id}')" title="刪除目標">🗑️</button>
                        </div>

                        <div class="records-area" id="records-${goal.id}">
                            ${goal.records.map(r => `
                                <div class="month-record">
                                    <div class="month-title">
                                        <span>第 ${r.month} 月</span>
                                        <span>達成率: ${r.rate}%</span>
                                    </div>
                                    
                                    <div class="month-desc-label">執行狀況</div>
                                    <div class="month-desc">${r.desc ? r.desc.replace(/\\n/g, '<br>') : '<span style="color:#a0aec0;font-style:italic">尚未記錄</span>'}</div>
                                    
                                    <div class="month-desc-label">本月執行策略說明</div>
                                    <div class="month-desc">${r.strategy ? r.strategy.replace(/\\n/g, '<br>') : '<span style="color:#a0aec0;font-style:italic">尚未記錄</span>'}</div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `;
                container.innerHTML += cardHTML;
            });

            document.getElementById('midTermText').value = userData.midTerm || '';
            document.getElementById('endTermText').value = userData.endTerm || '';

            if (window.sortableInstance) {
                window.sortableInstance.destroy();
            }
            window.sortableInstance = new Sortable(container, {
                animation: 150,
                handle: '.drag-handle',
                ghostClass: 'sortable-ghost',
                onEnd: function (evt) {
                    if (evt.newIndex !== evt.oldIndex) {
                        const movedGoal = currentData[currentUser].goals.splice(evt.oldIndex, 1)[0];
                        currentData[currentUser].goals.splice(evt.newIndex, 0, movedGoal);
                        saveData();
                    }
                }
            });
        }

        function deleteGoal(goalId) {
            if (confirm('確定要刪除此目標嗎？')) {
                currentData[currentUser].goals = currentData[currentUser].goals.filter(g => g.id !== goalId);
                saveData();
                renderDashboard();
            }
        }

        function toggleRecords(goalId) {
            const el = document.getElementById(`records-${goalId}`);
            if(el.classList.contains('active')) {
                el.classList.remove('active');
            } else {
                // close others
                document.querySelectorAll('.records-area').forEach(e => e.classList.remove('active'));
                el.classList.add('active');
            }
        }

        function openModal(goalId = null) {
            editingGoalId = goalId;
            const modalTitle = document.getElementById('modalTitle');
            
            const monthsContainer = document.getElementById('monthInputsContainer');
            monthsContainer.innerHTML = '';
            
            if (goalId) {
                modalTitle.textContent = "編輯 ISP 目標";
                const goal = currentData[currentUser].goals.find(g => g.id === goalId);
                
                document.getElementById('editTarget').value = goal.target;
                document.getElementById('editDomain').value = goal.domain;
                document.getElementById('editStrategy').value = goal.strategy;
                document.getElementById('editStandard').value = goal.standard;
                document.getElementById('editStatus').value = goal.status;

                goal.records.forEach(r => {
                    monthsContainer.innerHTML += createMonthInputHTML(r.month, r.desc, r.strategy, r.rate);
                });
            } else {
                modalTitle.textContent = "新增 ISP 目標";
                document.getElementById('editTarget').value = "";
                document.getElementById('editDomain').value = "";
                document.getElementById('editStrategy').value = "";
                document.getElementById('editStandard').value = "";
                document.getElementById('editStatus').value = "未紀錄";
                
                for(let i=1; i<=12; i++) {
                    monthsContainer.innerHTML += createMonthInputHTML(i, "", "", 0);
                }
            }

            document.getElementById('editModalOverlay').style.display = 'flex';
        }
        
        function createMonthInputHTML(month, desc, strategy, rate) {
            return `
                <div class="month-input-card">
                    <div class="month-input-header">
                        <span>第 ${month} 月</span>
                        <div class="rate-input-group">
                            <label style="margin:0; font-size:13px; font-weight:600;">達成率%</label>
                            <input type="number" id="rate-${month}" value="${rate}" min="0" max="100">
                        </div>
                    </div>
                    <div class="form-group" style="margin-bottom: 12px;">
                        <textarea id="desc-${month}" rows="2" placeholder="請輸入執行狀況...">${desc || ''}</textarea>
                    </div>
                    <div class="form-group" style="margin-bottom: 0;">
                        <textarea id="strategy-${month}" rows="2" placeholder="請輸入本月執行策略說明...">${strategy || ''}</textarea>
                    </div>
                </div>
            `;
        }

        function closeModal() {
            document.getElementById('editModalOverlay').style.display = 'none';
            editingGoalId = null;
        }

        function saveChanges() {
            let goal;
            
            if (editingGoalId) {
                // Edit existing
                goal = currentData[currentUser].goals.find(g => g.id === editingGoalId);
            } else {
                // Add new
                goal = {
                    id: 'g_' + Math.random().toString(36).substr(2, 9),
                    records: Array.from({length: 12}, (_, i) => ({ month: i + 1, desc: "", strategy: "", rate: 0 }))
                };
                currentData[currentUser].goals.unshift(goal); // Add to top
            }
            
            goal.target = document.getElementById('editTarget').value;
            goal.domain = document.getElementById('editDomain').value;
            goal.strategy = document.getElementById('editStrategy').value;
            goal.standard = document.getElementById('editStandard').value;
            goal.status = document.getElementById('editStatus').value;

            for(let i = 1; i <= 12; i++) {
                goal.records[i-1].desc = document.getElementById(`desc-${i}`).value;
                goal.records[i-1].strategy = document.getElementById(`strategy-${i}`).value;
                goal.records[i-1].rate = parseInt(document.getElementById(`rate-${i}`).value) || 0;
            }

            saveData();
            renderDashboard();
            closeModal();
        }

        function saveEvaluation() {
            if(!currentData[currentUser]) return;
            currentData[currentUser].midTerm = document.getElementById('midTermText').value;
            currentData[currentUser].endTerm = document.getElementById('endTermText').value;
            saveData();
        }

        document.getElementById('editModalOverlay').addEventListener('click', function(e) {
            if (e.target === this) {
                closeModal();
            }
        });

        window.onload = init;
    </script>
</body>
</html>"""

    with open('antigravity_isp_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

if __name__ == '__main__':
    generate()
