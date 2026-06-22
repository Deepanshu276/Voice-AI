import React from 'react'
import { ToolEvent } from '../lib/types'

const TOOL_LABELS: Record<string, string> = {
  identify_user: 'Identifying user',
  fetch_slots: 'Fetching available slots',
  book_appointment: 'Booking appointment',
  retrieve_appointments: 'Retrieving appointments',
  cancel_appointment: 'Cancelling appointment',
  modify_appointment: 'Modifying appointment',
  end_conversation: 'Ending conversation',
}

const TOOL_ICONS: Record<string, string> = {
  identify_user: '👤',
  fetch_slots: '📅',
  book_appointment: '✅',
  retrieve_appointments: '📋',
  cancel_appointment: '❌',
  modify_appointment: '✏️',
  end_conversation: '📝',
}

interface ToolStatusPanelProps {
  events: ToolEvent[]
}

export function ToolStatusPanel({ events }: ToolStatusPanelProps) {
  if (events.length === 0) return null

  return (
    <div className="tool-panel">
      <h3 className="tool-panel-title">Actions</h3>
      <div className="tool-list">
        {events.map((event) => (
          <div key={event.id} className={`tool-item tool-${event.status}`}>
            <span className="tool-icon">{TOOL_ICONS[event.tool] ?? '⚙️'}</span>
            <div className="tool-info">
              <span className="tool-label">{TOOL_LABELS[event.tool] ?? event.tool}</span>
              {event.status === 'calling' && <span className="tool-status-badge calling">In progress...</span>}
              {event.status === 'done' && <span className="tool-status-badge done">Done ✓</span>}
              {event.status === 'error' && <span className="tool-status-badge error">Failed</span>}
              {event.result && event.status === 'done' && renderResult(event.tool, event.result)}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function renderResult(tool: string, result: Record<string, unknown>) {
  if (tool === 'book_appointment' && result.status === 'confirmed') {
    return (
      <span className="tool-detail">
        {String(result.date)} at {String(result.time)}
      </span>
    )
  }
  if (tool === 'fetch_slots' && Array.isArray(result.available_slots)) {
    return (
      <span className="tool-detail">
        {(result.available_slots as string[]).length} slots available
      </span>
    )
  }
  if (tool === 'retrieve_appointments') {
    return (
      <span className="tool-detail">
        {String(result.count ?? 0)} appointment(s) found
      </span>
    )
  }
  if (tool === 'cancel_appointment' && result.status === 'cancelled') {
    return <span className="tool-detail">Cancelled successfully</span>
  }
  if (tool === 'modify_appointment' && result.status === 'modified') {
    return (
      <span className="tool-detail">
        Moved to {String(result.new_date)} {String(result.new_time)}
      </span>
    )
  }
  if (tool === 'identify_user') {
    return (
      <span className="tool-detail">
        {result.status === 'existing_user' ? `Welcome back, ${String(result.name)}` : 'New patient'}
      </span>
    )
  }
  return null
}
