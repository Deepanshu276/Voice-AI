export type ToolStatus = 'calling' | 'done' | 'error'

export interface ToolEvent {
  id: string
  tool: string
  status: ToolStatus
  result?: Record<string, unknown>
  timestamp: number
}

export interface CallSummary {
  summary: string
  appointments: AppointmentItem[]
  preferences: string
  timestamp: string
}

export interface AppointmentItem {
  id?: number
  date: string
  time: string
  reason: string
  status?: string
}

export type CallState = 'idle' | 'connecting' | 'connected' | 'ended'
