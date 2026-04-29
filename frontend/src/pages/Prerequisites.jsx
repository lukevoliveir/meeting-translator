import { useEffect, useState } from 'react'
import './Prerequisites.css'

const BACKEND_URL = 'http://localhost:8000'

const METHOD_LABELS = {
  wasapi_native:        'WASAPI Loopback nativo',
  stereo_mix:           'Stereo Mix',
  vb_cable:             'VB-Audio CABLE',
  voicemeeter:          'VoiceMeeter',
  blackhole:            'BlackHole',
  pulse_monitor:        'PulseAudio Monitor',
  keyword:              'Dispositivo loopback',
  manual:               'Configurado manualmente',
  microphone_fallback:  'Microfone (fallback)',
}

export default function Prerequisites({ onReady }) {
  const [status, setStatus]         = useState('checking') // checking | ready | missing | error
  const [systemInfo, setSystemInfo] = useState(null)
  const [audioInfo, setAudioInfo]   = useState(null)       // /audio/devices payload
  const [showPicker, setShowPicker] = useState(false)
  const [switching, setSwitching]   = useState(false)
  const [switchError, setSwitchError] = useState(null)

  useEffect(() => { check() }, [])

  async function check() {
    setStatus('checking')
    setSwitchError(null)
    try {
      const [sysRes, audioRes] = await Promise.all([
        fetch(`${BACKEND_URL}/api/system/check`),
        fetch(`${BACKEND_URL}/audio/devices`),
      ])
      if (!sysRes.ok) throw new Error('Backend unreachable')

      const sys   = await sysRes.json()
      const audio = audioRes.ok ? await audioRes.json() : null

      setSystemInfo(sys)
      setAudioInfo(audio)
      setStatus(sys.loopback_found ? 'ready' : 'missing')
    } catch {
      setStatus('error')
    }
  }

  async function switchDevice(deviceName) {
    setSwitching(true)
    setSwitchError(null)
    try {
      const res = await fetch(`${BACKEND_URL}/audio/device`, {
        method:  'PUT',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ name: deviceName }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Erro ao trocar dispositivo')
      setShowPicker(false)
      await check()
    } catch (err) {
      setSwitchError(err.message)
    } finally {
      setSwitching(false)
    }
  }

  const osLabel = { Darwin: 'macOS', Windows: 'Windows', Linux: 'Linux' }

  const candidates    = audioInfo?.candidates ?? []
  const currentDevice = audioInfo?.current_device ?? null
  const methodLabel   = currentDevice ? (METHOD_LABELS[currentDevice.method] ?? currentDevice.method) : null
  const isWasapi      = currentDevice?.method === 'wasapi_native'
  const isFallback    = currentDevice?.method === 'microphone_fallback'

  return (
    <div className="pr-page">
      <div className="pr-card">

        <div className="pr-icon">
          {status === 'checking' && '⏳'}
          {status === 'ready'    && (isFallback ? '⚠️' : '✅')}
          {status === 'missing'  && '⚠️'}
          {status === 'error'    && '❌'}
        </div>

        <h1 className="pr-title">Meeting Translator</h1>
        <p className="pr-subtitle">Verificação de pré-requisitos</p>

        {/* Checklist */}
        <div className="pr-checklist">
          {/* Backend */}
          <div className={`pr-item ${status !== 'error' ? 'pr-item--ok' : 'pr-item--fail'}`}>
            <span className="pr-dot" />
            <span className="pr-item-text">
              Backend rodando
              {status === 'error' && <span className="pr-hint"> — inicie o servidor Python</span>}
            </span>
          </div>

          {/* OS */}
          {systemInfo && (
            <div className="pr-item pr-item--ok">
              <span className="pr-dot" />
              <span className="pr-item-text">
                Sistema: <strong>{osLabel[systemInfo.os] ?? systemInfo.os}</strong>
              </span>
            </div>
          )}

          {/* Audio device */}
          <div className={`pr-item ${
            status === 'ready'   ? (isFallback ? 'pr-item--warn' : 'pr-item--ok') :
            status === 'missing' ? 'pr-item--fail' :
            'pr-item--idle'
          }`}>
            <span className="pr-dot" />
            <span className="pr-item-text">
              {status === 'ready' && currentDevice && (
                <>
                  Áudio: <strong>{currentDevice.name}</strong>
                  <span className="pr-badge">{methodLabel}</span>
                </>
              )}
              {status === 'missing' && <>Nenhum dispositivo de loopback encontrado</>}
              {(status === 'checking' || status === 'error') && <>Dispositivo de áudio</>}
            </span>
          </div>
        </div>

        {/* WASAPI native badge */}
        {status === 'ready' && isWasapi && (
          <div className="pr-info-box pr-info-box--success">
            Usando WASAPI Loopback nativo — nenhum driver adicional necessário.
          </div>
        )}

        {/* Audio routing instructions for BlackHole / VB-Cable */}
        {status === 'ready' && !isFallback && currentDevice && (
          <div className="pr-info-box pr-info-box--warn">
            <strong>⚙️ Configure a saída de áudio da call:</strong>
            {currentDevice.method === 'blackhole' && (
              <p style={{ margin: '0.4rem 0 0' }}>
                No Google Meet/Zoom → ícone de áudio →{' '}
                <strong>selecione {currentDevice.name} como saída</strong>.
                Para continuar ouvindo, crie um <em>Multi-Output Device</em> no Audio MIDI Setup
                combinando {currentDevice.name} + fones.
              </p>
            )}
            {(currentDevice.method === 'vb_cable' || currentDevice.method === 'wasapi_native') && (
              <p style={{ margin: '0.4rem 0 0' }}>
                No Google Meet/Zoom → ícone de áudio →{' '}
                <strong>selecione CABLE Input (VB-Audio Virtual Cable) como saída</strong>.
              </p>
            )}
          </div>
        )}

        {/* Microphone fallback warning (macOS without BlackHole) */}
        {status === 'ready' && isFallback && (
          <div className="pr-info-box pr-info-box--warn">
            Usando microfone como fallback. Para capturar áudio do sistema instale o{' '}
            <a href="https://existential.audio/blackhole/" target="_blank" rel="noreferrer">
              BlackHole
            </a>.
          </div>
        )}

        {/* Device switcher */}
        {status === 'ready' && candidates.length > 1 && (
          <button className="pr-btn-ghost" onClick={() => { setShowPicker(v => !v); setSwitchError(null) }}>
            {showPicker ? 'Fechar' : 'Trocar dispositivo'}
          </button>
        )}

        {/* Device picker */}
        {showPicker && (
          <div className="pr-device-list">
            {candidates.map((c) => {
              const isActive = currentDevice?.name === c.name
              return (
                <button
                  key={`${c.backend}-${c.device_id}`}
                  className={`pr-device-item ${isActive ? 'pr-device-item--active' : ''}`}
                  onClick={() => !isActive && switchDevice(c.name)}
                  disabled={switching || isActive}
                >
                  <span className="pr-device-name">{c.name}</span>
                  <span className="pr-device-meta">
                    {METHOD_LABELS[c.method] ?? c.method}
                    {c.recommended && <span className="pr-badge pr-badge--green">recomendado</span>}
                  </span>
                </button>
              )
            })}
            {switchError && <p className="pr-switch-error">{switchError}</p>}
          </div>
        )}

        {/* Missing device instructions */}
        {status === 'missing' && systemInfo && (
          <div className="pr-alert">
            <p className="pr-alert-text">
              Nenhum dispositivo de loopback detectado. Escolha uma opção:
            </p>

            {/* Option 1: WASAPI (Windows only, pyaudiowpatch not installed) */}
            {systemInfo.os === 'Windows' && !audioInfo?.wasapi_native_available && (
              <div className="pr-option">
                <strong>Opção 1 — WASAPI nativo (recomendado, sem instalar drivers)</strong>
                <code className="pr-code">pip install pyaudiowpatch</code>
                <p className="pr-alert-hint">Reinicie o backend após instalar.</p>
              </div>
            )}

            {/* Option 2: VB-Cable */}
            {systemInfo.os === 'Windows' && (
              <div className="pr-option">
                <strong>Opção 2 — VB-Audio Virtual Cable (driver gratuito)</strong>
                <a
                  className="pr-download-btn"
                  href="https://vb-audio.com/Cable/"
                  target="_blank"
                  rel="noreferrer"
                >
                  Baixar VB-Audio CABLE →
                </a>
                <p className="pr-alert-hint">
                  Após instalar, defina "CABLE Output" como dispositivo de gravação padrão
                  e clique em "Verificar novamente".
                </p>
              </div>
            )}

            {/* Option 3: Stereo Mix */}
            {systemInfo.os === 'Windows' && (
              <div className="pr-option">
                <strong>Opção 3 — Stereo Mix (se sua placa de som suportar)</strong>
                <p className="pr-alert-hint">
                  Painel de Controle → Som → Gravação → clique com botão direito →
                  "Mostrar dispositivos desabilitados" → habilite "Stereo Mix".
                </p>
              </div>
            )}

            {/* macOS */}
            {systemInfo.os === 'Darwin' && (
              <div className="pr-option">
                <strong>Instale o BlackHole para capturar o áudio do sistema:</strong>
                <a
                  className="pr-download-btn"
                  href="https://existential.audio/blackhole/"
                  target="_blank"
                  rel="noreferrer"
                >
                  Baixar BlackHole →
                </a>
              </div>
            )}

            {/* Available devices list */}
            {candidates.length > 0 && (
              <div className="pr-device-list pr-device-list--inline">
                <p className="pr-alert-hint" style={{ marginBottom: '0.4rem' }}>
                  Dispositivos detectados que podem funcionar:
                </p>
                {candidates.map((c) => (
                  <button
                    key={`${c.backend}-${c.device_id}`}
                    className="pr-device-item"
                    onClick={() => switchDevice(c.name)}
                    disabled={switching}
                  >
                    <span className="pr-device-name">{c.name}</span>
                    <span className="pr-device-meta">{METHOD_LABELS[c.method] ?? c.method}</span>
                  </button>
                ))}
                {switchError && <p className="pr-switch-error">{switchError}</p>}
              </div>
            )}
          </div>
        )}

        {/* Backend error */}
        {status === 'error' && (
          <div className="pr-alert pr-alert--error">
            <p className="pr-alert-text">
              Não foi possível conectar ao backend:
            </p>
            <code className="pr-code">cd backend &amp;&amp; python main.py</code>
          </div>
        )}

        {/* Actions */}
        <div className="pr-actions">
          {status === 'ready' && !isFallback && (
            <button className="pr-btn-primary" onClick={onReady}>
              Continuar →
            </button>
          )}
          {status === 'ready' && isFallback && (
            <>
              <button className="pr-btn-secondary" onClick={onReady}>
                Continuar mesmo assim
              </button>
            </>
          )}
          {(status === 'missing' || status === 'error') && (
            <button className="pr-btn-secondary" onClick={check}>
              Verificar novamente
            </button>
          )}
          {status === 'checking' && <div className="pr-spinner" />}
        </div>

      </div>
    </div>
  )
}
