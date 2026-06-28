export interface ZoneDef {
  x: number
  y: number
  w: number
  h: number
  label: string
  fillColor: number
  borderColor: number
  textColor: string
}

export interface AgentConfig {
  color: number
  homeZone: string
  identityInfo: string
  incomeBracket: string
  name: string
  neighborhood: string
}

export const CANVAS_W = 960
export const CANVAS_H = 520

export const ZONES: Record<string, ZoneDef> = {
  west_side: {
    x: 20, y: 54, w: 220, h: 112,
    label: 'WEST SIDE HOMES',
    fillColor: 0x102235, borderColor: 0x2b6f91, textColor: '#69b7d6',
  },
  north_side: {
    x: 20, y: 214, w: 220, h: 112,
    label: 'NORTH SIDE STREETS',
    fillColor: 0x241a34, borderColor: 0x7651a6, textColor: '#b79be8',
  },
  civic_market: {
    x: 370, y: 54, w: 220, h: 112,
    label: 'CIVIC + MARKET',
    fillColor: 0x10281d, borderColor: 0x2d8b5f, textColor: '#77d8a2',
  },
  neighborhood_work: {
    x: 370, y: 214, w: 220, h: 112,
    label: 'NEIGHBORHOOD WORK',
    fillColor: 0x2b2111, borderColor: 0x9b712c, textColor: '#e3b760',
  },
  transit_commons: {
    x: 330, y: 382, w: 300, h: 90,
    label: 'TRANSIT COMMONS',
    fillColor: 0x251515, borderColor: 0xa04444, textColor: '#ee8d8d',
  },
  southeast: {
    x: 720, y: 54, w: 220, h: 112,
    label: 'SOUTHEAST SF',
    fillColor: 0x13251c, borderColor: 0x4c9468, textColor: '#94dfad',
  },
  service_corridor: {
    x: 720, y: 214, w: 220, h: 112,
    label: 'SERVICE CORRIDOR',
    fillColor: 0x12242c, borderColor: 0x33859c, textColor: '#81d6ed',
  },
}

export function zoneCenterX(key: string): number {
  const z = ZONES[key]
  return z.x + z.w / 2
}

export function zoneCenterY(key: string): number {
  const z = ZONES[key]
  return z.y + z.h / 2
}

export const AGENT_CONFIG: Record<string, AgentConfig> = {
  'agent-1': { color: 0xd96c4a, homeZone: 'west_side', identityInfo: '40, Male, Data engineer, Sunset, Latino', incomeBracket: '$150,000 to $199,999', name: 'Mateo Rivera', neighborhood: 'Sunset' },
  'agent-2': { color: 0x5aa8d8, homeZone: 'southeast', identityInfo: '39, Male, Software developer, Excelsior, Korean American', incomeBracket: '$200,000 or more', name: 'James Park', neighborhood: 'Excelsior' },
  'agent-3': { color: 0xe0b64d, homeZone: 'civic_market', identityInfo: '39, Male, Network systems analyst, Mission, Chinese American', incomeBracket: '$200,000 or more', name: 'Wei Chen', neighborhood: 'Mission' },
  'agent-4': { color: 0xb884d8, homeZone: 'north_side', identityInfo: '24, Female, Software engineer, Nob Hill, Multiracial', incomeBracket: '$200,000 or more', name: 'Nadia Lewis', neighborhood: 'Nob Hill' },
  'agent-5': { color: 0xd86f9f, homeZone: 'civic_market', identityInfo: '35, Male, Facilities operations manager, Haight, Latina and multiracial', incomeBracket: '$150,000 to $199,999', name: 'Rosa Calderon', neighborhood: 'Haight' },
  'agent-6': { color: 0x7ed06f, homeZone: 'civic_market', identityInfo: '34, Male, Food service manager, Chinatown, Black', incomeBracket: '$100,000 to $124,999', name: 'Andre Brooks', neighborhood: 'Chinatown' },
  'agent-7': { color: 0xd4d66a, homeZone: 'west_side', identityInfo: '21, Male, Assistant manager, neighborhood retail, Richmond, Pacific Islander', incomeBracket: '$30,000 to $34,999', name: 'Tane Fale', neighborhood: 'Richmond' },
  'agent-8': { color: 0x7cc6b2, homeZone: 'southeast', identityInfo: '50, Male, Financial analyst, Portola, White', incomeBracket: '$200,000 or more', name: 'Connor Wallace', neighborhood: 'Portola' },
  'agent-9': { color: 0xce8d53, homeZone: 'neighborhood_work', identityInfo: '67, Male, Market research analyst, Mission, Pacific Islander and Latino', incomeBracket: '$10,000 to $14,999', name: 'Leilani Cruz', neighborhood: 'Mission' },
  'agent-10': { color: 0x78a8e8, homeZone: 'north_side', identityInfo: '30, Male, Social worker, North Beach, Latino and multiracial', incomeBracket: '$75,000 to $99,999', name: 'Diego Morales', neighborhood: 'North Beach' },
  'agent-11': { color: 0xaed66d, homeZone: 'west_side', identityInfo: '29, Male, Paralegal, Sunset, Indian American', incomeBracket: '$40,000 to $44,999', name: 'Arjun Patel', neighborhood: 'Sunset' },
  'agent-12': { color: 0xe08e68, homeZone: 'southeast', identityInfo: '64, Female, Elementary school teacher, Bayview, Native American and Latina', incomeBracket: '$150,000 to $199,999', name: 'Elena Yazzie', neighborhood: 'Bayview' },
  'agent-13': { color: 0x8fbaef, homeZone: 'civic_market', identityInfo: '71, Male, Writer and editor, Chinatown, Black', incomeBracket: '$150,000 to $199,999', name: 'Malik Johnson', neighborhood: 'Chinatown' },
  'agent-14': { color: 0xe0ce72, homeZone: 'southeast', identityInfo: '68, Male, Health technologist, Bayview, White', incomeBracket: '$25,000 to $29,999', name: 'Samuel Miller', neighborhood: 'Bayview' },
  'agent-15': { color: 0x77d0c2, homeZone: 'neighborhood_work', identityInfo: '47, Male, Medical records specialist, Mission, Vietnamese American', incomeBracket: '$60,000 to $74,999', name: 'Minh Nguyen', neighborhood: 'Mission' },
  'agent-16': { color: 0xd582c9, homeZone: 'west_side', identityInfo: '46, Female, Registered nurse, Sunset, Multiracial', incomeBracket: '$125,000 to $149,999', name: 'Avery Thompson', neighborhood: 'Sunset' },
  'agent-17': { color: 0xd28f64, homeZone: 'north_side', identityInfo: '41, Female, Food service worker, Castro, Native American', incomeBracket: '$60,000 to $74,999', name: 'Aiyana Begay', neighborhood: 'Castro' },
  'agent-18': { color: 0x6ecf82, homeZone: 'southeast', identityInfo: '50, Male, Protective service supervisor, Excelsior, Pacific Islander and Latino', incomeBracket: '$200,000 or more', name: 'Malia Kealoha', neighborhood: 'Excelsior' },
  'agent-19': { color: 0x9e95ea, homeZone: 'service_corridor', identityInfo: '57, Male, Healthcare support aide, Tenderloin, Latina and multiracial', incomeBracket: '$200,000 or more', name: 'Lucia Ortega', neighborhood: 'Tenderloin' },
  'agent-20': { color: 0xeab066, homeZone: 'west_side', identityInfo: '32, Male, Healthcare support aide, Richmond, Black', incomeBracket: '$125,000 to $149,999', name: 'Darius Carter', neighborhood: 'Richmond' },
  'agent-21': { color: 0x6fb4dd, homeZone: 'civic_market', identityInfo: '42, Male, Office clerk, Chinatown, Pacific Islander', incomeBracket: '$150,000 to $199,999', name: 'Tane Mahina', neighborhood: 'Chinatown' },
  'agent-22': { color: 0xd56c73, homeZone: 'neighborhood_work', identityInfo: '44, Female, Customer service representative, Mission, Native American', incomeBracket: '$100,000 to $124,999', name: 'Megan Yazzie', neighborhood: 'Mission' },
  'agent-23': { color: 0xa7cf68, homeZone: 'west_side', identityInfo: '50, Female, Retail salesperson, Sunset, Chinese American', incomeBracket: '$15,000 to $19,999', name: 'Grace Liu', neighborhood: 'Sunset' },
  'agent-24': { color: 0xc994e8, homeZone: 'southeast', identityInfo: '40, Male, Real estate sales agent, Portola, White', incomeBracket: '$200,000 or more', name: 'Peter Novak', neighborhood: 'Portola' },
  'agent-25': { color: 0x70d5a1, homeZone: 'west_side', identityInfo: '38, Male, Building maintenance worker, Richmond, Pacific Islander', incomeBracket: '$75,000 to $99,999', name: 'Keone Tui', neighborhood: 'Richmond' },
  'agent-26': { color: 0xd6bb5f, homeZone: 'neighborhood_work', identityInfo: '26, Male, Repair technician, Mission, Multiracial', incomeBracket: '$125,000 to $149,999', name: 'Samir Haddad', neighborhood: 'Mission' },
  'agent-27': { color: 0x7fceef, homeZone: 'north_side', identityInfo: '47, Female, Dispatch and logistics worker, North Beach, Black', incomeBracket: '$125,000 to $149,999', name: 'Monique Davis', neighborhood: 'North Beach' },
  'agent-28': { color: 0xe07755, homeZone: 'southeast', identityInfo: '36, Female, Production worker, Bayview, Latina and multiracial', incomeBracket: '$125,000 to $149,999', name: 'Isabel Torres', neighborhood: 'Bayview' },
  'agent-29': { color: 0x9bd88b, homeZone: 'civic_market', identityInfo: '72, Female, Retired office worker, Chinatown, Native American', incomeBracket: '$150,000 to $199,999', name: 'Carol Yazzie', neighborhood: 'Chinatown' },
  'agent-30': { color: 0xd78aae, homeZone: 'neighborhood_work', identityInfo: '73, Male, Retired service worker, Mission, Latino and Pacific Islander', incomeBracket: '$20,000 to $24,999', name: 'Rafael Santana', neighborhood: 'Mission' },
}

export function getAgentConfig(agentId: string, name?: string): AgentConfig {
  const fallbackZones = Object.keys(ZONES)
  const numeric = Number(agentId.replace('agent-', ''))
  const homeZone = fallbackZones[Number.isFinite(numeric) ? numeric % fallbackZones.length : 0]
  return AGENT_CONFIG[agentId] ?? {
    color: 0xb8c2d6,
    homeZone,
    identityInfo: 'identity unknown',
    incomeBracket: 'Unknown income',
    name: name ?? agentId,
    neighborhood: 'Unknown neighborhood',
  }
}

const ACTION_ZONES: Record<string, string> = {
  tweet: 'civic_market',
  statement: 'civic_market',
  email: 'neighborhood_work',
  phone_call: 'transit_commons',
  reflection: 'west_side',
  decision: 'neighborhood_work',
  announcement: 'civic_market',
  meeting: 'transit_commons',
}

export function getZoneForAction(agentId: string, actionType: string): string {
  return ACTION_ZONES[actionType] ?? getAgentConfig(agentId).homeZone
}
