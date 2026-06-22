import React from 'react'
import { CallSummary as CallSummaryType } from '../lib/types'

interface CallSummaryProps {
  summary: CallSummaryType
  onClose: () => void
}

export function CallSummary({ summary, onClose }: CallSummaryProps) {
  const formattedTime = summary.timestamp
    ? new Date(summary.timestamp).toLocaleString()
    : new Date().toLocaleString()

  return (
    <div className="summary-overlay">
      <div className="summary-modal">
        <div className="summary-header">
          <h2>Call Summary</h2>
          <span className="summary-timestamp">{formattedTime}</span>
        </div>

        <div className="summary-section">
          <h3>Conversation Summary</h3>
          <p className="summary-text">{summary.summary}</p>
        </div>

        {summary.appointments && summary.appointments.length > 0 && (
          <div className="summary-section">
            <h3>Appointments Booked</h3>
            <div className="summary-appointments">
              {summary.appointments.map((appt, i) => (
                <div key={i} className="summary-appt-card">
                  <span className="appt-icon">📅</span>
                  <div className="appt-details">
                    <strong>{appt.date}</strong> at <strong>{appt.time}</strong>
                    <br />
                    <span className="appt-reason">{appt.reason}</span>
                  </div>
                  <span className={`appt-status ${appt.status ?? 'confirmed'}`}>
                    {appt.status ?? 'Confirmed'}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {summary.preferences && (
          <div className="summary-section">
            <h3>Patient Preferences</h3>
            <p className="summary-text">{summary.preferences}</p>
          </div>
        )}

        <button className="summary-close-btn" onClick={onClose}>
          Close
        </button>
      </div>
    </div>
  )
}
