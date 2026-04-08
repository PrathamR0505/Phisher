import { useEffect } from 'react'
import { motion, useSpring } from 'framer-motion'
import Spline from '@splinetool/react-spline'
import { Link, useLocation } from 'wouter'
import { Home } from './pages/Home'
import { About } from './pages/About'
import { Scan } from './pages/Scan'
import { Contact } from './pages/Contact'

function useParallax() {
  const springX = useSpring(0, { stiffness: 120, damping: 24, mass: 0.4 })
  const springY = useSpring(0, { stiffness: 120, damping: 24, mass: 0.4 })

  useEffect(() => {
    const onMove = (e: MouseEvent) => {
      const x = (e.clientX / window.innerWidth - 0.5) * 2
      const y = (e.clientY / window.innerHeight - 0.5) * 2
      springX.set(x * 18)
      springY.set(y * 14)
    }
    window.addEventListener('mousemove', onMove, { passive: true })
    return () => window.removeEventListener('mousemove', onMove)
  }, [springX, springY])

  return { springX, springY }
}

export default function App() {
  const { springX, springY } = useParallax()
  const [location] = useLocation()
  const isHome = location === '/'
  const isAbout = location === '/about'
  const isScan = location === '/scan'
  const isContact = location === '/contact'

  return (
    <div className="relative min-h-svh w-full overflow-x-hidden bg-black text-white">
      <div id="spline-wrapper" className="pointer-events-none fixed inset-0 z-0 select-none h-svh w-svw overflow-hidden bg-black">
        {/* Scaled-up wrapper: Pushes the watermark perfectly outside the screen boundaries while keeping the background centered */}
        <div className="absolute left-1/2 top-1/2 h-[120vh] w-[120vw] -translate-x-1/2 -translate-y-1/2">
          <Spline
            scene="https://prod.spline.design/hfRF7TwkN8Ac9MKN/scene.splinecode"
            className="pointer-events-auto"
            style={{ width: '100%', height: '100%', position: 'absolute' }}
          />
        </div>
        <div className="noise-overlay pointer-events-none absolute inset-0 opacity-[0.04]" />
        {/* Foggy/smoky overlay to soften the 3D scene */}
        <div className="pointer-events-none absolute inset-0 bg-gradient-to-b from-black/20 via-black/5 to-black/40 backdrop-blur-[1.5px] mix-blend-overlay" />
      </div>

      <motion.header
        style={isHome ? { x: springX, y: springY } : undefined}
        className="pointer-events-none relative z-20 flex items-center justify-between px-6 py-6 md:px-12 md:py-8"
        initial={{ opacity: 0, y: -16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
      >
        <Link href="/">
          <span className="pointer-events-auto cursor-pointer text-sm font-bold tracking-[0.2em] md:text-base transition hover:text-white/80">HACKAHOLICS</span>
        </Link>
        <nav className="pointer-events-auto hidden items-center gap-8 text-[11px] font-medium tracking-[0.18em] md:flex">
          <Link href="/" className={`transition-colors ${location === '/' ? 'text-white' : 'text-white/60 hover:text-white'}`}>
            HOME
          </Link>
          <a href="#" className="text-white/60 transition-colors hover:text-white">SERVICES</a>
          <Link href="/contact" className={`transition-colors ${location === '/contact' ? 'text-white' : 'text-white/60 hover:text-white'}`}>
            GET IN TOUCH
          </Link>
          <Link href="/about" className={`transition-colors ${location === '/about' ? 'text-white' : 'text-white/60 hover:text-white'}`}>
            ABOUT
          </Link>
        </nav>
      </motion.header>

      <div className={!isAbout && !isScan && !isContact ? 'contents' : 'hidden'}>
        <Home springX={springX} springY={springY} />
      </div>
      <div className={isAbout ? 'contents' : 'hidden'}>
        <About />
      </div>
      <div className={isScan ? 'contents' : 'hidden'}>
        <Scan />
      </div>
      <div className={isContact ? 'contents' : 'hidden'}>
        <Contact />
      </div>
    </div>
  )
}
