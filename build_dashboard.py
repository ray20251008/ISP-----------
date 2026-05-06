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
        # We will look for "115年執行成效總結: ..." or "執行狀況說明: ..."
        # Note that "執行狀況說明:" is often just a link to the user.
        # But if the user asked to retain "執行狀況說明" as diagnostic, let's grab it.
        diag_match = re.search(r'執行狀況說明:\s*(.*?)(?=\n|$)', content)
        summary_match = re.search(r'115年執行成效總結:\s*(.*?)(?=\n|$)', content)
        
        diagnostic = ""
        if summary_match:
            diagnostic += summary_match.group(1).strip() + "\n"
        if diag_match:
            # Often it's just "曾宇彤 (url)" we might want to clean it up or keep it verbatim as user requested.
            diagnostic += "執行狀況說明: " + diag_match.group(1).strip()
            
        if not diagnostic:
            diagnostic = "無"
            
        item['diagnostic'] = diagnostic

    # Generate HTML
    html_template = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ISP 支持目標儀表板 (ANTIGRAVITY)</title>
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- React & ReactDOM -->
    <script src="https://unpkg.com/react@18/umd/react.production.min.js" crossorigin></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js" crossorigin></script>
    <!-- Babel -->
    <script src="https://unpkg.com/babel-standalone@6/babel.min.js"></script>
    <!-- Lucide Icons -->
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        body { font-family: 'Inter', system-ui, -apple-system, sans-serif; background-color: #f3f4f6; }
        .glass-panel { background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.2); }
    </style>
</head>
<body>
    <div id="root"></div>
    <script type="text/babel">
        const { useState, useMemo } = React;

        const rawData = DATA_PLACEHOLDER;

        const App = () => {
            const [activeUser, setActiveUser] = useState("曾宇彤");
            
            const users = [...new Set(rawData.map(d => d.user))];
            
            const filteredData = useMemo(() => {
                return rawData.filter(d => d.user === activeUser);
            }, [activeUser]);

            const stats = useMemo(() => {
                const total = filteredData.length;
                const achieved = filteredData.filter(d => d.status.includes('✅')).length;
                const notAchieved = total - achieved;
                const percentage = total > 0 ? Math.round((achieved / total) * 100) : 0;
                return { total, achieved, notAchieved, percentage };
            }, [filteredData]);

            return (
                <div className="min-h-screen p-8 text-slate-800">
                    <div className="max-w-7xl mx-auto space-y-8">
                        
                        {/* Header */}
                        <header className="flex items-center justify-between">
                            <div>
                                <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600 tracking-tight">
                                    ANTIGRAVITY ISP Dashboard
                                </h1>
                                <p className="text-slate-500 mt-2 font-medium">個人化支持計畫任務矩陣與診斷分析</p>
                            </div>
                        </header>

                        {/* Navigation / Tabs */}
                        <div className="flex space-x-2 bg-slate-200/50 p-1 rounded-xl w-max">
                            {users.map(u => (
                                <button
                                    key={u}
                                    onClick={() => setActiveUser(u)}
                                    className={`px-6 py-2.5 rounded-lg font-bold transition-all duration-300 ${activeUser === u ? 'bg-white text-indigo-600 shadow-sm scale-105' : 'text-slate-500 hover:text-slate-700 hover:bg-slate-200'}`}
                                >
                                    {u}
                                </button>
                            ))}
                        </div>

                        {/* KPI Cards */}
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                            <div className="glass-panel p-6 rounded-2xl shadow-sm border border-slate-100 flex flex-col justify-center relative overflow-hidden group">
                                <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/></svg>
                                </div>
                                <h3 className="text-slate-500 text-sm font-bold uppercase tracking-wider">總目標數</h3>
                                <p className="text-4xl font-black text-slate-800 mt-2">{stats.total}</p>
                            </div>
                            
                            <div className="glass-panel p-6 rounded-2xl shadow-sm border border-slate-100 flex flex-col justify-center relative overflow-hidden group">
                                <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity text-emerald-500">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                                </div>
                                <h3 className="text-emerald-600 text-sm font-bold uppercase tracking-wider">已達標</h3>
                                <p className="text-4xl font-black text-emerald-500 mt-2">{stats.achieved}</p>
                            </div>

                            <div className="glass-panel p-6 rounded-2xl shadow-sm border border-slate-100 flex flex-col justify-center relative overflow-hidden group">
                                <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity text-rose-500">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                                </div>
                                <h3 className="text-rose-600 text-sm font-bold uppercase tracking-wider">未達標</h3>
                                <p className="text-4xl font-black text-rose-500 mt-2">{stats.notAchieved}</p>
                            </div>

                            <div className="glass-panel p-6 rounded-2xl shadow-sm border border-slate-100 flex flex-col justify-center relative overflow-hidden group bg-gradient-to-br from-indigo-500 to-purple-600 text-white">
                                <h3 className="text-indigo-100 text-sm font-bold uppercase tracking-wider">達成率</h3>
                                <div className="flex items-baseline space-x-1 mt-2">
                                    <p className="text-5xl font-black">{stats.percentage}</p>
                                    <span className="text-xl font-bold opacity-80">%</span>
                                </div>
                                <div className="w-full bg-black/20 h-1.5 rounded-full mt-4 overflow-hidden">
                                    <div className="bg-white h-full rounded-full transition-all duration-1000" style={{ width: `${stats.percentage}%` }}></div>
                                </div>
                            </div>
                        </div>

                        {/* Interactive Data Table */}
                        <div className="glass-panel rounded-2xl shadow-sm overflow-hidden border border-slate-200">
                            <div className="overflow-x-auto">
                                <table className="w-full text-left border-collapse">
                                    <thead>
                                        <tr className="bg-slate-50 border-b border-slate-200">
                                            <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-wider w-1/4">目標編號與名稱</th>
                                            <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-wider w-24">狀態</th>
                                            <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-wider w-1/4">執行狀況診斷</th>
                                            <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-wider w-1/4">支持策略</th>
                                            <th className="p-4 text-xs font-bold text-slate-500 uppercase tracking-wider w-1/4">通過標準</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-slate-100">
                                        {filteredData.map((row, idx) => {
                                            const isAchieved = row.status.includes('✅');
                                            return (
                                                <tr key={idx} className="hover:bg-slate-50/50 transition-colors">
                                                    <td className="p-4 align-top">
                                                        <div className="font-semibold text-slate-800 leading-snug">{row.goal}</div>
                                                        <div className="mt-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-500 border border-slate-200">
                                                            {row.qol !== '-' ? row.qol : '未分類'}
                                                        </div>
                                                    </td>
                                                    <td className="p-4 align-top">
                                                        <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold ${
                                                            isAchieved 
                                                            ? 'bg-emerald-100 text-emerald-700 border border-emerald-200' 
                                                            : 'bg-rose-100 text-rose-700 border border-rose-200'
                                                        }`}>
                                                            {isAchieved ? '✅ 達標' : '❌ 未達標'}
                                                        </span>
                                                    </td>
                                                    <td className="p-4 align-top text-sm text-slate-600">
                                                        <div dangerouslySetInnerHTML={{ __html: row.diagnostic.replace(/\\n/g, '<br/>') }} className="prose prose-sm prose-slate max-w-none" />
                                                    </td>
                                                    <td className="p-4 align-top text-sm text-slate-600">
                                                        <div dangerouslySetInnerHTML={{ __html: row.strategy || '無具體策略' }} className="prose prose-sm prose-slate max-w-none leading-relaxed" />
                                                    </td>
                                                    <td className="p-4 align-top text-sm text-slate-600">
                                                        {row.criteria !== '-' ? row.criteria : '無'}
                                                    </td>
                                                </tr>
                                            );
                                        })}
                                    </tbody>
                                </table>
                            </div>
                        </div>

                    </div>
                </div>
            );
        };

        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<App />);
    </script>
</body>
</html>"""
    
    html_output = html_template.replace('DATA_PLACEHOLDER', json.dumps(parsed_data, ensure_ascii=False))
    
    with open('isp_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html_output)
        
if __name__ == "__main__":
    main()
