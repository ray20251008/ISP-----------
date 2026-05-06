import json
import re
import uuid

def main():
    # Load parsed_isp.json
    with open('parsed_isp.json', 'r', encoding='utf-8') as f:
        parsed_data = json.load(f)
        
    # Load data.json
    with open('data.json', 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
        
    raw_map = {item['file']: item['content'] for item in raw_data}
    
    app_data = []
    
    for item in parsed_data:
        filename = item['file']
        content = raw_map.get(filename, '')
        
        # Extract fields
        diag_match = re.search(r'執行狀況說明:\s*(.*?)(?=\n|$)', content)
        summary_match = re.search(r'115年執行成效總結:\s*(.*?)(?=\n|$)', content)
        domain_match = re.search(r'支持領域:\s*(.*?)(?=\n|$)', content)
        
        diagnostic = ""
        if summary_match:
            diagnostic += summary_match.group(1).strip() + "\n"
        if diag_match:
            diagnostic += "執行狀況說明: " + diag_match.group(1).strip()
            
        if not diagnostic:
            diagnostic = "無"
            
        # Determine initial status
        initial_status = "無紀錄"
        if "✅" in item['status']:
            initial_status = "已達成"
        elif "❌" in item['status']:
            initial_status = "未達成"
            
        # Format strategy
        strategy = item['strategy']
        if strategy:
            strategy = strategy.replace('<br>', '\n').replace('<br/>', '\n')
            
        app_data.append({
            "id": str(uuid.uuid4()),
            "user": item['user'],
            "goal": item['goal'],
            "domain": domain_match.group(1).strip() if domain_match else "未分類",
            "status": initial_status,
            "diagnostic": diagnostic,
            "strategy": strategy,
            "criteria": item['criteria'],
            "months": {str(i): "" for i in range(1, 13)},
            "midTermSummary": "",
            "endTermSummary": "",
            "futureGoal": ""
        })

    html_template = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ANTIGRAVITY ISP 粉藍主題儀表板</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        body { 
            font-family: 'Nunito', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background-color: #FDFEFC; 
            color: #4A4A4A;
        }
        
        /* Macaron Color Palette */
        .theme-pink { color: #f472b6; }
        .theme-blue { color: #60a5fa; }
        .bg-macaron-pink { background-color: #fce7f3; }
        .bg-macaron-blue { background-color: #dbeafe; }
        .bg-macaron-yellow { background-color: #fef9c3; }
        
        .shadow-soft {
            box-shadow: 0 10px 40px -10px rgba(0,0,0,0.06);
        }
        
        /* Editable styling */
        .editable-input {
            width: 100%;
            background: transparent;
            border: 1px solid transparent;
            border-radius: 0.5rem;
            transition: all 0.2s;
        }
        .editable-input:hover {
            background: rgba(255, 255, 255, 0.5);
            border-color: rgba(0,0,0,0.05);
        }
        .editable-input:focus {
            background: white;
            border-color: #93c5fd;
            outline: none;
            box-shadow: 0 0 0 3px rgba(147, 197, 253, 0.3);
        }

        /* Print Styles */
        @media print {
            body { background-color: white !important; }
            .no-print { display: none !important; }
            .print-card { 
                page-break-after: always;
                page-break-inside: avoid;
                box-shadow: none !important;
                border: 2px solid #e5e7eb;
                margin-bottom: 2rem !important;
                border-radius: 1.5rem !important;
            }
            .print-card:last-child {
                page-break-after: auto;
            }
            .editable-input { border: none !important; resize: none !important; }
        }
        
        /* Hide scrollbar */
        textarea::-webkit-scrollbar { width: 6px; }
        textarea::-webkit-scrollbar-track { background: transparent; }
        textarea::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
    </style>
</head>
<body class="min-h-screen pb-16">
    <div id="app">
        <!-- Top Navigation -->
        <nav class="bg-white/80 backdrop-blur-md shadow-sm sticky top-0 z-50 no-print border-b border-pink-100">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="flex justify-between h-16 items-center">
                    <div class="flex-shrink-0 flex items-center gap-2">
                        <div class="w-8 h-8 rounded-full bg-gradient-to-tr from-pink-400 to-blue-400"></div>
                        <span class="font-extrabold text-xl tracking-tight text-gray-800">ANTIGRAVITY</span>
                    </div>
                    <div class="flex space-x-3">
                        <button @click="exportData" class="flex items-center px-4 py-2 rounded-2xl text-sm font-bold text-blue-600 bg-blue-50 hover:bg-blue-100 transition-colors">
                            💾 備份資料
                        </button>
                        <label class="flex items-center px-4 py-2 rounded-2xl text-sm font-bold text-pink-600 bg-pink-50 hover:bg-pink-100 transition-colors cursor-pointer">
                            📤 還原資料
                            <input type="file" @change="importData" class="hidden" accept=".json">
                        </label>
                        <button @click="printReport" class="flex items-center px-4 py-2 rounded-2xl text-sm font-bold text-purple-600 bg-purple-50 hover:bg-purple-100 transition-colors">
                            🖨️ 列印報表
                        </button>
                    </div>
                </div>
            </div>
        </nav>

        <main class="max-w-5xl mx-auto px-4 pt-10">
            
            <!-- User Tabs -->
            <div class="flex justify-center mb-10 no-print">
                <div class="bg-white p-2 rounded-3xl shadow-sm border border-pink-100 inline-flex space-x-2 relative">
                    <button 
                        v-for="user in users" :key="user"
                        @click="activeUser = user"
                        :class="['px-8 py-3 rounded-2xl font-bold transition-all duration-300 z-10', 
                                activeUser === user ? 'bg-gradient-to-r from-pink-400 to-blue-400 text-white shadow-md transform scale-105' : 'text-gray-500 hover:bg-gray-50']"
                    >
                        {{ user }}
                    </button>
                </div>
            </div>

            <!-- Cards Container -->
            <div class="space-y-12">
                <div v-for="(item, idx) in filteredData" :key="item.id" class="print-card bg-white rounded-[2rem] shadow-soft p-8 relative overflow-hidden transition-all border-2"
                     :class="{
                         'border-gray-200': item.status === '無紀錄',
                         'border-emerald-300 ring-4 ring-emerald-50': item.status === '已達成',
                         'border-rose-300 ring-4 ring-rose-50': item.status === '未達成'
                     }">
                     
                    <!-- Background Decoration -->
                    <div class="absolute -top-10 -right-10 w-48 h-48 rounded-full mix-blend-multiply filter blur-2xl opacity-40 -z-10"
                         :class="{
                             'bg-gray-200': item.status === '無紀錄',
                             'bg-emerald-200': item.status === '已達成',
                             'bg-rose-200': item.status === '未達成'
                         }"></div>
                    <div class="absolute -bottom-10 -left-10 w-48 h-48 bg-blue-200 rounded-full mix-blend-multiply filter blur-2xl opacity-40 -z-10"></div>

                    <!-- Header -->
                    <div class="flex justify-between items-start mb-6 gap-4">
                        <div class="flex-1">
                            <div class="flex items-center gap-3 mb-2">
                                <span class="px-3 py-1 bg-pink-100 text-pink-600 rounded-full text-xs font-bold uppercase tracking-wider">
                                    {{ item.domain }}
                                </span>
                                <!-- Name is editable inline -->
                                <input v-model="item.user" @input="saveData" class="editable-input text-sm font-bold text-gray-500 w-32 px-2 py-1 -ml-2" />
                            </div>
                            
                            <!-- Goal Name Editable -->
                            <textarea v-model="item.goal" @input="saveData" class="editable-input text-2xl font-extrabold text-gray-800 leading-tight resize-y px-2 py-1 -ml-2" rows="2"></textarea>
                        </div>
                        
                        <!-- Status Toggle Action (Cycle) -->
                        <div class="flex flex-col items-end gap-2">
                            <button @click="cycleStatus(item)" class="no-print px-5 py-3 rounded-2xl text-sm font-bold transition-all shadow-sm border"
                                :class="{
                                    'bg-rose-500 text-white border-rose-600 shadow-rose-200': item.status === '未達成',
                                    'bg-emerald-500 text-white border-emerald-600 shadow-emerald-200': item.status === '已達成',
                                    'bg-gray-100 text-gray-600 border-gray-300': item.status === '無紀錄'
                                }">
                                {{ item.status === '已達成' ? '✅ 已達成' : item.status === '未達成' ? '❌ 未達成' : '⚪ 無紀錄' }}
                            </button>
                            <span class="text-xs text-gray-400 font-medium no-print">點擊切換狀態</span>
                            
                            <!-- Print Status -->
                            <div class="hidden print:block text-lg font-bold"
                                 :class="{ 'text-gray-500': item.status === '無紀錄', 'text-emerald-600': item.status === '已達成', 'text-rose-600': item.status === '未達成' }">
                                狀態：{{ item.status }}
                            </div>
                        </div>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                        <!-- Diagnostic & Strategy & Criteria -->
                        <div class="space-y-4">
                            
                            <div class="bg-blue-50/70 p-5 rounded-3xl border border-blue-100">
                                <h3 class="text-xs font-bold text-blue-500 uppercase tracking-wider mb-2 flex items-center gap-1">
                                    <span>🎯</span> 核心支持策略
                                </h3>
                                <textarea v-model="item.strategy" @input="saveData" class="editable-input text-sm text-gray-700 leading-relaxed resize-y" rows="5"></textarea>
                            </div>

                            <div class="bg-pink-50/70 p-5 rounded-3xl border border-pink-100">
                                <h3 class="text-xs font-bold text-pink-500 uppercase tracking-wider mb-2 flex items-center gap-1">
                                    <span>⭐</span> 通過標準
                                </h3>
                                <textarea v-model="item.criteria" @input="saveData" class="editable-input text-sm text-gray-700 font-medium resize-y" rows="2"></textarea>
                            </div>
                            
                            <!-- Static Diagnostic for reference -->
                            <div class="bg-gray-50/70 p-5 rounded-3xl border border-gray-100">
                                <h3 class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2 flex items-center gap-1">
                                    <span>🔍</span> 原檔執行狀況診斷 (參考用)
                                </h3>
                                <p class="text-sm text-gray-600 whitespace-pre-line">{{ item.diagnostic }}</p>
                            </div>
                        </div>

                        <!-- Monthly Records -->
                        <div class="bg-indigo-50/40 p-6 rounded-3xl border border-indigo-100 flex flex-col">
                            <h3 class="text-xs font-bold text-indigo-500 uppercase tracking-wider mb-4 flex items-center gap-1">
                                <span>📅</span> 每月執行狀況紀錄
                            </h3>
                            
                            <div class="flex flex-wrap gap-2 mb-5 no-print">
                                <button v-for="m in 12" :key="m"
                                        @click="activeMonth[item.id] = String(m)"
                                        :class="['w-10 h-10 rounded-2xl text-sm font-bold transition-all flex items-center justify-center', 
                                                (activeMonth[item.id] || '1') === String(m) ? 'bg-indigo-500 text-white shadow-md shadow-indigo-200 transform scale-110' : 
                                                item.months[String(m)] ? 'bg-indigo-100 text-indigo-700 border border-indigo-200' : 'bg-white text-gray-400 border border-gray-200 hover:bg-gray-50']">
                                    {{ m }}
                                </button>
                            </div>
                            
                            <!-- Editor -->
                            <div class="flex-1 flex flex-col no-print bg-white rounded-2xl p-4 border border-indigo-100 shadow-inner">
                                <div class="text-sm font-bold text-indigo-400 mb-2">{{ activeMonth[item.id] || '1' }}月紀錄：</div>
                                <textarea v-model="item.months[activeMonth[item.id] || '1']" 
                                          @input="saveData"
                                          class="flex-1 w-full p-2 rounded-xl focus:outline-none text-sm text-gray-700 resize-none bg-transparent"
                                          placeholder="請直接點擊輸入本月執行紀錄..."></textarea>
                            </div>

                            <!-- Print version of months -->
                            <div class="hidden print:block w-full mt-4">
                                <div v-for="m in 12" :key="'p'+m" v-show="item.months[String(m)]" class="mb-3 border-b border-gray-100 pb-2">
                                    <strong class="text-indigo-600">{{ m }}月紀錄：</strong>
                                    <p class="text-sm mt-1 text-gray-700">{{ item.months[String(m)] }}</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Summaries & Future -->
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 border-t-2 border-dashed border-pink-100 pt-6">
                        <div class="bg-white p-4 rounded-3xl border border-gray-100 shadow-sm">
                            <h3 class="text-xs font-bold text-purple-400 uppercase tracking-wider mb-2">期中總結</h3>
                            <textarea v-model="item.midTermSummary" @input="saveData" class="editable-input p-2 text-sm text-gray-700 resize-y" rows="3" placeholder="點擊填寫期中檢討與修正方向..."></textarea>
                        </div>
                        <div class="bg-white p-4 rounded-3xl border border-gray-100 shadow-sm">
                            <h3 class="text-xs font-bold text-purple-400 uppercase tracking-wider mb-2">期末總結</h3>
                            <textarea v-model="item.endTermSummary" @input="saveData" class="editable-input p-2 text-sm text-gray-700 resize-y" rows="3" placeholder="點擊填寫期末最終成果評估..."></textarea>
                        </div>
                        <div class="bg-pink-50 p-4 rounded-3xl border border-pink-200 shadow-sm">
                            <h3 class="text-xs font-bold text-pink-500 uppercase tracking-wider mb-2">116年度預計設立目標</h3>
                            <textarea v-model="item.futureGoal" @input="saveData" class="editable-input p-2 text-sm text-gray-800 resize-y" rows="3" placeholder="點擊設定明年新目標..."></textarea>
                        </div>
                    </div>

                </div>
            </div>
            
            <div v-if="filteredData.length === 0" class="text-center py-20 text-gray-400">
                <p class="text-lg font-bold">目前沒有資料</p>
            </div>

        </main>
    </div>

    <script>
        const INITIAL_DATA = DATA_PLACEHOLDER;

        const { createApp, ref, computed, onMounted, watch } = Vue;

        createApp({
            setup() {
                const ispData = ref([]);
                const activeUser = ref('');
                const activeMonth = ref({}); 
                
                onMounted(() => {
                    loadData();
                });

                const loadData = () => {
                    const saved = localStorage.getItem('antigravity_isp_data_v2'); // New key to avoid conflict if data structure changed slightly
                    if (saved) {
                        try {
                            ispData.value = JSON.parse(saved);
                        } catch (e) {
                            console.error('Failed to parse localStorage data', e);
                            ispData.value = JSON.parse(JSON.stringify(INITIAL_DATA));
                        }
                    } else {
                        ispData.value = JSON.parse(JSON.stringify(INITIAL_DATA));
                    }
                    
                    if (ispData.value.length > 0) {
                        activeUser.value = ispData.value[0].user;
                    }
                };

                const saveData = () => {
                    localStorage.setItem('antigravity_isp_data_v2', JSON.stringify(ispData.value));
                };

                const users = computed(() => {
                    return [...new Set(ispData.value.map(d => d.user))];
                });

                const filteredData = computed(() => {
                    return ispData.value.filter(d => d.user === activeUser.value);
                });

                // Cycle Status Update
                const cycleStatus = (item) => {
                    const order = ["無紀錄", "未達成", "已達成"];
                    const currIdx = order.indexOf(item.status);
                    const nextIdx = (currIdx + 1) % order.length;
                    item.status = order[nextIdx];
                    saveData();
                };

                // Export / Import
                const exportData = () => {
                    const dataStr = JSON.stringify(ispData.value, null, 2);
                    const blob = new Blob([dataStr], { type: "application/json" });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `isp_backup_${new Date().toISOString().slice(0,10)}.json`;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                };

                const importData = (event) => {
                    const file = event.target.files[0];
                    if (!file) return;
                    
                    const reader = new FileReader();
                    reader.onload = (e) => {
                        try {
                            const imported = JSON.parse(e.target.result);
                            if (Array.isArray(imported)) {
                                ispData.value = imported;
                                saveData();
                                alert("資料還原成功！");
                                if (users.value.length > 0 && !users.value.includes(activeUser.value)) {
                                    activeUser.value = users.value[0];
                                }
                            } else {
                                alert("檔案格式錯誤。");
                            }
                        } catch (err) {
                            alert("解析檔案失敗。");
                        }
                    };
                    reader.readAsText(file);
                    event.target.value = '';
                };

                const printReport = () => {
                    window.print();
                };

                return {
                    ispData,
                    activeUser,
                    users,
                    filteredData,
                    activeMonth,
                    cycleStatus,
                    saveData,
                    exportData,
                    importData,
                    printReport
                };
            }
        }).mount('#app');
    </script>
</body>
</html>"""
    
    html_output = html_template.replace('DATA_PLACEHOLDER', json.dumps(app_data, ensure_ascii=False))
    
    with open('isp_advanced_app.html', 'w', encoding='utf-8') as f:
        f.write(html_output)
        
if __name__ == "__main__":
    main()
