'use client'

import { useEffect, useMemo, useState } from 'react'
import { AGENT_CONFIG } from '@/game/constants'
import { simBus } from '@/lib/simBus'
import type {
  BehavioralScenarioResponse,
  BehavioralScenarioSummary,
  SimEvent,
} from '@/lib/simBus'

type ResponseMode = 'yes_no_reason' | 'freeform'
type BreakdownMode = 'neighborhood' | 'income'

interface BehavioralScenariosProps {
  isRunning: boolean
  onRun: (
    title: string,
    prompt: string,
    responseMode: ResponseMode,
    useDeliveryAppExperiences: boolean,
  ) => void
  onStop: () => void
}

type ReasonSummary = { reason: string; count: number; example: string }
type VoteBreakdownRow = { label: string; yes: number; no: number; total: number }

const PROP_X_PROMPT = 'San Francisco is voting on a measure that would cap food delivery app fees (DoorDash, Uber Eats) at 15%. As a resident, would you vote Yes or No? Give your single most important reason in one sentence.'

export default function BehavioralScenarios({
  isRunning,
  onRun,
  onStop,
}: BehavioralScenariosProps) {
  const [title, setTitle] = useState('Prop X delivery fee cap')
  const [prompt, setPrompt] = useState(PROP_X_PROMPT)
  const [responseMode, setResponseMode] = useState<ResponseMode>('yes_no_reason')
  const [activeExperimentId, setActiveExperimentId] = useState<string | null>(null)
  const [activeTitle, setActiveTitle] = useState('')
  const [activePrompt, setActivePrompt] = useState('')
  const [responses, setResponses] = useState<BehavioralScenarioResponse[]>([])
  const [summary, setSummary] = useState<BehavioralScenarioSummary | null>(null)
  const [status, setStatus] = useState('Ready')
  const [activeResponseMode, setActiveResponseMode] = useState<ResponseMode>('yes_no_reason')
  const [breakdownMode, setBreakdownMode] = useState<BreakdownMode>('neighborhood')
  const [useDeliveryAppExperiences, setUseDeliveryAppExperiences] = useState(false)

  useEffect(() => {
    const handler = (event: SimEvent) => {
      switch (event.type) {
        case 'behavioral_scenario_started':
          setActiveExperimentId(event.experiment_id)
          setActiveTitle(event.title)
          setActivePrompt(event.prompt)
          setActiveResponseMode(event.response_mode)
          setResponses([])
          setSummary(null)
          setStatus('Running')
          break

        case 'behavioral_agent_response':
          setResponses(prev => [...prev, {
            agent_id: event.agent_id,
            agent_name: event.agent_name,
            response: event.response,
            vote: event.vote,
            reason: event.reason,
            delivery_app_experiences: event.delivery_app_experiences,
          }])
          setStatus(`${event.agent_name} responded`)
          break

        case 'behavioral_scenario_summary':
          setSummary(event.summary)
          setStatus('Summary ready')
          break

        case 'error':
          setStatus(event.message)
          break

        case 'done':
          if (activeExperimentId) setStatus('Complete')
          break
      }
    }

    simBus.on('sim', handler)
    return () => simBus.off('sim', handler)
  }, [activeExperimentId])

  const sortedResponses = useMemo(() => {
    return [...responses].sort((a, b) => {
      const left = Number(a.agent_id.replace('agent-', ''))
      const right = Number(b.agent_id.replace('agent-', ''))
      return left - right
    })
  }, [responses])

  const runDisabled = isRunning || !prompt.trim()
  const voteSplit = summary?.vote_split
  const yesPct = voteSplit?.total ? Math.round((voteSplit.yes / voteSplit.total) * 100) : 0
  const noPct = voteSplit?.total ? 100 - yesPct : 0
  const interimReasons = useMemo(() => ({
    yes: buildTopReasons(sortedResponses, 'Yes'),
    no: buildTopReasons(sortedResponses, 'No'),
  }), [sortedResponses])
  const topReasons = summary?.top_reasons ?? interimReasons
  const shouldShowReasonSummary = activeResponseMode === 'yes_no_reason' && (activeExperimentId || responses.length > 0)
  const voteBreakdown = useMemo(
    () => buildVoteBreakdown(sortedResponses, breakdownMode),
    [breakdownMode, sortedResponses],
  )
  const shouldShowVoteBreakdown = activeResponseMode === 'yes_no_reason' && (activeExperimentId || responses.length > 0)
  const responsesWithDeliveryExperiences = useMemo(
    () => sortedResponses.filter(response => response.delivery_app_experiences?.length),
    [sortedResponses],
  )

  const handleRun = () => {
    if (runDisabled) return
    onRun(
      title.trim() || 'Behavioral scenario',
      prompt.trim(),
      responseMode,
      useDeliveryAppExperiences,
    )
  }

  return (
    <section className="mt-4 w-full border border-slate-700/80 bg-black/85 px-4 py-4 font-mono text-slate-300">
      <div className="grid gap-4 lg:grid-cols-[minmax(0,0.95fr)_minmax(0,1.35fr)]">
        <div className="min-w-0">
          <div className="flex items-center justify-between gap-3 border-b border-slate-800 pb-2">
            <h2 className="text-sm text-emerald-300">Behavioral Scenarios</h2>
            <span className="text-xs text-slate-500">{status}</span>
          </div>

          <label className="mt-4 block text-xs text-slate-500" htmlFor="scenario-title">
            Title
          </label>
          <input
            id="scenario-title"
            value={title}
            onChange={event => setTitle(event.target.value)}
            className="mt-1 w-full border border-slate-700 bg-[#07090f] px-3 py-2 text-sm text-slate-200 outline-none focus:border-emerald-500"
          />

          <label className="mt-3 block text-xs text-slate-500" htmlFor="scenario-prompt">
            Prompt
          </label>
          <textarea
            id="scenario-prompt"
            value={prompt}
            onChange={event => setPrompt(event.target.value)}
            rows={6}
            className="mt-1 min-h-36 w-full resize-y border border-slate-700 bg-[#07090f] px-3 py-2 text-sm leading-5 text-slate-200 outline-none focus:border-emerald-500"
          />

          <div className="mt-3 flex flex-wrap items-center gap-2">
            <button
              type="button"
              onClick={() => {
                setTitle('Prop X delivery fee cap')
                setPrompt(PROP_X_PROMPT)
                setResponseMode('yes_no_reason')
              }}
              className="border border-amber-500/50 px-3 py-2 text-xs text-amber-100 hover:bg-amber-500/15"
            >
              Prop X preset
            </button>

            <button
              type="button"
              onClick={() => setResponseMode('yes_no_reason')}
              className={[
                'border px-3 py-2 text-xs',
                responseMode === 'yes_no_reason'
                  ? 'border-emerald-500 bg-emerald-500/15 text-emerald-100'
                  : 'border-slate-700 text-slate-400 hover:bg-slate-800',
              ].join(' ')}
            >
              Yes/No
            </button>

            <button
              type="button"
              onClick={() => setResponseMode('freeform')}
              className={[
                'border px-3 py-2 text-xs',
                responseMode === 'freeform'
                  ? 'border-emerald-500 bg-emerald-500/15 text-emerald-100'
                  : 'border-slate-700 text-slate-400 hover:bg-slate-800',
              ].join(' ')}
            >
              Freeform
            </button>

            <button
              type="button"
              onClick={() => setUseDeliveryAppExperiences(value => !value)}
              aria-pressed={useDeliveryAppExperiences}
              className={[
                'flex items-center gap-2 border px-3 py-2 text-xs',
                useDeliveryAppExperiences
                  ? 'border-cyan-400 bg-cyan-400/15 text-cyan-100'
                  : 'border-slate-700 text-slate-400 hover:bg-slate-800',
              ].join(' ')}
            >
              <span
                className={[
                  'relative h-3 w-6 border transition-colors',
                  useDeliveryAppExperiences
                    ? 'border-cyan-300 bg-cyan-300/30'
                    : 'border-slate-600 bg-black',
                ].join(' ')}
              >
                <span
                  className={[
                    'absolute top-0.5 h-1.5 w-1.5 bg-current transition-transform',
                    useDeliveryAppExperiences ? 'translate-x-3.5' : 'translate-x-0.5',
                  ].join(' ')}
                />
              </span>
              Past experiences
            </button>

            <button
              type="button"
              onClick={handleRun}
              disabled={runDisabled}
              className="ml-auto border border-emerald-500 px-4 py-2 text-xs text-emerald-100 hover:bg-emerald-500/15 disabled:cursor-not-allowed disabled:opacity-30"
            >
              Run
            </button>

            {isRunning && (
              <button
                type="button"
                onClick={onStop}
                className="border border-red-500 px-4 py-2 text-xs text-red-100 hover:bg-red-500/15"
              >
                Stop
              </button>
            )}
          </div>
        </div>

        <div className="min-w-0">
          <div className="flex items-center justify-between gap-3 border-b border-slate-800 pb-2">
            <div className="min-w-0">
              <h3 className="truncate text-sm text-slate-200">
                {activeTitle || 'No scenario run yet'}
              </h3>
              {activePrompt && (
                <p className="mt-1 line-clamp-2 text-xs leading-4 text-slate-500">{activePrompt}</p>
              )}
            </div>
            <span className="shrink-0 text-xs text-slate-500">{responses.length}/30</span>
          </div>

          {voteSplit && (
            <div className="mt-4 border border-slate-800 bg-[#07090f] px-3 py-3">
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <div className="text-emerald-300">Yes {voteSplit.yes}</div>
                  <div className="mt-2 h-2 bg-slate-800">
                    <div className="h-2 bg-emerald-500" style={{ width: `${yesPct}%` }} />
                  </div>
                </div>
                <div>
                  <div className="text-red-300">No {voteSplit.no}</div>
                  <div className="mt-2 h-2 bg-slate-800">
                    <div className="h-2 bg-red-500" style={{ width: `${noPct}%` }} />
                  </div>
                </div>
              </div>
            </div>
          )}

          {shouldShowReasonSummary && (
            <div className="mt-3 grid gap-3 md:grid-cols-2">
              <ReasonList title="Top 3 Yes Reasons" reasons={topReasons.yes} />
              <ReasonList title="Top 3 No Reasons" reasons={topReasons.no} />
            </div>
          )}

          {summary?.most_interesting && (
            <div className="mt-3 border border-amber-500/40 bg-amber-500/10 px-3 py-3 text-sm">
              <div className="text-amber-100">Most interesting: {summary.most_interesting.agent_name}</div>
              <p className="mt-1 leading-5 text-slate-300">{summary.most_interesting.response}</p>
              {summary.most_interesting.why_interesting && (
                <p className="mt-1 text-xs leading-4 text-amber-200/80">
                  {summary.most_interesting.why_interesting}
                </p>
              )}
            </div>
          )}

          <div className="mt-3 max-h-[420px] min-h-40 overflow-y-auto border border-slate-800">
            {sortedResponses.length ? (
              sortedResponses.map(response => (
                <AgentResponseRow key={response.agent_id} response={response} />
              ))
            ) : (
              <div className="px-4 py-8 text-sm text-slate-600">
                Agent responses will stream here.
              </div>
            )}
          </div>
        </div>
      </div>

      {shouldShowVoteBreakdown && (
        <VoteBreakdownPanel
          mode={breakdownMode}
          onModeChange={setBreakdownMode}
          rows={voteBreakdown}
        />
      )}

      {shouldShowVoteBreakdown && responsesWithDeliveryExperiences.length > 0 && (
        <DeliveryExperiencePanel responses={responsesWithDeliveryExperiences} />
      )}
    </section>
  )
}

function DeliveryExperiencePanel({
  responses,
}: {
  responses: BehavioralScenarioResponse[]
}) {
  return (
    <div className="mt-4 border border-cyan-500/30 bg-[#050a0d] px-3 py-3">
      <div className="border-b border-slate-800 pb-2">
        <div className="text-sm text-slate-200">Delivery App Memories</div>
        <div className="mt-1 text-xs text-slate-500">
          Past experiences included in each agent&apos;s voting context
        </div>
      </div>

      <div className="mt-3 grid gap-2 md:grid-cols-2 xl:grid-cols-3">
        {responses.map(response => (
          <DeliveryExperienceItem key={response.agent_id} response={response} />
        ))}
      </div>
    </div>
  )
}

function DeliveryExperienceItem({ response }: { response: BehavioralScenarioResponse }) {
  const voteClass = response.vote === 'Yes'
    ? 'border-emerald-500/50 text-emerald-200'
    : response.vote === 'No'
      ? 'border-red-500/50 text-red-200'
      : 'border-slate-700 text-slate-400'

  return (
    <div className="border border-slate-800 bg-black/40 px-3 py-3">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 truncate text-sm text-slate-200">{response.agent_name}</div>
        {response.vote && (
          <div className={`shrink-0 border px-2 py-1 text-xs ${voteClass}`}>
            {response.vote}
          </div>
        )}
      </div>
      <ol className="mt-2 space-y-1 text-xs leading-4 text-slate-500">
        {(response.delivery_app_experiences ?? []).slice(0, 3).map((experience, index) => (
          <li key={`${response.agent_id}-experience-${index}`} className="grid grid-cols-[1rem_minmax(0,1fr)] gap-1">
            <span className="text-slate-700">{index + 1}.</span>
            <span>{experience}</span>
          </li>
        ))}
      </ol>
    </div>
  )
}

function VoteBreakdownPanel({
  mode,
  onModeChange,
  rows,
}: {
  mode: BreakdownMode
  onModeChange: (mode: BreakdownMode) => void
  rows: VoteBreakdownRow[]
}) {
  return (
    <div className="mt-4 border border-slate-800 bg-[#05070c] px-3 py-3">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-2">
        <div>
          <div className="text-sm text-slate-200">Yes/No Splits</div>
          <div className="mt-1 text-xs text-slate-500">
            Broken down by {mode === 'neighborhood' ? 'neighborhood' : 'household income bracket'}
          </div>
        </div>
        <div className="flex border border-slate-700 text-xs">
          <button
            type="button"
            onClick={() => onModeChange('neighborhood')}
            className={[
              'px-3 py-2',
              mode === 'neighborhood'
                ? 'bg-slate-200 text-black'
                : 'text-slate-400 hover:bg-slate-800',
            ].join(' ')}
          >
            Neighborhood
          </button>
          <button
            type="button"
            onClick={() => onModeChange('income')}
            className={[
              'border-l border-slate-700 px-3 py-2',
              mode === 'income'
                ? 'bg-slate-200 text-black'
                : 'text-slate-400 hover:bg-slate-800',
            ].join(' ')}
          >
            Income
          </button>
        </div>
      </div>

      {rows.length ? (
        <div className="mt-3 grid gap-2 md:grid-cols-2 xl:grid-cols-3">
          {rows.map(row => (
            <VoteBreakdownItem key={row.label} row={row} />
          ))}
        </div>
      ) : (
        <div className="px-1 py-6 text-sm text-slate-600">
          Vote breakdown will appear as Yes/No responses stream in.
        </div>
      )}
    </div>
  )
}

function VoteBreakdownItem({ row }: { row: VoteBreakdownRow }) {
  const yesPct = row.total ? Math.round((row.yes / row.total) * 100) : 0
  const noPct = row.total ? 100 - yesPct : 0

  return (
    <div className="border border-slate-800 bg-black/40 px-3 py-3">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 truncate text-sm text-slate-200" title={row.label}>
          {row.label}
        </div>
        <div className="shrink-0 text-xs text-slate-500">{row.total}</div>
      </div>
      <div className="mt-3 flex h-2 overflow-hidden bg-slate-800">
        <div className="bg-emerald-500" style={{ width: `${yesPct}%` }} />
        <div className="bg-red-500" style={{ width: `${noPct}%` }} />
      </div>
      <div className="mt-2 flex items-center justify-between text-xs">
        <span className="text-emerald-300">Yes {row.yes} ({yesPct}%)</span>
        <span className="text-red-300">No {row.no} ({noPct}%)</span>
      </div>
    </div>
  )
}

function ReasonList({
  title,
  reasons,
}: {
  title: string
  reasons: ReasonSummary[]
}) {
  const rows = reasons
    .filter(reason => reason.reason.trim())
    .slice(0, 3)
  const missingCount = 3 - rows.length

  return (
    <div className="border border-slate-800 bg-[#07090f] px-3 py-3">
      <div className="text-xs text-slate-500">{title}</div>
      <div className="mt-2 space-y-2">
        {rows.map((reason, index) => (
          <div key={reason.reason} className="text-sm leading-5" title={reason.example}>
            <span className="text-slate-600">{index + 1}. </span>
            <span className="text-slate-200">{reason.reason}</span>
            <span className="text-slate-600"> / </span>
            <span className="text-slate-500">{reason.count}</span>
          </div>
        ))}
        {rows.length === 0 && (
          <div className="text-sm leading-5 text-slate-600">No reasons yet.</div>
        )}
        {rows.length > 0 && missingCount > 0 && (
          <div className="text-xs leading-4 text-slate-600">
            {rows.length === 1
              ? 'Only 1 distinct reason found so far.'
              : `Only ${rows.length} distinct reasons found so far.`}
          </div>
        )}
      </div>
    </div>
  )
}

function buildTopReasons(responses: BehavioralScenarioResponse[], vote: 'Yes' | 'No'): ReasonSummary[] {
  const grouped = new Map<string, ReasonSummary>()

  responses.forEach(response => {
    if (response.vote !== vote) return
    const reason = response.reason || response.response || ''
    const label = reasonLabel(reason)
    const current = grouped.get(label) ?? { reason: label, count: 0, example: reason }
    current.count += 1
    if (!current.example && reason) current.example = reason
    grouped.set(label, current)
  })

  return [...grouped.values()]
    .sort((left, right) => right.count - left.count || left.reason.localeCompare(right.reason))
    .slice(0, 3)
}

function buildVoteBreakdown(
  responses: BehavioralScenarioResponse[],
  mode: BreakdownMode,
): VoteBreakdownRow[] {
  const grouped = new Map<string, VoteBreakdownRow>()

  responses.forEach(response => {
    if (response.vote !== 'Yes' && response.vote !== 'No') return

    const config = AGENT_CONFIG[response.agent_id]
    const label = mode === 'neighborhood'
      ? config?.neighborhood ?? 'Unknown neighborhood'
      : config?.incomeBracket ?? 'Unknown income'
    const current = grouped.get(label) ?? { label, yes: 0, no: 0, total: 0 }

    if (response.vote === 'Yes') current.yes += 1
    if (response.vote === 'No') current.no += 1
    current.total += 1
    grouped.set(label, current)
  })

  return [...grouped.values()].sort((left, right) => {
    if (mode === 'income') {
      return incomeBracketRank(left.label) - incomeBracketRank(right.label)
    }
    return right.total - left.total || left.label.localeCompare(right.label)
  })
}

function incomeBracketRank(label: string): number {
  const firstNumber = label.match(/\$([\d,]+)/)?.[1]
  if (!firstNumber) return Number.MAX_SAFE_INTEGER
  return Number(firstNumber.replaceAll(',', ''))
}

function reasonLabel(reason: string): string {
  const text = reason.toLowerCase()
  const categories: Array<[string[], string]> = [
    [['restaurant', 'small business', 'local business', 'merchant'], 'Protecting restaurants and local businesses'],
    [['fee', 'commission', '15%', 'cap', 'cut'], 'Limiting platform fees'],
    [['consumer', 'customer', 'cost', 'price', 'affordable', 'affordability'], 'Consumer affordability'],
    [['driver', 'worker', 'wage', 'job', 'pay', 'labor'], 'Worker pay and jobs'],
    [['regulation', 'government', 'market', 'interfere', 'unintended'], 'Concern about government regulation or side effects'],
    [['delivery', 'access', 'convenience', 'mobility', 'elder', 'disabled'], 'Delivery access and convenience'],
    [['profit', 'doordash', 'uber', 'platform', 'corporate'], 'Platform power and fairness'],
  ]
  return categories.find(([keywords]) => keywords.some(keyword => text.includes(keyword)))?.[1]
    ?? 'Practical household or neighborhood impact'
}

function AgentResponseRow({ response }: { response: BehavioralScenarioResponse }) {
  const config = AGENT_CONFIG[response.agent_id]
  const voteClass = response.vote === 'Yes'
    ? 'border-emerald-500/50 text-emerald-200'
    : response.vote === 'No'
      ? 'border-red-500/50 text-red-200'
      : 'border-slate-700 text-slate-400'

  return (
    <div className="grid min-h-24 grid-cols-[minmax(0,0.45fr)_minmax(0,1fr)] gap-3 border-b border-slate-800 px-3 py-3 last:border-b-0">
      <div className="min-w-0">
        <div className="truncate text-sm text-slate-200">{response.agent_name}</div>
        <div className="mt-1 text-xs leading-4 text-slate-500">{config?.identityInfo ?? response.agent_id}</div>
        {response.vote && (
          <div className={`mt-2 inline-flex border px-2 py-1 text-xs ${voteClass}`}>
            {response.vote}
          </div>
        )}
      </div>
      <p className="min-w-0 text-sm leading-5 text-slate-400">
        {response.response || response.reason}
      </p>
    </div>
  )
}
