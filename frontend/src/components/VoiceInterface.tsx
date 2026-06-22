import React, { useCallback, useEffect, useRef, useState } from 'react'
import {
  LiveKitRoom,
  useDataChannel,
  useLocalParticipant,
  useRemoteParticipants,
  useTracks,
  AudioTrack,
} from '@livekit/components-react'
import { Track, RoomEvent, DataPacket_Kind } from 'livekit-client'
import { Avatar } from './Avatar'
import { ToolStatusPanel } from './ToolStatusPanel'
import { CallSummary } from './CallSummary'
import type { CallState, CallSummary as CallSummaryType, ToolEvent } from '../lib/types'

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL ?? ''

export function VoiceInterface() {
  const [callState, setCallState] = useState<CallState>('idle')
  const [token, setToken] = useState('')
  const [serverUrl, setServerUrl] = useState('')
  const [roomName, setRoomName] = useState('')
  const [error, setError] = useState('')

  const startCall = useCallback(async () => {
    setCallState('connecting')
    setError('')
    try {
      const res = await fetch(`${BACKEND_URL}/token`)
      if (!res.ok) throw new Error(`Backend error: ${res.status}`)
      const data = await res.json()
      setToken(data.token)
      setServerUrl(data.url)
      setRoomName(data.room)
      setCallState('connected')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to connect')
      setCallState('idle')
    }
  }, [])

  const endCall = useCallback(() => {
    setCallState('ended')
  }, [])

  const resetCall = useCallback(() => {
    setToken('')
    setServerUrl('')
    setRoomName('')
    setCallState('idle')
  }, [])

  if (callState === 'idle') {
    return (
      <div className="landing">
        <div className="landing-card">
          <div className="landing-logo">
            <span className="logo-icon">🏥</span>
            <h1>Mykare Health</h1>
          </div>
          <p className="landing-subtitle">AI Front Desk — Book appointments instantly with your voice</p>
          {error && <p className="error-msg">{error}</p>}
          <button className="btn-primary btn-large" onClick={startCall}>
            <span>🎤</span> Start Voice Call
          </button>
          <p className="landing-hint">Click to speak with Aria, your AI health assistant</p>
        </div>
      </div>
    )
  }

  if (callState === 'connecting') {
    return (
      <div className="landing">
        <div className="landing-card">
          <div className="spinner" />
          <p>Connecting to Aria...</p>
        </div>
      </div>
    )
  }

  return (
    <LiveKitRoom
      token={token}
      serverUrl={serverUrl}
      connect={callState === 'connected'}
      audio={true}
      video={false}
      onDisconnected={resetCall}
    >
      <ActiveCall roomName={roomName} onEndCall={endCall} />
    </LiveKitRoom>
  )
}

interface ActiveCallProps {
  roomName: string
  onEndCall: () => void
}

function ActiveCall({ roomName, onEndCall }: ActiveCallProps) {
  const [toolEvents, setToolEvents] = useState<ToolEvent[]>([])
  const [summary, setSummary] = useState<CallSummaryType | null>(null)
  const [agentSpeaking, setAgentSpeaking] = useState(false)
  const [userSpeaking, setUserSpeaking] = useState(false)
  const eventIdRef = useRef(0)

  const remoteParticipants = useRemoteParticipants()
  const { localParticipant } = useLocalParticipant()

  const tracks = useTracks(
    [{ source: Track.Source.Microphone, withPlaceholder: true }],
    { onlySubscribed: false }
  )

  // Listen for data messages from the agent
  useDataChannel((msg) => {
    try {
      const payload = JSON.parse(new TextDecoder().decode(msg.payload)) as Record<string, unknown>

      if (payload.type === 'tool_call') {
        const id = `event-${eventIdRef.current++}`
        setToolEvents((prev) => {
          const existing = prev.findIndex(
            (e) => e.tool === payload.tool && e.status === 'calling'
          )
          if (existing >= 0 && payload.status !== 'calling') {
            const updated = [...prev]
            updated[existing] = {
              ...updated[existing],
              status: payload.status as 'done' | 'error',
              result: payload.result as Record<string, unknown> | undefined,
            }
            return updated
          }
          if (payload.status === 'calling') {
            return [
              ...prev,
              {
                id,
                tool: payload.tool as string,
                status: 'calling',
                timestamp: Date.now(),
              },
            ]
          }
          return prev
        })
      }

      if (payload.type === 'summary') {
        setSummary({
          summary: payload.summary as string,
          appointments: (payload.appointments as CallSummaryType['appointments']) ?? [],
          preferences: (payload.preferences as string) ?? '',
          timestamp: (payload.timestamp as string) ?? new Date().toISOString(),
        })
      }

      if (payload.type === 'speaking') {
        setAgentSpeaking(Boolean(payload.state))
      }
    } catch {
      // ignore malformed messages
    }
  })

  // Track remote participant speaking state via audio level
  useEffect(() => {
    const interval = setInterval(() => {
      for (const participant of remoteParticipants) {
        const audioTrack = participant.getTrackPublication(Track.Source.Microphone)
        if (audioTrack) {
          setAgentSpeaking(participant.isSpeaking)
        }
      }
      setUserSpeaking(localParticipant?.isSpeaking ?? false)
    }, 100)
    return () => clearInterval(interval)
  }, [remoteParticipants, localParticipant])

  return (
    <div className="call-layout">
      {/* Hidden audio tracks for remote participants */}
      {tracks
        .filter((t) => t.participant?.identity !== localParticipant?.identity)
        .map((track) =>
          track.publication?.track ? (
            <AudioTrack key={track.publication.trackSid} trackRef={track} />
          ) : null
        )}

      <div className="call-header">
        <span className="call-badge live">● LIVE</span>
        <span className="call-room">Room: {roomName}</span>
        <button className="btn-danger" onClick={onEndCall}>
          End Call
        </button>
      </div>

      <div className="call-body">
        <div className="call-left">
          <Avatar isSpeaking={agentSpeaking} isListening={userSpeaking} />
        </div>

        <div className="call-right">
          <ToolStatusPanel events={toolEvents} />
          {toolEvents.length === 0 && (
            <div className="waiting-hint">
              <p>Tool actions will appear here as Aria works on your request.</p>
            </div>
          )}
        </div>
      </div>

      {summary && (
        <CallSummary summary={summary} onClose={() => setSummary(null)} />
      )}
    </div>
  )
}
