import { useEffect, useState, useRef } from 'react'
import { useWebSocket } from '../hooks/useWebSocket'
import { getFlag } from '../utils/languages'
import './CallOverlay.css'

export default function CallOverlay({ sessionId, targetLang, profile, onSessionEnd }) {
  const [caption, setCaption] = useState('')
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [warning, setWarning] = useState(null)
  const [phraseCount, setPhraseCount] = useState(0)
  const [showExitModal, setShowExitModal] = useState(false)
  const startTime = useRef(Date.now())
  const sentInit = useRef(false)
  const historyEndRef = useRef(null)

  const { connected, send } = useWebSocket(
    `ws://localhost:8000/ws/transcribe/${sessionId}`,
    (data) => {
      if (data.type === 'caption') {
        setCaption(data.translated)
        setHistory((prev) => [...prev, {
          original: data.original,
          translated: data.translated,
          timestamp: data.timestamp,
        }])
        setPhraseCount((n) => n + 1)
        setLoading(false)
        setWarning(null)
      } else if (data.type === 'warning') {
        setWarning(data.message)
      } else if (data.type === 'error') {
        setWarning(data.message)
        setLoading(false)
      }
    }
  )

  useEffect(() => {
    historyEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [history])

  useEffect(() => {
    if (connected && !sentInit.current) {
      sentInit.current = true
      send({ target_lang: targetLang, profile_id: profile?.id ?? null })
    }
  }, [connected, send, targetLang, profile])

  const handlePopup = () => {
    const params = new URLSearchParams({
      popup: '1',
      session: sessionId,
      lang: targetLang,
      ...(profile?.id ? { profile: profile.id } : {}),
    })
    window.open(
      `${window.location.origin}/?${params}`,
      'meeting-translator-popup',
      'width=700,height=56,resizable=yes,scrollbars=no,toolbar=no,menubar=no,location=no,status=no,alwaysOnTop=yes'
    )
  }

  const handleExit = () => {
    const duration = Math.round((Date.now() - startTime.current) / 60000)
    onSessionEnd({
      duration_minutes: duration,
      phrases_translated: phraseCount,
      target_language: targetLang,
      profile_used: profile,
    })
  }

  return (
    <div className="co-page">
      <div className="co-bar">
        <div className="co-left">
          <span className="co-flag">{getFlag(targetLang)}</span>
          {loading && <span className="co-spinner" />}
        </div>

        <p className="co-caption">{caption || '🎙️ Aguardando áudio...'}</p>

        <button className="co-popup-btn" onClick={handlePopup} aria-label="Abrir em janela flutuante">⬆︎</button>
        <button className="co-exit-btn" onClick={() => setShowExitModal(true)} aria-label="Encerrar sessão">✕</button>
      </div>

      {warning && (
        <div className="co-warning">
          ⚠️ {warning}
        </div>
      )}

      {history.length > 0 && (
        <div className="co-history">
          {history.map((entry, i) => (
            <div key={i} className="co-history-entry">
              <p className="co-history-translated">{entry.translated}</p>
              {entry.original !== entry.translated && (
                <p className="co-history-original">{entry.original}</p>
              )}
            </div>
          ))}
          <div ref={historyEndRef} />
        </div>
      )}

      <div className="co-stats">
        <span>{phraseCount} {phraseCount === 1 ? 'frase' : 'frases'} traduzidas</span>
        {profile && <span>👤 {profile.speaker_name}</span>}
        {connected ? <span className="co-dot co-dot--on" /> : <span className="co-dot co-dot--off" />}
      </div>

      {showExitModal && (
        <div className="co-overlay">
          <div className="co-modal">
            <h2>Encerrar tradução?</h2>
            <p>{phraseCount} {phraseCount === 1 ? 'frase traduzida' : 'frases traduzidas'}</p>
            <div className="co-modal-btns">
              <button className="co-modal-continue" onClick={() => setShowExitModal(false)}>
                Continuar
              </button>
              <button className="co-modal-end" onClick={handleExit}>
                Encerrar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
