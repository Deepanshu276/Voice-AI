import React from 'react'

interface AvatarProps {
  isSpeaking: boolean
  isListening: boolean
}

export function Avatar({ isSpeaking, isListening }: AvatarProps) {
  return (
    <div className="avatar-container">
      <div className={`avatar-ring ring-3 ${isSpeaking ? 'speaking' : ''}`} />
      <div className={`avatar-ring ring-2 ${isSpeaking ? 'speaking' : ''}`} />
      <div className={`avatar-ring ring-1 ${isSpeaking ? 'speaking' : ''}`} />
      <div className={`avatar-core ${isListening ? 'listening' : ''} ${isSpeaking ? 'speaking' : ''}`}>
        <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg" className="avatar-icon">
          <circle cx="24" cy="16" r="8" fill="currentColor" opacity="0.9" />
          <path
            d="M8 40c0-8.837 7.163-16 16-16s16 7.163 16 16"
            stroke="currentColor"
            strokeWidth="3"
            strokeLinecap="round"
            fill="none"
            opacity="0.9"
          />
          <path
            d="M24 34v-4M20 38h8"
            stroke="currentColor"
            strokeWidth="2.5"
            strokeLinecap="round"
            opacity="0.7"
          />
        </svg>
        {isSpeaking && (
          <div className="waveform">
            {[...Array(5)].map((_, i) => (
              <span key={i} className="wave-bar" style={{ animationDelay: `${i * 0.1}s` }} />
            ))}
          </div>
        )}
      </div>
      <p className="avatar-name">Aria</p>
      <p className="avatar-status">
        {isSpeaking ? 'Speaking...' : isListening ? 'Listening...' : 'Mykare Health AI'}
      </p>
    </div>
  )
}
