import { useState } from 'react'
import { Link } from 'react-router-dom'

const PRODUCTS = [
  { id: 1, name: 'Wireless Headphones', price: 129.99, emoji: '🎧', tag: 'Audio' },
  { id: 2, name: 'Mechanical Keyboard', price: 89.99, emoji: '⌨️', tag: 'Accessories' },
  { id: 3, name: 'Smart Watch', price: 199.99, emoji: '⌚', tag: 'Wearables' },
  { id: 4, name: '4K Webcam', price: 74.99, emoji: '📷', tag: 'Accessories' },
  { id: 5, name: 'USB-C Hub', price: 49.99, emoji: '🔌', tag: 'Accessories' },
  { id: 6, name: 'Portable SSD 1TB', price: 119.99, emoji: '💾', tag: 'Storage' },
]

const PRIORITY_STYLES = {
  Critical: 'bg-red-100 text-red-800',
  High: 'bg-orange-100 text-orange-800',
  Medium: 'bg-blue-100 text-blue-800',
  Low: 'bg-green-100 text-green-800',
}

export default function App() {
  const [open, setOpen] = useState(false)
  const [email, setEmail] = useState('')
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  async function submitQuery(e) {
    e.preventDefault()
    setError('')
    setResult(null)
    setLoading(true)
    try {
      const res = await fetch('/api/tickets', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, email: email || null }),
      })
      if (!res.ok) {
        const body = await res.json().catch(() => ({}))
        throw new Error(body.detail || `Request failed (${res.status})`)
      }
      setResult(await res.json())
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  function closeModal() {
    setOpen(false)
    setResult(null)
    setError('')
    setText('')
  }

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <header className="sticky top-0 z-10 bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-2xl">🛍️</span>
            <span className="text-xl font-semibold">Acme Store</span>
          </div>
          <nav className="flex items-center gap-6 text-sm text-gray-600">
            <a className="hover:text-gray-900 hidden sm:inline" href="#">Shop</a>
            <a className="hover:text-gray-900 hidden sm:inline" href="#">Deals</a>
            <Link to="/dashboard" className="hover:text-gray-900 hidden sm:inline">Dashboard</Link>
            <button
              onClick={() => setOpen(true)}
              className="rounded-lg bg-indigo-600 px-4 py-2 text-white font-medium hover:bg-indigo-700"
            >
              Need help?
            </button>
          </nav>
        </div>
      </header>

      <section className="max-w-6xl mx-auto px-4 py-10">
        <div className="rounded-2xl bg-indigo-600 text-white p-8 md:p-12">
          <h1 className="text-3xl md:text-4xl font-bold">Tech that just works.</h1>
          <p className="mt-2 text-indigo-100">
            Free shipping over $50 · 30-day returns · 24/7 AI-assisted support.
          </p>
        </div>
      </section>

      <main className="max-w-6xl mx-auto px-4 pb-24">
        <h2 className="text-lg font-semibold mb-4">Featured products</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {PRODUCTS.map((p) => (
            <div key={p.id} className="bg-white rounded-xl border border-gray-200 p-5 flex flex-col">
              <div className="text-5xl mb-4">{p.emoji}</div>
              <div className="text-xs text-gray-500">{p.tag}</div>
              <div className="font-medium">{p.name}</div>
              <div className="mt-1 font-semibold">${p.price.toFixed(2)}</div>
              <button className="mt-4 rounded-lg border border-gray-300 py-2 text-sm font-medium hover:bg-gray-50">
                Add to cart
              </button>
            </div>
          ))}
        </div>
      </main>

      <button
        onClick={() => setOpen(true)}
        className="fixed bottom-6 right-6 rounded-full bg-indigo-600 text-white px-5 py-3 shadow-lg hover:bg-indigo-700 font-medium"
      >
        💬 Raise a query
      </button>

      {open && (
        <div
          className="fixed inset-0 z-20 bg-black/40 flex items-center justify-center p-4"
          onClick={closeModal}
        >
          <div
            className="bg-white rounded-2xl max-w-lg w-full p-6"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Contact support</h3>
              <button onClick={closeModal} className="text-gray-400 hover:text-gray-600 text-xl">✕</button>
            </div>

            {!result ? (
              <form onSubmit={submitQuery} className="space-y-3">
                <div>
                  <label className="block text-sm text-gray-600 mb-1">Your email</label>
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@example.com"
                    className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-600 mb-1">How can we help?</label>
                  <textarea
                    required
                    rows={4}
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    placeholder="Describe your issue…"
                    className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                {error && <p className="text-sm text-red-600">{error}</p>}
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full rounded-lg bg-indigo-600 text-white py-2.5 font-medium hover:bg-indigo-700 disabled:opacity-60"
                >
                  {loading ? 'Submitting…' : 'Submit query'}
                </button>
              </form>
            ) : (
              <div className="space-y-3">
                <div className="rounded-lg bg-green-50 text-green-800 p-3 text-sm">
                  ✅ Query <span className="font-semibold">#{result.ticket_id}</span> registered.
                  {result.email_queued
                    ? <> A confirmation was emailed to <span className="font-medium">{email}</span>.</>
                    : email
                      ? <> We'll email <span className="font-medium">{email}</span> once email sending is configured.</>
                      : null}
                </div>
                <div className="flex flex-wrap gap-2 text-xs">
                  <span className="px-2 py-1 rounded bg-gray-100">{result.category}</span>
                  <span className={`px-2 py-1 rounded ${PRIORITY_STYLES[result.priority] || 'bg-gray-100'}`}>
                    {result.priority} priority
                  </span>
                  <span className="px-2 py-1 rounded bg-gray-100">{result.assigned_team}</span>
                  <span className="px-2 py-1 rounded bg-gray-100">SLA {result.sla_hours}h</span>
                </div>
                <p className="text-sm text-gray-700">
                  <span className="text-gray-500">Summary:</span> {result.summary}
                </p>
                {result.escalated ? (
                  <div className="rounded-lg bg-orange-50 text-orange-800 p-3 text-sm">
                    🚨 Your query was escalated — a senior specialist will reach out personally.
                  </div>
                ) : result.draft_reply ? (
                  <div className="rounded-lg border border-gray-200 p-3">
                    <div className="text-xs text-gray-500 mb-1">Our response</div>
                    <div className="font-medium text-sm mb-1">{result.draft_reply.subject}</div>
                    <p className="text-sm text-gray-700 whitespace-pre-line">{result.draft_reply.body}</p>
                  </div>
                ) : null}
                <button
                  onClick={closeModal}
                  className="w-full rounded-lg border border-gray-300 py-2 text-sm font-medium hover:bg-gray-50"
                >
                  Done
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
