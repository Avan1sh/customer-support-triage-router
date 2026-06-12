import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

const BAR_COLORS = {
  Critical: 'bg-red-500',
  High: 'bg-orange-500',
  Medium: 'bg-blue-500',
  Low: 'bg-green-500',
}

const PRIORITY_BADGE = {
  Critical: 'bg-red-100 text-red-800',
  High: 'bg-orange-100 text-orange-800',
  Medium: 'bg-blue-100 text-blue-800',
  Low: 'bg-green-100 text-green-800',
}

function Kpi({ label, value, accent }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4">
      <div className="text-xs text-gray-500">{label}</div>
      <div className={`text-3xl font-bold ${accent || 'text-gray-900'}`}>{value}</div>
    </div>
  )
}

function BarChart({ title, data }) {
  const entries = Object.entries(data || {})
  const max = Math.max(1, ...entries.map(([, v]) => v))
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4">
      <h3 className="text-sm font-semibold text-gray-700 mb-3">{title}</h3>
      {entries.length === 0 ? (
        <p className="text-sm text-gray-400">No data yet</p>
      ) : (
        <div className="space-y-2">
          {entries.map(([label, value]) => (
            <div key={label} className="flex items-center gap-2">
              <span className="w-32 truncate text-xs text-gray-600" title={label}>{label}</span>
              <div className="flex-1 bg-gray-100 rounded h-4 overflow-hidden">
                <div
                  className={`h-4 ${BAR_COLORS[label] || 'bg-indigo-500'}`}
                  style={{ width: `${(value / max) * 100}%` }}
                />
              </div>
              <span className="w-8 text-right text-xs font-medium text-gray-700">{value}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default function Dashboard() {
  const [analytics, setAnalytics] = useState(null)
  const [tickets, setTickets] = useState([])
  const [error, setError] = useState('')
  const [updated, setUpdated] = useState(null)

  async function load() {
    try {
      const [a, t] = await Promise.all([
        fetch('/api/analytics').then((r) => r.json()),
        fetch('/api/tickets?limit=25').then((r) => r.json()),
      ])
      setAnalytics(a)
      setTickets(t)
      setError('')
      setUpdated(new Date())
    } catch {
      setError('Could not reach the API. Is it running?')
    }
  }

  useEffect(() => {
    load()
    const id = setInterval(load, 10000) // auto-refresh every 10s
    return () => clearInterval(id)
  }, [])

  const escalated = analytics
    ? Object.entries(analytics.by_team)
        .filter(([k]) => k.includes('Escalation'))
        .reduce((s, [, v]) => s + v, 0)
    : 0

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <header className="sticky top-0 z-10 bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-2xl">📊</span>
            <span className="text-xl font-semibold">Support Ops Dashboard</span>
          </div>
          <div className="flex items-center gap-3 text-sm">
            <span className="text-gray-400 hidden sm:inline">
              {updated ? `Updated ${updated.toLocaleTimeString()}` : 'Loading…'}
            </span>
            <button onClick={load} className="rounded-lg border border-gray-300 px-3 py-1.5 hover:bg-gray-50">
              Refresh
            </button>
            <Link to="/" className="rounded-lg bg-indigo-600 px-3 py-1.5 text-white hover:bg-indigo-700">
              ← Store
            </Link>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-6 space-y-6">
        {error && <div className="rounded-lg bg-red-50 text-red-700 p-3 text-sm">{error}</div>}

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Kpi label="Total tickets" value={analytics?.total ?? '—'} />
          <Kpi label="Critical" value={analytics?.by_priority?.Critical ?? 0} accent="text-red-600" />
          <Kpi label="Escalated" value={escalated} accent="text-orange-600" />
          <Kpi label="Open" value={analytics?.by_status?.Open ?? 0} accent="text-blue-600" />
        </div>

        <div className="grid md:grid-cols-2 gap-4">
          <BarChart title="By priority" data={analytics?.by_priority} />
          <BarChart title="By category" data={analytics?.by_category} />
          <BarChart title="By team" data={analytics?.by_team} />
          <BarChart title="By status" data={analytics?.by_status} />
        </div>

        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <div className="px-4 py-3 border-b border-gray-200 flex items-center justify-between">
            <h3 className="text-sm font-semibold text-gray-700">Recent tickets</h3>
            <span className="text-xs text-gray-400">auto-refreshes every 10s</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-gray-500 text-xs">
                <tr>
                  <th className="text-left px-4 py-2">#</th>
                  <th className="text-left px-4 py-2">Priority</th>
                  <th className="text-left px-4 py-2">Category</th>
                  <th className="text-left px-4 py-2">Team</th>
                  <th className="text-left px-4 py-2">Status</th>
                  <th className="text-left px-4 py-2">Summary</th>
                </tr>
              </thead>
              <tbody>
                {tickets.map((t) => (
                  <tr key={t.id} className="border-t border-gray-100">
                    <td className="px-4 py-2 text-gray-500">{t.id}</td>
                    <td className="px-4 py-2">
                      <span className={`px-2 py-0.5 rounded text-xs ${PRIORITY_BADGE[t.priority] || 'bg-gray-100'}`}>
                        {t.priority}
                      </span>
                    </td>
                    <td className="px-4 py-2">{t.category}</td>
                    <td className="px-4 py-2 text-gray-600">{t.assigned_team}</td>
                    <td className="px-4 py-2">{t.status}</td>
                    <td className="px-4 py-2 text-gray-600 max-w-xs truncate" title={t.summary}>{t.summary}</td>
                  </tr>
                ))}
                {tickets.length === 0 && (
                  <tr><td colSpan="6" className="px-4 py-6 text-center text-gray-400">No tickets yet</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  )
}
