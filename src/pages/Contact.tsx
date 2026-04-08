import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Mail, MessageSquare, Send, User, Sparkles, CheckCircle2 } from 'lucide-react'

export function Contact() {
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setStatus('loading')
    const form = e.currentTarget
    const data = new FormData(form)

    try {
      const res = await fetch('https://formspree.io/f/mnjogyrz', {
        method: 'POST',
        body: data,
        headers: { Accept: 'application/json' },
      })
      if (res.ok) {
        setStatus('success')
        form.reset()
        setTimeout(() => setStatus('idle'), 5000) // Reset after 5 seconds
      } else {
        setStatus('error')
      }
    } catch {
      setStatus('error')
    }
  }

  return (
    <main className="pointer-events-none relative z-10 flex min-h-[calc(100svh-96px)] flex-col px-4 pb-8 md:px-8">
      <div className="relative mx-auto mt-6 flex w-full max-w-5xl flex-1 flex-col items-center justify-center gap-12 md:mt-12 lg:flex-row lg:justify-between lg:gap-20">

        {/* Left Side: Header & Info */}
        <motion.div
          initial={{ opacity: 0, x: -24 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
          className="flex max-w-lg flex-col pt-8 lg:pt-0"
        >
          <div className="mb-4 flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-emerald-400" />
            <h2 className="text-sm font-black tracking-[0.2em] text-emerald-400">CONNECT WITH US</h2>
          </div>

          <h1 className="mb-6 text-4xl font-black uppercase tracking-wider text-white md:text-6xl">
            GET IN <span className="text-white/40">TOUCH</span>
          </h1>

          <p className="mb-10 text-lg leading-relaxed text-white/50">
            Whether you need hands-on technical support, enterprise security integration, or want to explore partnership opportunities, our team is ready to assist.
          </p>

          <div className="flex flex-col gap-6">
            <div className="group flex items-center gap-5 rounded-2xl border border-white/5 bg-white/5 p-4 backdrop-blur-sm transition-all hover:bg-white/10 hover:border-white/10">
              {/* Sleek Homepage Glass Icon Aesthetic */}
              <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-white/10 to-white/5 shadow-inner ring-1 ring-white/10 transition-transform group-hover:scale-110">
                <Mail className="h-6 w-6 text-white" />
              </div>
              <div>
                <div className="text-xs font-bold tracking-widest text-white/40 uppercase transition-colors group-hover:text-white/60">Email Support</div>
                <div className="mt-1 text-sm font-medium text-white/90">prathamr.0513@gmail.com</div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Right Side: The Contact Form */}
        <motion.div
          initial={{ opacity: 0, x: 24 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, delay: 0.1, ease: [0.22, 1, 0.36, 1] }}
          className="pointer-events-none relative w-full max-w-md"
        >
          {/* Animated Background Drop Glow */}
          <div className="pointer-events-none absolute -inset-4 -z-10 rounded-[3rem] bg-emerald-500/10 blur-[80px]" />

          <div className="relative flex flex-col overflow-hidden rounded-3xl border border-white/10 bg-black/40 p-8 shadow-2xl backdrop-blur-xl">

            <AnimatePresence mode="wait">
              {status === 'success' ? (
                <motion.div
                  key="success"
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0 }}
                  className="flex min-h-[350px] flex-col items-center justify-center text-center"
                >
                  <motion.div animate={{ scale: [1, 1.1, 1] }} transition={{ repeat: Infinity, duration: 2.5 }}>
                    <CheckCircle2 className="mb-6 h-20 w-20 text-emerald-400 drop-shadow-[0_0_15px_rgba(52,211,153,0.5)]" />
                  </motion.div>
                  <h3 className="mb-2 text-2xl font-black uppercase tracking-wider text-white">Message Sent</h3>
                  <p className="text-white/50">We've received your request and will be in touch shortly.</p>
                </motion.div>
              ) : (
                <motion.form
                  key="form"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  onSubmit={handleSubmit}
                  className="flex flex-col gap-5"
                >
                  {/* Name Input */}
                  <div className="group relative">
                    <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-4 text-white/30 group-focus-within:text-emerald-400">
                      <User className="h-4 w-4 transition-colors" />
                    </div>
                    <input
                      type="text"
                      name="name"
                      required
                      disabled={status === 'loading'}
                      className="pointer-events-auto w-full rounded-xl border border-white/10 bg-black/30 py-3.5 pl-11 pr-4 text-sm text-white placeholder-white/30 transition-all focus:border-emerald-500/50 focus:bg-emerald-500/5 focus:outline-none focus:ring-1 focus:ring-emerald-500/50 disabled:opacity-50"
                      placeholder="Your name"
                    />
                  </div>

                  {/* Email Input */}
                  <div className="group relative">
                    <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-4 text-white/30 group-focus-within:text-emerald-400">
                      <Mail className="h-4 w-4 transition-colors" />
                    </div>
                    <input
                      type="email"
                      name="email"
                      required
                      disabled={status === 'loading'}
                      className="pointer-events-auto w-full rounded-xl border border-white/10 bg-black/30 py-3.5 pl-11 pr-4 text-sm text-white placeholder-white/30 transition-all focus:border-emerald-500/50 focus:bg-emerald-500/5 focus:outline-none focus:ring-1 focus:ring-emerald-500/50 disabled:opacity-50"
                      placeholder="your@email.com"
                    />
                  </div>

                  {/* Message Input */}
                  <div className="group relative">
                    <div className="pointer-events-none absolute left-0 top-0 mt-4 flex items-center pl-4 text-white/30 group-focus-within:text-emerald-400">
                      <MessageSquare className="h-4 w-4 transition-colors" />
                    </div>
                    <textarea
                      name="message"
                      required
                      disabled={status === 'loading'}
                      rows={5}
                      className="pointer-events-auto w-full resize-none rounded-xl border border-white/10 bg-black/30 py-3.5 pl-11 pr-4 text-sm text-white placeholder-white/30 transition-all focus:border-emerald-500/50 focus:bg-emerald-500/5 focus:outline-none focus:ring-1 focus:ring-emerald-500/50 disabled:opacity-50"
                      placeholder="How can we help?"
                    />
                  </div>

                  {status === 'error' && (
                    <div className="rounded-lg bg-rose-500/10 px-4 py-3 text-xs text-rose-400 border border-rose-500/20">
                      Something went wrong submitting your form. Please try again.
                    </div>
                  )}

                  {/* Submit Button */}
                  <button
                    type="submit"
                    disabled={status === 'loading'}
                    className="pointer-events-auto group relative mt-2 flex w-full items-center justify-center gap-2 overflow-hidden rounded-xl bg-white px-6 py-4 font-bold text-black transition-all hover:bg-emerald-400 active:scale-[0.98] disabled:opacity-50 disabled:active:scale-100"
                  >
                    {status === 'loading' ? (
                      <div className="h-5 w-5 animate-spin rounded-full border-2 border-black border-t-transparent" />
                    ) : (
                      <>
                        <span>SEND MESSAGE</span>
                        <Send className="h-4 w-4 transition-transform group-hover:translate-x-1 group-hover:-translate-y-1" />
                      </>
                    )}
                  </button>
                </motion.form>
              )}
            </AnimatePresence>
          </div>
        </motion.div>
      </div>
    </main>
  )
}
