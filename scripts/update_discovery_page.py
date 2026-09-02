with open(r'D:\ai-system-s\frontend\src\app\discovery\page.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

history_section = '''      </form>

      {/* Discovery Operations History & Truth Audit Log */}
      <div className=\"p-6 bg-white rounded-lg border border-slate-200 shadow-xs space-y-4\">
        <div className=\"flex items-center justify-between border-b border-slate-100 pb-3\">
          <div>
            <h2 className=\"text-sm font-bold text-slate-900\">
              Discovery Operations History & Ingestion Log
            </h2>
            <p className=\"text-xs text-slate-500 mt-0.5\">
              Historical discovery batches, rejected noise counts, and strictly qualified lead yields.
            </p>
          </div>
          <button
            onClick={fetchJobs}
            className=\"text-xs font-semibold text-blue-600 hover:text-blue-800 flex items-center gap-1\"
          >
            <RefreshCw className=\"w-3 h-3\" />
            <span>Refresh Jobs</span>
          </button>
        </div>

        <div className=\"overflow-x-auto\">
          <table className=\"w-full text-left border-collapse text-xs\">
            <thead>
              <tr className=\"border-b border-slate-200 bg-slate-50 text-slate-500 font-bold uppercase tracking-wider text-[10px]\">
                <th className=\"p-3\">Job #</th>
                <th className=\"p-3\">Campaign Target</th>
                <th className=\"p-3\">Discovered</th>
                <th className=\"p-3\">Websites (Found / Reachable / Verified)</th>
                <th className=\"p-3\">Audits (Done / Incomplete)</th>
                <th className=\"p-3\">Qualified</th>
                <th className=\"p-3\">Sales Ready</th>
                <th className=\"p-3\">Status</th>
                <th className=\"p-3\">Date</th>
              </tr>
            </thead>
            <tbody className=\"divide-y divide-slate-100\">
              {loading ? (
                <tr>
                  <td colSpan={9} className=\"p-8 text-center text-slate-400\">
                    Loading discovery operations...
                  </td>
                </tr>
              ) : jobs.length === 0 ? (
                <tr>
                  <td colSpan={9} className=\"p-8 text-center text-slate-400\">
                    No discovery operations recorded yet.
                  </td>
                </tr>
              ) : (
                jobs.map((j) => (
                  <tr key={j.id} className=\"hover:bg-slate-50/80 transition\">
                    <td className=\"p-3 font-mono font-bold text-slate-700\">#{j.id}</td>
                    <td className=\"p-3\">
                      <div className=\"font-bold text-slate-900\">{j.name}</div>
                      <div className=\"text-[11px] text-slate-400\">
                        {j.location} • {j.industry} • {j.sources_used}
                      </div>
                    </td>
                    <td className=\"p-3 font-mono font-bold text-slate-900\">{j.discovered_count}</td>
                    <td className=\"p-3\">
                      <span className=\"font-mono font-semibold text-slate-800\">{j.websites_found_count}</span>
                      <span className=\"text-slate-400 mx-1\">/</span>
                      <span className=\"font-mono font-semibold text-blue-600\">{j.websites_reachable_count ?? j.websites_crawled_count}</span>
                      <span className=\"text-slate-400 mx-1\">/</span>
                      <span className=\"font-mono font-semibold text-emerald-600\">{j.websites_verified_count ?? 0}</span>
                    </td>
                    <td className=\"p-3\">
                      <span className=\"font-mono font-semibold text-emerald-700\">{j.audits_completed_count}</span>
                      <span className=\"text-slate-400 mx-1\">/</span>
                      <span className=\"font-mono font-semibold text-amber-600\">{j.audits_incomplete_count ?? 0}</span>
                    </td>
                    <td className=\"p-3\">
                      <span className={px-2 py-0.5 rounded text-[10px] font-mono font-bold }>
                        {j.qualified_leads_count}
                      </span>
                    </td>
                    <td className=\"p-3\">
                      <span className={px-2 py-0.5 rounded text-[10px] font-mono font-bold }>
                        {j.sales_ready_count ?? 0}
                      </span>
                    </td>
                    <td className=\"p-3\">
                      <span className={px-2 py-0.5 rounded text-[10px] uppercase font-bold }>
                        {j.status}
                      </span>
                    </td>
                    <td className=\"p-3 text-[11px] text-slate-400 whitespace-nowrap\">
                      {new Date(j.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>'''

assert '</form>' in content, 'Closing form tag not found'
content = content.replace('      </form>', history_section)
with open(r'D:\ai-system-s\frontend\src\app\discovery\page.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
print('Successfully written discovery page with job history table.')
