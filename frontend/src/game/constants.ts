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
  name: string
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
  'agent-1': { color: 0xd96c4a, homeZone: 'west_side', identityInfo: '40, Male, Data engineer, Sunset, Latino', name: 'Mateo Rivera' },
  'agent-2': { color: 0x5aa8d8, homeZone: 'southeast', identityInfo: '39, Male, Software developer, Excelsior, Korean American', name: 'James Park' },
  'agent-3': { color: 0xe0b64d, homeZone: 'civic_market', identityInfo: '39, Male, Network systems analyst, Mission, Chinese American', name: 'Wei Chen' },
  'agent-4': { color: 0xb884d8, homeZone: 'north_side', identityInfo: '24, Female, Software engineer, Nob Hill, Multiracial', name: 'Nadia Lewis' },
  'agent-5': { color: 0xd86f9f, homeZone: 'civic_market', identityInfo: '35, Male, Facilities operations manager, Haight, Latina and multiracial', name: 'Rosa Calderon' },
  'agent-6': { color: 0x7ed06f, homeZone: 'civic_market', identityInfo: '34, Male, Food service manager, Chinatown, Black', name: 'Andre Brooks' },
  'agent-7': { color: 0xd4d66a, homeZone: 'west_side', identityInfo: '21, Male, Assistant manager, neighborhood retail, Richmond, Pacific Islander', name: 'Tane Fale' },
  'agent-8': { color: 0x7cc6b2, homeZone: 'southeast', identityInfo: '50, Male, Financial analyst, Portola, White', name: 'Connor Wallace' },
  'agent-9': { color: 0xce8d53, homeZone: 'neighborhood_work', identityInfo: '67, Male, Market research analyst, Mission, Pacific Islander and Latino', name: 'Leilani Cruz' },
  'agent-10': { color: 0x78a8e8, homeZone: 'north_side', identityInfo: '30, Male, Social worker, North Beach, Latino and multiracial', name: 'Diego Morales' },
  'agent-11': { color: 0xaed66d, homeZone: 'west_side', identityInfo: '29, Male, Paralegal, Sunset, Indian American', name: 'Arjun Patel' },
  'agent-12': { color: 0xe08e68, homeZone: 'southeast', identityInfo: '64, Female, Elementary school teacher, Bayview, Native American and Latina', name: 'Elena Yazzie' },
  'agent-13': { color: 0x8fbaef, homeZone: 'civic_market', identityInfo: '71, Male, Writer and editor, Chinatown, Black', name: 'Malik Johnson' },
  'agent-14': { color: 0xe0ce72, homeZone: 'southeast', identityInfo: '68, Male, Health technologist, Bayview, White', name: 'Samuel Miller' },
  'agent-15': { color: 0x77d0c2, homeZone: 'neighborhood_work', identityInfo: '47, Male, Medical records specialist, Mission, Vietnamese American', name: 'Minh Nguyen' },
  'agent-16': { color: 0xd582c9, homeZone: 'west_side', identityInfo: '46, Female, Registered nurse, Sunset, Multiracial', name: 'Avery Thompson' },
  'agent-17': { color: 0xd28f64, homeZone: 'north_side', identityInfo: '41, Female, Food service worker, Castro, Native American', name: 'Aiyana Begay' },
  'agent-18': { color: 0x6ecf82, homeZone: 'southeast', identityInfo: '50, Male, Protective service supervisor, Excelsior, Pacific Islander and Latino', name: 'Malia Kealoha' },
  'agent-19': { color: 0x9e95ea, homeZone: 'service_corridor', identityInfo: '57, Male, Healthcare support aide, Tenderloin, Latina and multiracial', name: 'Lucia Ortega' },
  'agent-20': { color: 0xeab066, homeZone: 'west_side', identityInfo: '32, Male, Healthcare support aide, Richmond, Black', name: 'Darius Carter' },
  'agent-21': { color: 0x6fb4dd, homeZone: 'civic_market', identityInfo: '42, Male, Office clerk, Chinatown, Pacific Islander', name: 'Tane Mahina' },
  'agent-22': { color: 0xd56c73, homeZone: 'neighborhood_work', identityInfo: '44, Female, Customer service representative, Mission, Native American', name: 'Megan Yazzie' },
  'agent-23': { color: 0xa7cf68, homeZone: 'west_side', identityInfo: '50, Female, Retail salesperson, Sunset, Chinese American', name: 'Grace Liu' },
  'agent-24': { color: 0xc994e8, homeZone: 'southeast', identityInfo: '40, Male, Real estate sales agent, Portola, White', name: 'Peter Novak' },
  'agent-25': { color: 0x70d5a1, homeZone: 'west_side', identityInfo: '38, Male, Building maintenance worker, Richmond, Pacific Islander', name: 'Keone Tui' },
  'agent-26': { color: 0xd6bb5f, homeZone: 'neighborhood_work', identityInfo: '26, Male, Repair technician, Mission, Multiracial', name: 'Samir Haddad' },
  'agent-27': { color: 0x7fceef, homeZone: 'north_side', identityInfo: '47, Female, Dispatch and logistics worker, North Beach, Black', name: 'Monique Davis' },
  'agent-28': { color: 0xe07755, homeZone: 'southeast', identityInfo: '36, Female, Production worker, Bayview, Latina and multiracial', name: 'Isabel Torres' },
  'agent-29': { color: 0x9bd88b, homeZone: 'civic_market', identityInfo: '72, Female, Retired office worker, Chinatown, Native American', name: 'Carol Yazzie' },
  'agent-30': { color: 0xd78aae, homeZone: 'neighborhood_work', identityInfo: '73, Male, Retired service worker, Mission, Latino and Pacific Islander', name: 'Rafael Santana' },
}

export function getAgentConfig(agentId: string, name?: string): AgentConfig {
  const fallbackZones = Object.keys(ZONES)
  const numeric = Number(agentId.replace('agent-', ''))
  const homeZone = fallbackZones[Number.isFinite(numeric) ? numeric % fallbackZones.length : 0]
  return AGENT_CONFIG[agentId] ?? {
    color: 0xb8c2d6,
    homeZone,
    identityInfo: 'identity unknown',
    name: name ?? agentId,
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
