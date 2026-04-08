import { motion, type MotionValue } from 'framer-motion'
import Spline from '@splinetool/react-spline'
import { useLocation } from 'wouter'
import { type ComponentType, type SVGProps } from 'react'
import {
  IconDownload,
  IconShield,
} from '../components/icons'

const pillItems = [
  { id: 'cyber', label: 'SCAN NOW', icon: IconShield, href: '/scan' },
  { id: 'digital', label: 'DOWNLOAD BROWSER EXTENSION', icon: IconDownload, href: 'https://github.com/sahanac0513/phishing-chrome-extention' },
] as const

export function Home({
  springX,
  springY,
}: {
  springX: MotionValue<number>
  springY: MotionValue<number>
}) {
  return (
    <main className="pointer-events-none relative z-10 flex min-h-[calc(100svh-96px)] flex-col px-4 pb-8 md:px-8">
      <div className="relative mx-auto flex w-full max-w-6xl flex-1 flex-col items-center">
        <motion.div
          className="relative z-20 mt-4 text-center md:mt-6"
          style={{ x: springX, y: springY }}
          initial="hidden"
          animate="show"
          variants={{
            hidden: {},
            show: { transition: { staggerChildren: 0.08, delayChildren: 0.15 } },
          }}
        >
          <motion.p
            variants={{
              hidden: { opacity: 0, y: 28, filter: 'blur(8px)' },
              show: {
                opacity: 1, y: 0, filter: 'blur(0px)',
                transition: { duration: 0.85, ease: [0.22, 1, 0.36, 1] },
              },
            }}
            className="bg-gradient-to-r from-white/70 to-white/30 bg-clip-text pb-2 text-[clamp(2.5rem,8vw,5.5rem)] font-extrabold leading-none tracking-tight text-transparent"
          >
            Cybersecurity simplified
          </motion.p>
          <motion.p
            variants={{
              hidden: { opacity: 0, y: 36, filter: 'blur(10px)' },
              show: {
                opacity: 1, y: 0, filter: 'blur(0px)',
                transition: { duration: 0.9, ease: [0.22, 1, 0.36, 1] },
              },
            }}
            className="mt-1 text-[clamp(3rem,12vw,7rem)] font-extrabold leading-none tracking-tight text-white drop-shadow-[0_0_15px_rgba(255,255,255,0.3)]"
          >
            Risks neutralized
          </motion.p>
        </motion.div>

        <motion.div
          className="pointer-events-none relative z-20 mt-12 flex w-full max-w-4xl flex-wrap justify-center gap-6 md:mt-16 md:gap-8"
          style={{ x: springX, y: springY }}
        >
          {pillItems.map((pill, i) => (
            <ServiceButton key={pill.id} {...pill} delay={i * 0.15} />
          ))}
        </motion.div>

        <div className="flex-1" />
      </div>

      <motion.footer
        className="pointer-events-none relative z-20 mx-auto mt-auto mb-6 flex w-full max-w-6xl flex-col items-start justify-between gap-8 rounded-2xl border border-white/5 bg-black/10 p-6 shadow-2xl backdrop-blur-md md:flex-row md:items-center md:px-10 md:py-8"
        style={{ x: springX, y: springY }}
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6, duration: 0.7 }}
      >
        <div className="flex w-full flex-wrap items-center gap-10 justify-between md:w-auto md:justify-start md:gap-16">
          {[
            { n: 'HIGHLY', l: 'ACCURATE' },
            { n: '< 1s', l: 'DETECTION TIME' },
            { n: '100%', l: 'TRANSPARENT RESULTS' },
          ].map((s) => (
            <Stat key={s.l} value={s.n} label={s.l} />
          ))}
        </div>
        {/* Footer placement box (matching exact previous button container size) */}
        <div className="group relative z-50 flex h-16 w-32 items-center justify-center self-end md:self-auto md:h-20 md:w-40">

          {/* Soft ambient glow to give the 3D model physical presence and depth */}
          <div className="absolute left-1/2 top-1/2 h-16 w-24 -translate-x-1/2 -translate-y-[80%] rounded-full bg-white/5 blur-[20px] transition-all duration-700 group-hover:bg-white/10 group-hover:blur-[28px] md:h-24 md:w-32" />

          {/* This is the visual bounds of the 3D object. It's larger than the footer box so it visibly pops out! */}
          <div className="pointer-events-none absolute left-1/2 top-1/2 h-[600px] w-[800px] -translate-x-1/2 -translate-y-[55%] md:-translate-y-[50%] overflow-hidden scale-[0.25] md:scale-[0.32]">

            {/* The mathematical crop guarantee! 
                By adding exactly +250px to both width and height, placing it relative to the 
                center translates to exactly a 125px margin overlapping OUTSIDE the box on all 4 sides. 
                The Spline watermark is ~35px tall and sits on the bottom right corner, permanently falling completely under this invisible 125px boundary line! */}
            <div className="pointer-events-auto absolute left-1/2 top-1/2 h-[calc(100%+250px)] w-[calc(100%+250px)] -translate-x-1/2 -translate-y-1/2">
              <Spline
                scene="https://prod.spline.design/UzNkboxIX-8Tc032/scene.splinecode"
                style={{ width: '100%', height: '100%', position: 'absolute' }}
              />
            </div>
          </div>
        </div>
      </motion.footer>
    </main>
  )
}

function ServiceButton({
  label,
  icon: Icon,
  delay,
  href,
}: {
  label: string
  icon: ComponentType<SVGProps<SVGSVGElement>>
  delay: number
  href?: string
}) {
  const [, setLocation] = useLocation()

  return (
    <motion.button
      type="button"
      onClick={() => {
        if (!href) return
        if (href.startsWith('http')) {
          window.open(href, '_blank', 'noopener,noreferrer')
        } else {
          setLocation(href)
        }
      }}
      className="pointer-events-auto group relative flex items-center gap-3 overflow-hidden rounded-full border border-white/10 bg-white/5 px-6 py-3.5 shadow-lg backdrop-blur-md transition-all hover:border-white/30 hover:bg-white/10 hover:shadow-[0_0_24px_rgba(255,255,255,0.1)] active:scale-95 md:gap-4 md:px-8 md:py-4"
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: 0.6 + delay, duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.98 }}
    >
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent opacity-0 transition-opacity duration-500 group-hover:opacity-100" />
      <Icon className="relative z-10 h-5 w-5 shrink-0 text-white/50 transition-colors duration-300 group-hover:text-white md:h-6 md:w-6" />
      <span className="relative z-10 text-[10px] font-bold tracking-[0.16em] text-white/70 transition-colors duration-300 group-hover:text-white md:text-[12px]">
        {label}
      </span>
    </motion.button>
  )
}

function Stat({ value, label }: { value: string; label: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
    >
      <motion.p
        className="text-3xl font-bold tracking-tight md:text-4xl"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.2 }}
      >
        {value.split('').map((ch, i) => (
          <motion.span
            key={`${ch}-${i}`}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.65 + i * 0.04 }}
          >
            {ch}
          </motion.span>
        ))}
      </motion.p>
      <p className="mt-1 max-w-[140px] text-[10px] font-medium uppercase leading-snug tracking-[0.14em] text-white/55 md:text-[11px]">
        {label}
      </p>
    </motion.div>
  )
}
