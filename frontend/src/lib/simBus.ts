import mitt from 'mitt'

export interface BehavioralScenarioResponse {
  agent_id: string
  agent_name: string
  response: string
  vote?: 'Yes' | 'No'
  reason?: string
  delivery_app_experiences?: string[]
  neighborhood?: string
  neighborhood_votes_seen?: { yes: number; no: number; total: number }
}

export interface BehavioralScenarioSummary {
  total?: number
  vote_split?: { yes: number; no: number; total: number }
  top_reasons?: {
    yes: Array<{ reason: string; count: number; example: string }>
    no: Array<{ reason: string; count: number; example: string }>
  }
  most_interesting?: BehavioralScenarioResponse & { why_interesting?: string }
}

export type SimEvent =
  | { type: 'simulation_started' }
  | { type: 'simulation_stopped'; ticks_run: number }
  | { type: 'tick_started'; step: number; current_time: string }
  | { type: 'tick_done'; step: number; current_time: string }
  | { type: 'world_event'; content: string }
  | { type: 'agent_thinking'; agent_id: string; agent_name: string }
  | { type: 'agent_action'; agent_id: string; agent_name: string; action_type: string; inner_monologue: string; public_action: string; emotional_state: string; memory_entry: string }
  | { type: 'agent_observed'; agent_id: string; agent_name: string; zone: string; summary: string }
  | { type: 'agent_planned'; agent_id: string; agent_name: string; action_type: string; inner_monologue: string; public_action: string; emotional_state: string }
  | { type: 'agent_moved'; agent_id: string; agent_name: string; from_zone: string; to_zone: string; activity: string; emotional_state: string }
  | { type: 'encounter_start'; encounter_id?: string; topic: string; zone?: string; participants: Array<{ agent_id: string; name: string }> }
  | { type: 'agent_utterance'; encounter_id?: string; exchange: number; speaker_id: string; speaker_name: string; internal_state: string; utterance: string }
  | { type: 'encounter_end'; encounter_id: string; participants: Array<{ agent_id: string; name: string }> }
  | { type: 'behavioral_scenario_started'; experiment_id: string; title: string; prompt: string; response_mode: 'yes_no_reason' | 'freeform'; use_delivery_app_experiences?: boolean; use_social_influence?: boolean }
  | ({ type: 'behavioral_agent_response'; experiment_id: string } & BehavioralScenarioResponse)
  | { type: 'behavioral_scenario_summary'; experiment_id: string; summary: BehavioralScenarioSummary }
  | { type: 'memory_saved'; agent_id: string; agent_name: string; entry: string }
  | { type: 'reflection_saved'; agent_id: string; agent_name: string; entry: string }
  | { type: 'done' }
  | { type: 'error'; message: string }

type Events = { sim: SimEvent }

export const simBus = mitt<Events>()
