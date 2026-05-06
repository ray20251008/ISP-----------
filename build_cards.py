import json
import re

def main():
    # Load parsed_isp.json
    with open('parsed_isp.json', 'r', encoding='utf-8') as f:
        parsed_data = json.load(f)
        
    # Load data.json
    with open('data.json', 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
        
    raw_map = {item['file']: item['content'] for item in raw_data}
    
    for item in parsed_data:
        filename = item['file']
        content = raw_map.get(filename, '')
        
        # Extract "執行狀況說明" or "115年執行成效總結"
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
            
        item['diagnostic'] = diagnostic
        item['domain'] = domain_match.group(1).strip() if domain_match else "未分類"

    # Generate HTML with Vanilla JS
    html_template = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ANTIGRAVITY ISP 目標儀表板</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; background-color: #f8fafc; }
        .tab-btn.active { background-color: #4f46e5; color: white; transform: scale(1.05); box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.3); }
        .tab-btn { transition: all 0.3s ease; }
        .card-enter { animation: fade-in-up 0.4s ease-out forwards; }
        @keyframes fade-in-up {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body class="text-slate-800 antialiased min-h-screen pb-12">

    <div class="max-w-6xl mx-auto px-4 pt-12">
        <header class="mb-10 text-center">
            <h1 class="text-4xl md:text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600 tracking-tight mb-4">
                ANTIGRAVITY ISP Dashboard
            </h1>
            <p class="text-slate-500 font-medium text-lg">個人化支持計畫任務卡片與診斷分析</p>
        </header>

        <!-- Toggle Buttons -->
        <div class="flex justify-center mb-10">
            <div class="bg-white p-1.5 rounded-2xl shadow-sm border border-slate-200 inline-flex space-x-2">
                <button onclick="switchTab('曾宇彤')" id="tab-曾宇彤" class="tab-btn active px-8 py-3 rounded-xl font-bold text-slate-600 hover:bg-slate-50">曾宇彤</button>
                <button onclick="switchTab('林育萱')" id="tab-林育萱" class="tab-btn px-8 py-3 rounded-xl font-bold text-slate-600 hover:bg-slate-50">林育萱</button>
            </div>
        </div>

        <!-- Cards Container -->
        <div id="cards-container" class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Cards will be rendered here -->
        </div>
    </div>

    <script>
        const rawData = DATA_PLACEHOLDER;

        function renderCards(user) {
            const container = document.getElementById('cards-container');
            container.innerHTML = '';
            
            const filteredData = rawData.filter(d => d.user === user);
            
            filteredData.forEach((item, index) => {
                const isFailed = item.status.includes('❌');
                const isAchieved = item.status.includes('✅');
                
                // Border and badge styling based on status
                let borderClass = 'border-slate-200';
                let badgeClass = 'bg-slate-100 text-slate-600 border-slate-200';
                
                if (isFailed) {
                    borderClass = 'border-rose-400 shadow-[0_0_15px_rgba(244,63,94,0.15)] ring-1 ring-rose-400';
                    badgeClass = 'bg-rose-100 text-rose-700 border-rose-200';
                } else if (isAchieved) {
                    borderClass = 'border-emerald-200';
                    badgeClass = 'bg-emerald-100 text-emerald-700 border-emerald-200';
                }
                
                // Format texts
                const strategyHtml = item.strategy ? item.strategy.replace(/\\n/g, '<br/>') : '<span class="italic text-slate-400">無具體策略</span>';
                const diagHtml = item.diagnostic ? item.diagnostic.replace(/\\n/g, '<br/>') : '無';

                const cardHTML = `
                    <div class="bg-white rounded-2xl p-6 ${borderClass} card-enter relative overflow-hidden" style="animation-delay: ${index * 0.05}s">
                        ${isFailed ? '<div class="absolute top-0 right-0 w-16 h-16 bg-rose-50 rounded-bl-full -z-10"></div>' : ''}
                        
                        <div class="flex justify-between items-start mb-4 gap-4">
                            <h3 class="text-xl font-bold text-slate-800 leading-snug flex-1">${item.goal}</h3>
                            <span class="shrink-0 inline-flex items-center px-3 py-1 rounded-full text-sm font-bold border ${badgeClass}">
                                ${isAchieved ? '✅ 達標' : '❌ 未達標'}
                            </span>
                        </div>
                        
                        <div class="mb-5 inline-flex items-center px-2.5 py-1 rounded text-xs font-semibold bg-indigo-50 text-indigo-600 border border-indigo-100">
                            支持領域：${item.domain}
                        </div>
                        
                        <div class="space-y-4">
                            <div class="bg-slate-50 rounded-xl p-4 border border-slate-100">
                                <h4 class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2 flex items-center">
                                    <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"></path></svg>
                                    執行狀況診斷
                                </h4>
                                <p class="text-sm text-slate-700 leading-relaxed">${diagHtml}</p>
                            </div>

                            <div>
                                <h4 class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2 flex items-center">
                                    <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                                    核心支持策略
                                </h4>
                                <div class="text-sm text-slate-600 leading-relaxed prose prose-sm max-w-none">${strategyHtml}</div>
                            </div>
                            
                            <div class="pt-3 border-t border-slate-100">
                                <h4 class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-1 flex items-center">
                                    <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                                    通過標準
                                </h4>
                                <p class="text-sm text-slate-600 font-medium">${item.criteria !== '-' ? item.criteria : '無'}</p>
                            </div>
                        </div>
                    </div>
                `;
                container.insertAdjacentHTML('beforeend', cardHTML);
            });
        }

        function switchTab(user) {
            // Update buttons
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.remove('active');
                btn.classList.add('text-slate-600', 'hover:bg-slate-50');
            });
            const activeBtn = document.getElementById('tab-' + user);
            activeBtn.classList.add('active');
            activeBtn.classList.remove('text-slate-600', 'hover:bg-slate-50');
            
            // Render cards
            renderCards(user);
        }

        // Initialize
        document.addEventListener('DOMContentLoaded', () => {
            switchTab('曾宇彤');
        });
    </script>
</body>
</html>"""
    
    html_output = html_template.replace('DATA_PLACEHOLDER', json.dumps(parsed_data, ensure_ascii=False))
    
    with open('isp_cards.html', 'w', encoding='utf-8') as f:
        f.write(html_output)
        
if __name__ == "__main__":
    main()
