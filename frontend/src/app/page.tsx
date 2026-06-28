'use client'

import dynamic from 'next/dynamic'
import BehavioralScenarios from '@/components/BehavioralScenarios'
import SimUI from '@/components/SimUI'
import { useSimStream } from '@/hooks/useSimStream'

const PhaserGame = dynamic(() => import('@/components/PhaserGame'), { ssr: false })

export default function Home() {
  const { isRunning, runSimulation, runBehavioralScenario, stop } = useSimStream()

  return (
    <main className="flex flex-col items-center justify-center min-h-screen bg-[#060610] px-5 py-6">
      <div className="relative w-full max-w-[1280px]">
        {/* Phaser canvas */}
        <PhaserGame />

        {/* React overlay — sits on top, pointer-events managed per child */}
        <SimUI
          isRunning={isRunning}
          onSimulation={() => runSimulation()}
          onStop={() => stop()}
        />

        <BehavioralScenarios
          isRunning={isRunning}
          onRun={runBehavioralScenario}
          onStop={() => stop()}
        />
      </div>

      <p className="mt-4 text-xs text-slate-700 font-mono">
        SAPIAVERSE · LLM social simulation · 30 PUMS-grounded San Francisco residents
      </p>
    </main>
  )
}
