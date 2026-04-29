import { useEffect, useRef, useState } from 'react'
import { useWebSocket } from '../hooks/useWebSocket'
import { getFlag } from '../utils/languages'
import './PopupOverlay.css'

export default function PopupOverlay() {
  const params = new URLSearchParams(window.location.search)
  const sessionId = params.get('session')
  const targetLang = params.get('lang') || 'pt'
  const profileId = params.get('profile') || null

  const [caption, setCaption] = useState('')
  const [connected, setConnectedState] = useState(false)
  const sentInit = useRef(false)

  const { connected: wsConnected, send } = useWebSocket(
    `ws://localhost:8000/ws/transcribe/${sessionId}`,
    (data) => {
      if (data.type === 'caption') setCaption(data.translated)
    }
  )

  useEffect(() => {
    setConnectedState(wsConnected)
    if (wsConnected && !sentInit.current) {
      sentInit.current = true
      send({ target_lang: targetLang, profile_id: profileId })
    }
  }, [wsConnected, send, targetLang, profileId])

  return (
    <div className="po-bar">
      <span className="po-flag">{getFlag(targetLang)}</span>
      <p className="po-caption">{caption || '🎙️ Aguardando...'}</p>
      <span className={`po-dot ${wsConnected ? 'po-dot--on' : 'po-dot--off'}`} />
    </div>
  )
}
