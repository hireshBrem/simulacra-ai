'use client'

import { useEffect, useMemo, useState } from 'react'
import { AGENT_CONFIG } from '@/game/constants'
import { simBus } from '@/lib/simBus'
import type { SimEvent } from '@/lib/simBus'

interface AgentState {
  name: string
  mood: string
  lastAction: string
  actionType: string
  activeAt: number
}

interface ActivityItem {
  id: string
  label: string
  detail: string
}

type LogEntryTone = 'system' | 'speech' | 'memory' | 'error'

interface LogEntry {
  id: string
  tone: LogEntryTone
  label: string
  detail: string
  meta?: string
}

interface CurrentRun {
  kind: 'World Event' | 'Encounter' | 'Live Simulation'
  title: string
  participants: Array<{ agent_id: string; name: string }>
}

interface SimUIProps {
  isRunning: boolean
  onSimulation: () => void
  onStop: () => void
}

const roster = Object.entries(AGENT_CONFIG).map(([id, cfg]) => ({ id, ...cfg }))

export default function SimUI({ isRunning, onSimulation, onStop }: SimUIProps) {
  const [agents, setAgents] = useState<Record<string, AgentState>>({})
  const [activity, setActivity] = useState<ActivityItem[]>([])
  const [logEntries, setLogEntries] = useState<LogEntry[]>([])
  const [currentRun, setCurrentRun] = useState<CurrentRun | null>(null)
  const [isLogOpen, setIsLogOpen] = useState(true)
  const [statusLine, setStatusLine] = useState('IDLE - run a simulation to begin')
  const [eventText, setEventText] = useState<string | null>(null)

  useEffect(() => {
    const addActivity = (label: string, detail: string) => {
      setActivity(prev => [{ id: crypto.randomUUID(), label, detail }, ...prev].slice(0, 8))
    }

    const addLogEntry = (entry: Omit<LogEntry, 'id'>) => {
      setLogEntries(prev => [...prev, { id: crypto.randomUUID(), ...entry }])
    }

    const handler = (e: SimEvent) => {
      switch (e.type) {
        case 'simulation_started':
          setIsLogOpen(true)
          setEventText('Live SF simulation running')
          setCurrentRun({ kind: 'Live Simulation', title: 'Persistent SF simulation', participants: [] })
          setLogEntries([{
            id: crypto.randomUUID(),
            tone: 'system',
            label: 'Simulation started',
            detail: 'The backend Simulation Model is advancing step by step.',
          }])
          setStatusLine('LIVE SIMULATION RUNNING...')
          addActivity('Live simulation', 'step-based Simulation Model started')
          break

        case 'tick_started':
          setStatusLine(`STEP ${e.step} / ${e.current_time}`)
          break

        case 'tick_done':
          setStatusLine(`STEP ${e.step} COMPLETE / ${e.current_time}`)
          break

        case 'simulation_stopped':
          setStatusLine(`LIVE SIMULATION STOPPED AFTER ${e.ticks_run} TICKS`)
          addLogEntry({
            tone: 'system',
            label: 'Simulation stopped',
            detail: `${e.ticks_run} ticks completed.`,
          })
          break

        case 'world_event':
          setEventText(e.content)
          setIsLogOpen(true)
          setCurrentRun({ kind: 'World Event', title: e.content, participants: [] })
          setLogEntries([{
            id: crypto.randomUUID(),
            tone: 'system',
            label: 'World event',
            detail: e.content,
          }])
          setStatusLine('WORLD EVENT UNFOLDING...')
          addActivity('World event', e.content.slice(0, 120))
          break

        case 'agent_thinking':
          setStatusLine(`${e.agent_name} is thinking...`)
          addLogEntry({
            tone: 'system',
            label: e.agent_name,
            detail: 'Thinking through the event.',
          })
          break

        case 'agent_action':
          setAgents(prev => ({
            ...prev,
            [e.agent_id]: {
              name: e.agent_name,
              mood: e.emotional_state,
              lastAction: e.public_action.slice(0, 120),
              actionType: e.action_type,
              activeAt: Date.now(),
            },
          }))
          setStatusLine(`${e.agent_name} -> ${e.action_type.replace('_', ' ')}`)
          addActivity(e.agent_name, `${e.action_type.replace('_', ' ')}: ${e.public_action.slice(0, 110)}`)
          addLogEntry({
            tone: 'speech',
            label: e.agent_name,
            meta: e.action_type.replace('_', ' '),
            detail: e.public_action,
          })
          break

        case 'agent_observed':
          setStatusLine(`${e.agent_name} is observing ${e.zone}`)
          addActivity(e.agent_name, `observing ${e.zone}`)
          break

        case 'agent_planned':
          setAgents(prev => ({
            ...prev,
            [e.agent_id]: {
              name: e.agent_name,
              mood: e.emotional_state,
              lastAction: e.public_action.slice(0, 120),
              actionType: e.action_type,
              activeAt: Date.now(),
            },
          }))
          setStatusLine(`${e.agent_name} plans to ${e.action_type.replace('_', ' ')}`)
          addLogEntry({
            tone: 'system',
            label: e.agent_name,
            meta: e.action_type.replace('_', ' '),
            detail: e.public_action || e.inner_monologue,
          })
          break

        case 'agent_moved':
          setAgents(prev => ({
            ...prev,
            [e.agent_id]: {
              name: e.agent_name,
              mood: e.emotional_state,
              lastAction: e.activity.slice(0, 120),
              actionType: 'move',
              activeAt: Date.now(),
            },
          }))
          setStatusLine(`${e.agent_name} moved to ${e.to_zone}`)
          addActivity(e.agent_name, `${e.from_zone} -> ${e.to_zone}`)
          addLogEntry({
            tone: 'system',
            label: e.agent_name,
            meta: `${e.from_zone} -> ${e.to_zone}`,
            detail: e.activity,
          })
          break

        case 'encounter_start':
          setEventText(e.topic)
          setIsLogOpen(true)
          setCurrentRun({
            kind: 'Encounter',
            title: e.topic,
            participants: e.participants,
          })
          setLogEntries([{
            id: crypto.randomUUID(),
            tone: 'system',
            label: 'Encounter started',
            meta: e.participants.map(p => p.name).join(' x '),
            detail: e.topic,
          }])
          setStatusLine(`ENCOUNTER: ${e.participants.map(p => p.name).join(' x ')}`)
          addActivity('Encounter', e.participants.map(p => p.name).join(' x '))
          break

        case 'agent_utterance':
          setStatusLine(`${e.speaker_name} speaking (exchange ${e.exchange})`)
          addActivity(e.speaker_name, e.utterance.slice(0, 110))
          addLogEntry({
            tone: 'speech',
            label: e.speaker_name,
            meta: `Exchange ${e.exchange}`,
            detail: e.utterance,
          })
          break

        case 'memory_saved':
          setStatusLine(`${e.agent_name} committed a new memory`)
          addLogEntry({
            tone: 'memory',
            label: e.agent_name,
            meta: 'Memory saved',
            detail: e.entry,
          })
          break

        case 'reflection_saved':
          setStatusLine(`${e.agent_name} formed a reflection`)
          addLogEntry({
            tone: 'memory',
            label: e.agent_name,
            meta: 'Reflection saved',
            detail: e.entry,
          })
          break

        case 'encounter_end':
          setStatusLine(`ENCOUNTER ENDED: ${e.participants.map(p => p.name).join(' x ')}`)
          addLogEntry({
            tone: 'system',
            label: 'Encounter ended',
            meta: e.participants.map(p => p.name).join(' x '),
            detail: 'The conversation ended and participants saved memories.',
          })
          break

        case 'error':
          setStatusLine(`ERROR: ${e.message}`)
          addActivity('Error', e.message)
          setIsLogOpen(true)
          addLogEntry({
            tone: 'error',
            label: 'Error',
            detail: e.message,
          })
          break

        case 'done':
          setStatusLine('SIMULATION COMPLETE')
          addLogEntry({
            tone: 'system',
            label: 'Simulation complete',
            detail: 'All streamed events for this run have been received.',
          })
          break
      }
    }

    simBus.on('sim', handler)
    return () => simBus.off('sim', handler)
  }, [])

  const activeAgents = useMemo(() => {
    return Object.entries(agents)
      .sort((a, b) => b[1].activeAt - a[1].activeAt)
      .slice(0, 6)
  }, [agents])

  const btn =
    'px-4 py-3 font-mono text-sm border-2 transition-all disabled:opacity-30 disabled:cursor-not-allowed'
  const btnLive = `${btn} border-emerald-500 text-emerald-200 hover:bg-emerald-500/20 active:bg-emerald-500/40`
  const btnStop = `${btn} border-red-500 text-red-200 hover:bg-red-500/20 active:bg-red-500/40`
  const btnLog = `${btn} border-emerald-500 text-emerald-200 hover:bg-emerald-500/20 active:bg-emerald-500/40`

  return (
    <div className="mt-4 select-none font-mono">
      <div className="grid gap-3 bg-black/85 px-4 py-3 border border-slate-700/80 lg:grid-cols-[1fr_auto] lg:items-center">
        <div className="min-w-0">
          <div className="text-sm text-slate-500 uppercase tracking-widest">
            SAPIAVERSE / SF PUMS POPULATION
          </div>
          <div className="mt-1 truncate text-sm text-slate-300">
            {isRunning && <span className="text-green-400 mr-2">LIVE</span>}
            {statusLine}
          </div>
        </div>

        <div className="flex flex-wrap gap-3">
          <button onClick={onSimulation} disabled={isRunning} className={btnLive}>
            LIVE SIM
          </button>
          {isRunning && (
            <button onClick={onStop} className={btnStop}>
              STOP
            </button>
          )}
          <button onClick={() => setIsLogOpen(prev => !prev)} className={btnLog}>
            {isLogOpen ? 'CLOSE LOG' : 'OPEN LOG'}
          </button>
        </div>
      </div>

      {eventText && (
        <div className="mt-4 bg-black/85 border border-amber-600/60 px-5 py-3 text-center">
          <p className="text-amber-200 text-sm leading-6">{eventText}</p>
        </div>
      )}

      <div className="mt-4 grid w-full min-w-0 gap-4 select-none font-mono lg:grid-cols-[minmax(0,0.9fr)_minmax(0,1.35fr)_minmax(0,1.35fr)]">
        <div className="min-w-0 overflow-visible bg-black/85 border border-slate-700/80 px-4 py-3">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <span className="text-xs uppercase tracking-widest text-slate-500">Residents</span>
            <span className="text-xs text-slate-400">{roster.length}</span>
          </div>
          <div className="mt-3 grid grid-cols-2 gap-x-4 gap-y-2 sm:grid-cols-3 lg:grid-cols-2">
            {roster.map(agent => (
              <div
                key={agent.id}
                className="group relative flex items-center gap-2 min-w-0"
                title={`${agent.name} (${agent.identityInfo})`}
              >
                <span
                  className="h-3 w-3 shrink-0"
                  style={{ backgroundColor: `#${agent.color.toString(16).padStart(6, '0')}` }}
                />
                <span className="min-w-0 truncate text-sm text-slate-300">
                  {agent.name.split(' ')[0]}
                </span>
                <span className="pointer-events-none absolute left-5 top-1/2 z-30 hidden w-max max-w-[min(72vw,360px)] -translate-y-1/2 translate-x-2 whitespace-normal border border-slate-600 bg-[#05070b] px-2 py-1 text-xs leading-4 text-slate-300 shadow-[0_8px_24px_rgba(0,0,0,0.45)] group-hover:block">
                  ({agent.identityInfo})
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="min-w-0 min-h-44 overflow-hidden bg-black/85 border border-slate-700/80 px-4 py-3">
          <div className="text-xs uppercase tracking-widest text-slate-500 border-b border-slate-800 pb-2">
            Recent Activity
          </div>
          <div className="mt-3 space-y-2">
            {activity.length ? activity.map(item => (
              <div key={item.id} className="min-w-0 text-sm leading-5">
                <span className="break-words text-slate-300">{item.label}</span>
                <span className="text-slate-600"> / </span>
                <span className="break-words text-slate-500">{item.detail}</span>
              </div>
            )) : (
              <div className="text-sm text-slate-700 italic">awaiting simulation events...</div>
            )}
          </div>
        </div>

        <div className="min-w-0 min-h-44 overflow-hidden bg-black/85 border border-slate-700/80 px-4 py-3">
          <div className="text-xs uppercase tracking-widest text-slate-500 border-b border-slate-800 pb-2">
            Active Residents
          </div>
          <div className="mt-3 space-y-2">
            {activeAgents.length ? activeAgents.map(([id, a]) => (
              <div key={id} className="min-w-0 text-sm leading-5">
                <span className="break-words text-slate-300">{a.name}</span>
                <span className="text-slate-600"> / </span>
                <span className="break-words text-slate-500">{a.mood || 'unknown'}</span>
                <div className="min-w-0 truncate text-slate-600">
                  {a.actionType.replace('_', ' ')}: {a.lastAction}
                </div>
              </div>
            )) : (
              <div className="text-sm text-slate-700 italic">no resident has acted yet...</div>
            )}
          </div>
        </div>
      </div>

      <aside
        className={[
          'fixed right-0 top-0 z-50 h-screen w-full max-w-[390px] border-l border-emerald-500/40 bg-[#05070b]/95 font-mono shadow-[-16px_0_40px_rgba(0,0,0,0.45)] backdrop-blur-sm transition-transform duration-300',
          isLogOpen ? 'translate-x-0' : 'translate-x-[calc(100%-46px)]',
        ].join(' ')}
        aria-label="Simulation event log"
      >
        <button
          type="button"
          onClick={() => setIsLogOpen(prev => !prev)}
          className="absolute left-0 top-5 grid h-28 w-[46px] -translate-x-full place-items-center border border-r-0 border-emerald-500/40 bg-[#05070b]/95 text-[10px] uppercase tracking-widest text-emerald-200 transition-colors hover:bg-emerald-500/15"
          aria-label={isLogOpen ? 'Close simulation log' : 'Open simulation log'}
        >
          <span className="-rotate-90 whitespace-nowrap">{isLogOpen ? 'Close' : 'Logs'}</span>
        </button>

        <div className="flex h-full flex-col">
          <div className="border-b border-slate-800 px-5 py-4">
            <div className="flex items-center justify-between gap-3">
              <div className="min-w-0">
                <div className="text-xs uppercase tracking-widest text-emerald-300">
                  Simulation Log
                </div>
                <div className="mt-1 truncate text-sm text-slate-400">
                  {currentRun ? currentRun.kind : 'No event yet'}
                </div>
              </div>
              <div className={['h-2.5 w-2.5 shrink-0', isRunning ? 'bg-green-400' : 'bg-slate-700'].join(' ')} />
            </div>

            {currentRun && (
              <div className="mt-4">
                <p className="text-sm leading-5 text-slate-200">{currentRun.title}</p>
                {currentRun.participants.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {currentRun.participants.map(participant => (
                      <span
                        key={participant.agent_id}
                        className="border border-amber-500/40 bg-amber-500/10 px-2 py-1 text-xs text-amber-100"
                      >
                        {participant.name}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>

          <div className="min-h-0 flex-1 overflow-y-auto px-5 py-4">
            {logEntries.length ? (
              <div className="space-y-3">
                {logEntries.map((entry, index) => (
                  <div
                    key={entry.id}
                    className={[
                      'border-l-2 py-1 pl-3',
                      entry.tone === 'speech' && 'border-sky-500',
                      entry.tone === 'memory' && 'border-emerald-500',
                      entry.tone === 'error' && 'border-red-500',
                      entry.tone === 'system' && 'border-slate-600',
                    ].filter(Boolean).join(' ')}
                  >
                    <div className="flex items-baseline justify-between gap-3">
                      <span className="text-sm text-slate-200">{entry.label}</span>
                      <span className="shrink-0 text-[10px] uppercase tracking-wider text-slate-600">
                        {String(index + 1).padStart(2, '0')}
                      </span>
                    </div>
                    {entry.meta && (
                      <div className="mt-0.5 text-xs uppercase tracking-wider text-slate-500">
                        {entry.meta}
                      </div>
                    )}
                    <p className="mt-1 text-sm leading-5 text-slate-400">{entry.detail}</p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="border border-dashed border-slate-800 px-4 py-6 text-sm leading-6 text-slate-600">
                Run a world event or random encounter to populate the log.
              </div>
            )}
          </div>
        </div>
      </aside>
    </div>
  )
}
