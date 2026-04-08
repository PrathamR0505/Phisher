import { motion } from 'framer-motion'
import { Shield, Zap, Target, Cpu } from 'lucide-react'

export function About() {
  return (
    <main className="pointer-events-none relative z-10 flex min-h-[calc(100svh-96px)] flex-col px-4 pb-8 md:px-8">
      <div className="relative mx-auto flex w-full max-w-5xl flex-1 flex-col items-center justify-center gap-10">

        {/* Ambient Void Glow */}
        <div className="pointer-events-none absolute inset-0 -z-10 rounded-[4rem] bg-white/5 blur-[100px]" />

        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
          className="pointer-events-none relative w-full rounded-3xl border border-white/5 bg-black/40 p-6 shadow-2xl backdrop-blur-2xl md:p-10"
        >
          <div className="mb-4 flex flex-col items-center justify-center gap-4 text-center">
            {/* Minimalist Icon Badge */}
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-white/10 to-white/5 shadow-inner ring-1 ring-white/10">
              <Shield className="h-6 w-6 text-white" />
            </div>

            <h1 className="bg-gradient-to-br from-white to-white/40 bg-clip-text text-3xl font-black uppercase tracking-widest text-transparent md:text-5xl">
              Who We Are
            </h1>
          </div>

          <p className="mx-auto max-w-3xl text-center text-sm leading-relaxed text-white/50 md:text-base">
            At <strong className="font-bold text-white/90">Hackaholics</strong>, we build intelligent tools to detect and prevent phishing attacks in real time.

            Our goal is to make email communication safer by identifying suspicious patterns, malicious links, and deceptive content before users fall victim to scams.

            We combine machine learning with smart rule-based analysis to deliver fast, accurate, and transparent threat detection.
          </p>

          <div className="mt-8 grid gap-4 sm:grid-cols-3">

            {/* Card 1 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
              className="relative overflow-hidden rounded-2xl border border-white/5 bg-white/5 p-5 shadow-[0_15px_30px_rgba(255,255,255,0.02)]"
            >
              <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-white/10 to-white/5 shadow-inner ring-1 ring-white/10">
                <Zap className="h-4 w-4 text-white" />
              </div>
              <h2 className="mb-2 text-[10px] font-bold tracking-[0.2em] text-white/50 uppercase">The Tech</h2>
              <p className="text-[13px] leading-relaxed text-white/40">
                Real-time email analysis using machine learning and pattern detection. Identifies phishing attempts in under <span className="font-medium text-white/80">1 second</span>
              </p>
            </motion.div>

            {/* Card 2 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
              className="relative overflow-hidden rounded-2xl border border-white/5 bg-white/5 p-5 shadow-[0_15px_30px_rgba(255,255,255,0.02)]"
            >
              <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-white/10 to-white/5 shadow-inner ring-1 ring-white/10">
                <Target className="h-4 w-4 text-white" />
              </div>
              <h2 className="mb-2 text-[10px] font-bold tracking-[0.2em] text-white/50 uppercase">Our Promise</h2>
              <p className="text-[13px] leading-relaxed text-white/40">
                <span className="font-medium text-white/80">100% transparent results</span> Understand exactly why an email is flagged with clear reasons and risk scores.
              </p>
            </motion.div>

            {/* Card 3 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}
              className="relative overflow-hidden rounded-2xl border border-white/5 bg-white/5 p-5 shadow-[0_15px_30px_rgba(255,255,255,0.02)]"
            >
              <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-white/10 to-white/5 shadow-inner ring-1 ring-white/10">
                <Cpu className="h-4 w-4 text-white" />
              </div>
              <h2 className="mb-2 text-[10px] font-bold tracking-[0.2em] text-white/50 uppercase">The Team</h2>
              <p className="text-[13px] leading-relaxed text-white/40">
                A team of developers focused on building<span className="font-medium text-white/80"> simple and effective</span> cybersecurity solutions for everyday users.
              </p>
            </motion.div>

          </div>
        </motion.div>
      </div>
    </main>
  )
}
