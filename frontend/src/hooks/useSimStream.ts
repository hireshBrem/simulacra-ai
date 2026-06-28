'use client'

import { useCallback, useRef, useState } from 'react'
import { simBus } from '@/lib/simBus'
import type { SimEvent } from '@/lib/simBus'

const API = 'http://localhost:8000/api'

export function useSimStream() {
  const sourceRef = useRef<EventSource | null>(null)
  const [isRunning, setIsRunning] = useState(false)

  const connect = useCallback((url: string) => {
    sourceRef.current?.close()
    setIsRunning(true)

    const source = new EventSource(url)
    sourceRef.current = source

    source.onmessage = (e: MessageEvent) => {
      const event = JSON.parse(e.data) as SimEvent
      simBus.emit('sim', event)
      if (event.type === 'done' || event.type === 'error') {
        source.close()
        setIsRunning(false)
      }
    }

    source.onerror = () => {
      source.close()
      setIsRunning(false)
    }
  }, [])

  const runWorldEvent = useCallback((event?: string) => {
    const params = event ? `?event=${encodeURIComponent(event)}` : ''
    connect(`${API}/stream/world-event${params}`)
  }, [connect])

  const runEncounter = useCallback((topic?: string, exchanges = 4) => {
    const params = new URLSearchParams({ exchanges: String(exchanges) })
    if (topic) params.set('topic', topic)
    connect(`${API}/stream/encounter?${params}`)
  }, [connect])

  const runSimulation = useCallback(() => {
    const params = new URLSearchParams({
      tick_seconds: '2',
      max_ticks: '0',
      max_agents: '4',
      tick_minutes: '5',
      use_llm: 'true',
    })
    connect(`${API}/stream/simulation?${params}`)
  }, [connect])

  const stop = useCallback(() => {
    sourceRef.current?.close()
    setIsRunning(false)
  }, [])

  return { isRunning, runWorldEvent, runEncounter, runSimulation, stop }
}
