import { getName, getFlag } from '../utils/languages'
import './SessionSummary.css'

export default function SessionSummary({ sessionData, profile, onClose }) {
  const lang = sessionData?.target_language ?? '–'

  return (
    <div className="ss-page">
      <div className="ss-card">
        <div className="ss-header">
          <span className="ss-icon">📋</span>
          <h1 className="ss-title">Resumo da sessão</h1>
        </div>

        <div className="ss-stats">
          <div className="ss-stat">
            <span className="ss-stat-value">{sessionData?.phrases_translated ?? 0}</span>
            <span className="ss-stat-label">frases traduzidas</span>
          </div>
          <div className="ss-stat">
            <span className="ss-stat-value">
              {getFlag(lang)} {getName(lang)}
            </span>
            <span className="ss-stat-label">idioma destino</span>
          </div>
          <div className="ss-stat">
            <span className="ss-stat-value">{sessionData?.duration_minutes ?? 0} min</span>
            <span className="ss-stat-label">duração</span>
          </div>
        </div>

        {profile && (
          <div className="ss-profile-banner">
            👤 Perfil <strong>{profile.speaker_name}</strong> utilizado
          </div>
        )}

        {sessionData?.recent_phrases?.length > 0 && (
          <div className="ss-phrases">
            <p className="ss-phrases-label">Últimas legendas</p>
            <ul className="ss-phrase-list">
              {sessionData.recent_phrases.map((p, i) => (
                <li key={i} className="ss-phrase-item">
                  <span className="ss-phrase-original">{p.original}</span>
                  <span className="ss-phrase-arrow">→</span>
                  <span className="ss-phrase-translated">{p.translated}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        <button className="ss-btn-primary" onClick={onClose}>
          Nova sessão
        </button>
      </div>
    </div>
  )
}
