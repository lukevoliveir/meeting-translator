import { useEffect, useState } from 'react'
import './Prerequisites.css'

const BACKEND_URL = 'http://localhost:8000'

export default function Prerequisites({ onReady }) {
  const [status, setStatus] = useState('checking') // checking | ready | missing | error
  const [systemInfo, setSystemInfo] = useState(null)

  useEffect(() => {
    check()
  }, [])

  async function check() {
    setStatus('checking')
    try {
      const res = await fetch(`${BACKEND_URL}/api/system/check`)
      if (!res.ok) throw new Error('Backend unreachable')
      const data = await res.json()
      setSystemInfo(data)
      setStatus(data.virtual_device_found ? 'ready' : 'missing')
    } catch {
      setStatus('error')
    }
  }

  const osLabel = {
    Darwin:  'macOS',
    Windows: 'Windows',
    Linux:   'Linux',
  }

  return (
    <div className="pr-page">
      <div className="pr-card">

        <div className="pr-icon">
          {status === 'checking' && '⏳'}
          {status === 'ready'    && '✅'}
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
                Sistema operacional: <strong>{osLabel[systemInfo.os] ?? systemInfo.os}</strong>
              </span>
            </div>
          )}

          {/* Virtual audio driver */}
          <div className={`pr-item ${
            status === 'ready'   ? 'pr-item--ok'   :
            status === 'missing' ? 'pr-item--fail'  :
            status === 'error'   ? 'pr-item--idle'  : 'pr-item--idle'
          }`}>
            <span className="pr-dot" />
            <span className="pr-item-text">
              {status === 'ready' && (
                <>Driver de áudio virtual: <strong>{systemInfo.virtual_device_name}</strong></>
              )}
              {status === 'missing' && (
                <>{systemInfo.driver_name} não encontrado</>
              )}
              {(status === 'checking' || status === 'error') && (
                <>Driver de áudio virtual</>
              )}
            </span>
          </div>
        </div>

        {/* Missing driver instructions */}
        {status === 'missing' && systemInfo && (
          <div className="pr-alert">
            <p className="pr-alert-text">
              Para capturar o áudio da reunião, instale o <strong>{systemInfo.driver_name}</strong>:
            </p>
            <a
              className="pr-download-btn"
              href={systemInfo.driver_download_url}
              target="_blank"
              rel="noreferrer"
            >
              Baixar {systemInfo.driver_name} →
            </a>
            <p className="pr-alert-hint">
              Após instalar, reinicie o computador e clique em "Verificar novamente".
            </p>
          </div>
        )}

        {/* Backend error */}
        {status === 'error' && (
          <div className="pr-alert pr-alert--error">
            <p className="pr-alert-text">
              Não foi possível conectar ao backend. Certifique-se que o servidor está rodando:
            </p>
            <code className="pr-code">cd backend &amp;&amp; python main.py</code>
          </div>
        )}

        {/* Actions */}
        <div className="pr-actions">
          {status === 'ready' && (
            <button className="pr-btn-primary" onClick={onReady}>
              Continuar →
            </button>
          )}
          {(status === 'missing' || status === 'error') && (
            <button className="pr-btn-secondary" onClick={check}>
              Verificar novamente
            </button>
          )}
          {status === 'checking' && (
            <div className="pr-spinner" />
          )}
        </div>

      </div>
    </div>
  )
}
