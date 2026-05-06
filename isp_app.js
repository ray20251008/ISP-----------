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

let currentData = {};
let currentUser = "";
let editingGoalId = null;

function init() {
    // 網頁載入時先從 Firebase 抓取最新資料
    const dbRef = db.ref('ispDashboardDataV2');
    dbRef.on('value', (snapshot) => {
        const data = snapshot.val();
        
        if (data) {
            currentData = data;
        } else {
            // 如果雲端為空，載入外部預設資料檔並寫入 Firebase
            if (typeof defaultData !== 'undefined') {
                currentData = defaultData;
                saveData();
            } else {
                currentData = {};
            }
        }
        
        const users = Object.keys(currentData);
        if(users.length > 0 && !currentUser) {
            currentUser = users[0];
        }
        
        renderTabs();
        renderDashboard();
    });
}

function saveData() {
    // 寫入 Firebase
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
            
            // 抓取最新的 8 個目標 (使用 slice 只取前 8 筆)
            const latestGoals = userData.goals.slice(0, 8);
            
            latestGoals.forEach(goal => {
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

        
    



    with open('antigravity_isp_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

if __name__ == '__main__':
    generate()

window.onload = init;
