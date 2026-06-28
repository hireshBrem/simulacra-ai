import mitt from 'mitt'

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
  | { type: 'memory_saved'; agent_id: string; agent_name: string; entry: string }
  | { type: 'reflection_saved'; agent_id: string; agent_name: string; entry: string }
  | { type: 'done' }
  | { type: 'error'; message: string }

type Events = { sim: SimEvent }

export const simBus = mitt<Events>()
