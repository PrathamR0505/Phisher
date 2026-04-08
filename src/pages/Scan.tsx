import { useState, Component, useRef, type ReactNode } from 'react'
import Spline from '@splinetool/react-spline'
import { motion, AnimatePresence } from 'framer-motion'
import { AlertTriangle, ShieldCheck, Search, Link2, CheckCircle, XCircle, AlertOctagon, FileText, Image as ImageIcon, Upload } from 'lucide-react'

class SplineErrorBoundary extends Component<{ children: ReactNode }> {
  state = { hasError: false }
  static getDerivedStateFromError() { return { hasError: true } }
  render() { return this.state.hasError ? null : this.props.children }
}

console.error = (() => {
  const originalError = console.error
  return (...args: unknown[]) => {
    if (typeof args[0] === 'string' && args[0].includes('this model does not support image input')) return
    originalError.apply(console, args)
  }
})()

type ScanResult = { prediction: 'safe' | 'phishing' | 'suspicious'; risk_score: number; reasons: string[]; links: { link: string; domain: string; status: 'safe' | 'phishing' | 'suspicious' }[] }

export function Scan() {
  const [text, setText] = useState('')
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [result, setResult] = useState<ScanResult | null>(null)

  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleScan = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!text.trim()) return
    setStatus('loading')
    setErrorMessage(null)
    try {
      const res = await fetch('http://127.0.0.1:5000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: text })
      })
      if (!res.ok) {
        const errData = await res.json()
        throw new Error(errData.error || `HTTP error! status: ${res.status}`)
      }
      const data = await res.json()
      setResult(data)
      setStatus('success')
    } catch (err: any) {
      console.error('Scan failed:', err)
      setErrorMessage(err.message || 'Connection failed')
      setStatus('error')
    }
  }

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setStatus('loading')
    setErrorMessage(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await fetch('http://127.0.0.1:5000/predict-file', {
        method: 'POST',
        body: formData,
      })

      if (!res.ok) {
        const errData = await res.json()
        throw new Error(errData.error || `HTTP error! status: ${res.status}`)
      }

      const data = await res.json()
      setResult(data)
      setStatus('success')
    } catch (err: any) {
      console.error('File scan failed:', err)
      setErrorMessage(err.message || 'File processing failed')
      setStatus('error')
    } finally {
      // Reset input so same file can be selected again
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  const isPhishing = result?.prediction?.toLowerCase() === 'phishing'
  const isSuspicious = result?.prediction?.toLowerCase() === 'suspicious'
  const isSafe = result?.prediction?.toLowerCase() === 'safe'

  return (
    <main className="pointer-events-none relative z-10 flex min-h-[calc(100svh-96px)] flex-col px-4 pb-8 md:px-8">
      <div className="relative mx-auto mt-6 flex w-full max-w-4xl flex-1 flex-col gap-8 md:mt-12 lg:flex-row">
        <motion.div initial={{ opacity: 0, x: -24 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }} className="flex flex-1 flex-col rounded-3xl border border-white/5 bg-black/10 p-6 shadow-2xl backdrop-blur-md md:p-8">
          <div className="mb-6 flex items-center gap-3">
            <div className={`flex h-10 w-10 items-center justify-center rounded-full ${isPhishing ? 'bg-rose-500/20 text-rose-400' : isSuspicious ? 'bg-amber-500/20 text-amber-400' : 'bg-emerald-500/20 text-emerald-400'}`}>
              <Search className="h-5 w-5" />
            </div>
            <h1 className="text-2xl font-bold text-white uppercase tracking-tight">Email / File Scanner</h1>
          </div>

          <form onSubmit={handleScan} className="flex flex-1 flex-col gap-4">
            <div className="pointer-events-auto relative flex min-h-[220px] flex-1 overflow-hidden rounded-2xl border border-white/10 bg-black/20 focus-within:border-white/30 transition-all">
              <div className="absolute inset-0 z-0 overflow-hidden rounded-2xl">
                <div className="absolute left-1/2 top-1/2 h-[120%] w-[120%] -translate-x-1/2 -translate-y-1/2">
                  <SplineErrorBoundary><Spline scene="https://prod.spline.design/gqdgUa0EgIl1DKRK/scene.splinecode" style={{ width: '100%', height: '100%', position: 'absolute' }} /></SplineErrorBoundary>
                </div>
              </div>
              <div className="pointer-events-none absolute inset-0 z-0 bg-black/40 mix-blend-overlay" />
              <textarea className="pointer-events-auto relative z-10 flex-1 resize-none bg-transparent p-5 text-sm text-white/90 placeholder:text-white/50 focus:outline-none" placeholder="Paste email content here, or upload a file below..." value={text} onChange={(e) => setText(e.target.value)} disabled={status === 'loading'} />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                disabled={status === 'loading'}
                className="pointer-events-auto flex items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/5 py-4 text-[10px] font-bold tracking-[0.2em] text-white/70 transition hover:bg-white/10 hover:text-white active:scale-95 disabled:opacity-50"
              >
                <FileText className="h-4 w-4" />
                <span>UPLOAD PDF</span>
              </button>
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                disabled={status === 'loading'}
                className="pointer-events-auto flex items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/5 py-4 text-[10px] font-bold tracking-[0.2em] text-white/70 transition hover:bg-white/10 hover:text-white active:scale-95 disabled:opacity-50"
              >
                <ImageIcon className="h-4 w-4" />
                <span>UPLOAD IMAGE</span>
              </button>
            </div>

            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              className="hidden"
              accept=".pdf,image/*"
            />

            <button type="submit" disabled={status === 'loading' || !text.trim()} className={`pointer-events-auto flex w-full items-center justify-center gap-2 rounded-xl px-6 py-4 font-bold transition-all active:scale-[0.98] disabled:opacity-50 ${isPhishing ? 'bg-rose-500 hover:bg-rose-600 shadow-[0_4px_12px_rgba(244,63,94,0.3)]' : isSuspicious ? 'bg-amber-500 hover:bg-amber-600 shadow-[0_4px_12px_rgba(245,158,11,0.3)]' : 'bg-emerald-500 hover:bg-emerald-600 shadow-[0_4px_12px_rgba(16,185,129,0.3)]'} text-white`}>
              {status === 'loading' ? <div className="h-5 w-5 animate-spin rounded-full border-2 border-current border-t-transparent" /> : <><Search className="h-5 w-5" /><span>INITIATE SCAN</span></>}
            </button>

            {status === 'error' && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-3 text-center">
                <p className="text-xs text-rose-400 font-medium">{errorMessage || "Backend not running"}</p>
              </motion.div>
            )}
          </form>
        </motion.div>

        <AnimatePresence mode="popLayout">
          {result && status === 'success' && (
            <motion.div initial={{ opacity: 0, x: 24, scale: 0.95 }} animate={{ opacity: 1, x: 0, scale: 1 }} transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }} className="pointer-events-none relative flex w-full flex-col overflow-hidden rounded-3xl border border-white/10 bg-black/40 p-6 shadow-2xl backdrop-blur-2xl lg:w-[420px]">
              <div className={`pointer-events-none absolute -right-20 -top-20 z-0 h-72 w-72 rounded-full opacity-60 blur-[80px] ${isPhishing ? 'bg-rose-600/50 animate-pulse' : isSuspicious ? 'bg-amber-600/40 animate-pulse' : 'bg-emerald-600/40 animate-[safe-ambient_4s_ease-in-out_infinite]'}`} />
              <h2 className="relative z-10 mb-6 text-[10px] font-bold tracking-[0.2em] text-white/50">ANALYSIS REPORT</h2>

              <div className={`relative z-10 mb-8 flex flex-col items-center justify-center overflow-hidden rounded-2xl border p-8 transition-all ${isPhishing ? 'border-rose-500/40 bg-gradient-to-b from-rose-500/20 shadow-[0_0_60px_rgba(244,63,94,0.3)] animate-[pulse-shadow_2s_ease-in-out_infinite]' : isSuspicious ? 'border-amber-500/40 bg-gradient-to-b from-amber-500/20 shadow-[0_0_60px_rgba(245,158,11,0.3)] animate-[suspicious-pulse_2.5s_ease-in-out_infinite]' : 'border-emerald-500/40 bg-gradient-to-b from-emerald-500/20 shadow-[0_0_60px_rgba(16,185,129,0.25)] animate-[safe-glow_3s_ease-in-out_infinite]'}`}>
                {isPhishing && <motion.div animate={{ y: ['-100%', '400%'] }} transition={{ repeat: Infinity, duration: 2, ease: 'linear' }} className="pointer-events-none absolute left-0 top-0 h-32 w-full bg-gradient-to-b from-transparent via-rose-500/20 to-transparent" />}
                {isSuspicious && <><motion.div animate={{ y: ['-100%', '400%'] }} transition={{ repeat: Infinity, duration: 3, ease: 'linear' }} className="pointer-events-none absolute left-0 top-0 h-32 w-full bg-gradient-to-b from-transparent via-amber-500/15 to-transparent" /><motion.div animate={{ scale: [1, 1.1, 1], opacity: [0.8, 1, 0.8] }} transition={{ repeat: Infinity, duration: 1.5 }} className="pointer-events-none absolute inset-0 rounded-2xl border-2 border-amber-500/20" /></>}
                {isSafe && <><motion.div animate={{ y: [0, -10, 0], opacity: [0.3, 0.6, 0.3] }} transition={{ repeat: Infinity, duration: 3 }} className="pointer-events-none absolute inset-0 bg-gradient-to-t from-emerald-500/10 via-transparent to-transparent" /><motion.div animate={{ x: [-20, 20, -20] }} transition={{ repeat: Infinity, duration: 4 }} className="pointer-events-none absolute h-1 w-32 rounded-full bg-emerald-400/30 blur-sm" style={{ top: '20%', left: '50%', transform: 'translateX(-50%)' }} /><div className="pointer-events-none absolute h-1 w-24 rounded-full bg-emerald-400/20 blur-sm" style={{ top: '70%', left: '50%', transform: 'translateX(-50%)' }} />{Array.from({ length: 3 }).map((_, i) => <motion.div key={i} animate={{ y: [0, -30, 0], opacity: [0, 0.6, 0] }} transition={{ repeat: Infinity, duration: 2.5 + i * 0.5, delay: i * 0.8 }} className="pointer-events-none absolute h-2 w-2 rounded-full bg-emerald-400/50" style={{ left: `${30 + i * 20}%`, bottom: '10%' }} />)}</>}
                {isPhishing ? <motion.div animate={{ scale: [1, 1.15, 1], rotate: [-5, 5, -5] }} transition={{ repeat: Infinity, duration: 2.5 }}><AlertTriangle className="mb-4 h-20 w-20 text-rose-500 drop-shadow-[0_0_30px_rgba(244,63,94,0.8)]" /></motion.div> : isSuspicious ? <motion.div animate={{ scale: [1, 1.1, 1], rotate: [-2, 2, -2] }} transition={{ repeat: Infinity, duration: 2 }}><AlertOctagon className="mb-4 h-20 w-20 text-amber-400 drop-shadow-[0_0_30px_rgba(245,158,11,0.8)]" /></motion.div> : <motion.div animate={{ y: [0, -8, 0], scale: [1, 1.05, 1] }} transition={{ repeat: Infinity, duration: 4 }}><ShieldCheck className="mb-4 h-20 w-20 text-emerald-400 drop-shadow-[0_0_30px_rgba(52,211,153,0.7)]" /></motion.div>}
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className={`text-4xl font-black uppercase tracking-widest ${isPhishing ? 'text-rose-400' : isSuspicious ? 'text-amber-400' : 'text-emerald-400'}`}>{result.prediction}</motion.div>
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }} className="mt-4 flex items-center gap-3 text-[11px] font-bold uppercase tracking-[0.15em] text-white/50">Risk Score <span className={`rounded-md border px-2.5 py-1 text-xs font-black ${result.risk_score >= 60 ? 'border-rose-500/50 bg-rose-500/30 text-rose-300' : result.risk_score >= 40 ? 'border-amber-500/50 bg-amber-500/30 text-amber-300' : 'border-emerald-500/50 bg-emerald-500/20 text-emerald-300'}`}>{result.risk_score}%</span></motion.div>
                {isSafe && <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.6 }} className="mt-4 text-sm text-emerald-300/80">This content appears legitimate</motion.p>}
                {isSuspicious && <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.6 }} className="mt-4 text-sm text-amber-300/80">Requires extra verification</motion.p>}
              </div>

              {result.reasons.length > 0 && <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }} className="relative z-10 mb-8"><h3 className={`mb-4 flex items-center gap-2 text-[10px] font-bold tracking-[0.2em] ${isPhishing ? 'text-rose-400/70' : isSuspicious ? 'text-amber-400/70' : 'text-emerald-400/70'}`}>{isPhishing ? <><AlertTriangle className="h-3.5 w-3.5" /> THREATS DETECTED</> : isSuspicious ? <><AlertOctagon className="h-3.5 w-3.5" /> FLAGS DETECTED</> : <><ShieldCheck className="h-3.5 w-3.5" /> SECURITY CHECKS</>}</h3><ul className="flex flex-col gap-3">{result.reasons.map((reason, i) => <motion.li key={i} initial={{ opacity: 0, x: isSafe ? -20 : 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.5 + i * 0.1 }} className={`flex items-center gap-3 rounded-xl border p-3.5 ${isPhishing ? 'border-rose-500/20 bg-rose-500/15' : isSuspicious ? 'border-amber-500/20 bg-amber-500/15' : 'border-emerald-500/20 bg-emerald-500/15'}`}><div className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full ${isPhishing ? 'bg-rose-500/30' : isSuspicious ? 'bg-amber-500/30' : 'bg-emerald-500/30'}`}>{isPhishing ? <XCircle className="h-3.5 w-3.5 text-rose-400" /> : isSuspicious ? <AlertOctagon className="h-3.5 w-3.5 text-amber-400" /> : <CheckCircle className="h-3.5 w-3.5 text-emerald-400" />}</div><span className={`text-sm font-medium ${isPhishing ? 'text-rose-100' : isSuspicious ? 'text-amber-100' : 'text-emerald-100'}`}>{reason}</span></motion.li>)}</ul></motion.div>}

              {isSafe && result.reasons.length === 0 && <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 }} className="relative z-10 mb-8 flex flex-col items-center rounded-2xl border border-emerald-500/30 bg-emerald-500/10 p-6 text-center"><CheckCircle className="mb-3 h-10 w-10 text-emerald-400" /><p className="text-sm font-medium text-emerald-200/90">No malicious indicators</p><p className="mt-1 text-xs text-emerald-300/60">All security checks passed</p></motion.div>}

              {result.links.length > 0 && <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }} className="relative z-10"><h3 className={`mb-4 flex items-center gap-2 text-[10px] font-bold tracking-[0.2em] ${isPhishing ? 'text-rose-400/70' : isSuspicious ? 'text-amber-400/70' : 'text-emerald-400/70'}`}><Link2 className="h-3.5 w-3.5" /> URL DIAGNOSTICS</h3><ul className="flex flex-col gap-2">{result.links.map((l, i) => <motion.li key={i} initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.7 + i * 0.1 }} className={`flex items-center justify-between gap-4 rounded-xl border px-4 py-3 text-xs ${l.status?.toLowerCase() === 'phishing' ? 'border-rose-500/30 bg-rose-500/10' : l.status?.toLowerCase() === 'suspicious' ? 'border-amber-500/30 bg-amber-500/10' : 'border-emerald-500/30 bg-emerald-500/10'}`}><div className="flex flex-1 flex-col gap-1 min-w-0"><span className="truncate text-white/60">{l.link}</span>{l.domain && <span className={`text-[10px] ${l.status?.toLowerCase() === 'phishing' ? 'text-rose-400/60' : l.status?.toLowerCase() === 'suspicious' ? 'text-amber-400/60' : 'text-emerald-400/60'}`}>Domain: {l.domain}</span>}</div><span className={`shrink-0 flex items-center gap-1 rounded border px-2.5 py-1.5 text-[10px] font-bold uppercase ${l.status?.toLowerCase() === 'phishing' ? 'border-rose-500/50 bg-rose-500/20 text-rose-400' : l.status?.toLowerCase() === 'suspicious' ? 'border-amber-500/50 bg-amber-500/20 text-amber-400' : 'border-emerald-500/50 bg-emerald-500/20 text-emerald-400'}`}>{l.status?.toLowerCase() === 'phishing' ? <XCircle className="h-3 w-3" /> : l.status?.toLowerCase() === 'suspicious' ? <AlertOctagon className="h-3 w-3" /> : <CheckCircle className="h-3 w-3" />}{l.status}</span></motion.li>)}</ul></motion.div>}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
      <style>{`@keyframes pulse-shadow{0%,100%{box-shadow:0 0 60px rgba(244,63,94,0.3)}50%{box-shadow:0 0 80px rgba(244,63,94,0.5)}}@keyframes suspicious-pulse{0%,100%{box-shadow:0 0 50px rgba(245,158,11,0.3)}50%{box-shadow:0 0 70px rgba(245,158,11,0.5)}}@keyframes safe-glow{0%,100%{box-shadow:0 0 50px rgba(16,185,129,0.2)}50%{box-shadow:0 0 80px rgba(16,185,129,0.4)}}@keyframes safe-ambient{0%,100%{opacity:0.4;transform:scale(1)}50%{opacity:0.7;transform:scale(1.1)}}`}</style>
    </main>
  )
}
