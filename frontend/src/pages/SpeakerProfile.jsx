import { useState } from 'react'
import './SpeakerProfile.css'

const STEPS = [
  'Baixando áudios...',
  'Transcrevendo com Whisper...',
  'Extraindo vocabulário...',
  'Construindo glossário...',
  'Salvando perfil...',
]

export default function SpeakerProfile({ onSkip, onComplete }) {
  const [screen, setScreen] = useState('input')
  const [speakerName, setSpeakerName] = useState('')
  const [urlInput, setUrlInput] = useState('')
  const [urls, setUrls] = useState([])
  const [stepIdx, setStepIdx] = useState(0)
  const [profile, setProfile] = useState(null)
  const [error, setError] = useState(null)

  const addUrl = () => {
    const trimmed = urlInput.trim()
    if (trimmed && !urls.includes(trimmed)) {
      setUrls((u) => [...u, trimmed])
      setUrlInput('')
    }
  }

  const removeUrl = (url) => setUrls((u) => u.filter((x) => x !== url))

  const handleAnalyze = async () => {
    if (!urls.length) return
    setScreen('processing')
    setStepIdx(0)

    const tick = setInterval(() => {
      setStepIdx((i) => Math.min(i + 1, STEPS.length - 1))
    }, 2000)

    try {
      const res = await fetch('http://localhost:8000/api/speaker-profiles', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ urls, speaker_name: speakerName || 'Perfil' }),
      })
      clearInterval(tick)
      if (!res.ok) throw new Error('Falha ao criar perfil')
      const data = await res.json()
      setProfile(data)
      setScreen('result')
    } catch (e) {
      clearInterval(tick)
      setError(e.message)
      setScreen('input')
    }
  }

  if (screen === 'input') {
    return (
      <div className="sp-page">
        <div className="sp-card">
          <h2 className="sp-title">Perfil do Palestrante</h2>
          <p className="sp-subtitle">
            Adicione vídeos do YouTube para criar um perfil de vocabulário personalizado.
          </p>

          <input
            className="sp-input"
            placeholder="Nome do perfil (opcional)"
            value={speakerName}
            onChange={(e) => setSpeakerName(e.target.value)}
          />

          <div className="sp-url-row">
            <input
              className="sp-input sp-url-input"
              placeholder="URL do YouTube"
              value={urlInput}
              onChange={(e) => setUrlInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && addUrl()}
            />
            <button className="sp-btn-add" onClick={addUrl}>Adicionar</button>
          </div>

          {error && <p className="sp-error">{error}</p>}

          {urls.length > 0 && (
            <ul className="sp-url-list">
              {urls.map((u) => (
                <li key={u} className="sp-url-item">
                  <span className="sp-url-text">{u}</span>
                  <button className="sp-btn-remove" onClick={() => removeUrl(u)} aria-label={`Remover ${u}`}>✕</button>
                </li>
              ))}
            </ul>
          )}

          <div className="sp-actions">
            <button
              className="sp-btn-primary"
              disabled={!urls.length}
              onClick={handleAnalyze}
            >
              Analisar e criar perfil
            </button>
            <button className="sp-btn-skip" onClick={onSkip}>
              Pular →
            </button>
          </div>
        </div>
      </div>
    )
  }

  if (screen === 'processing') {
    return (
      <div className="sp-page">
        <div className="sp-card sp-card--center">
          <div className="sp-spinner" />
          <h2 className="sp-title">Analisando vídeos...</h2>
          <div className="sp-steps">
            {STEPS.map((step, i) => (
              <div
                key={step}
                className={`sp-step ${i <= stepIdx ? 'sp-step--active' : ''} ${i < stepIdx ? 'sp-step--done' : ''}`}
              >
                <span className="sp-step-dot">{i < stepIdx ? '✓' : i === stepIdx ? '●' : '○'}</span>
                <span>{step}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  // result screen
  return (
    <div className="sp-page">
      <div className="sp-card">
        <div className="sp-success-banner">✓ Perfil criado com sucesso</div>

        <div className="sp-avatar">{profile?.speaker_name?.slice(0, 2).toUpperCase() ?? 'SP'}</div>
        <h2 className="sp-title">{profile?.speaker_name}</h2>

        <div className="sp-stats">
          <div className="sp-stat">
            <span className="sp-stat-value">{profile?.stats?.unique_words ?? 0}</span>
            <span className="sp-stat-label">palavras únicas</span>
          </div>
          <div className="sp-stat">
            <span className="sp-stat-value">{profile?.stats?.accent?.toUpperCase() ?? '–'}</span>
            <span className="sp-stat-label">sotaque detectado</span>
          </div>
          <div className="sp-stat">
            <span className="sp-stat-value">{profile?.stats?.duration_minutes?.toFixed(1) ?? '0'} min</span>
            <span className="sp-stat-label">de áudio analisado</span>
          </div>
        </div>

        {profile?.vocabulary?.length > 0 && (
          <div className="sp-vocab">
            <p className="sp-vocab-label">Vocabulário detectado</p>
            <div className="sp-vocab-pills">
              {profile.vocabulary.slice(0, 12).map((w) => (
                <span key={w} className="sp-pill">{w}</span>
              ))}
            </div>
          </div>
        )}

        <div className="sp-actions">
          <button className="sp-btn-primary" onClick={() => onComplete(profile)}>
            Usar perfil e iniciar
          </button>
          <button className="sp-btn-skip" onClick={onSkip}>
            Iniciar sem perfil →
          </button>
        </div>
      </div>
    </div>
  )
}
