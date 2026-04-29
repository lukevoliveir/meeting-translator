import { useEffect, useState } from 'react'
import './LanguageSelector.css'

export default function LanguageSelector({ onSelect }) {
  const [languages, setLanguages] = useState([])
  const [selected, setSelected] = useState('pt')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const loadLanguages = () => {
    setLoading(true)
    setError(null)
    fetch('http://localhost:8000/api/languages')
      .then((r) => r.json())
      .then((data) => {
        setLanguages(data.languages)
        setLoading(false)
      })
      .catch(() => {
        setError('Não foi possível carregar os idiomas. Verifique se o backend está rodando.')
        setLoading(false)
      })
  }

  useEffect(() => { loadLanguages() }, [])

  return (
    <div className="ls-page">
      <div className="ls-card">
        <div className="ls-icon">🌐</div>
        <h1 className="ls-title">Meeting Translator</h1>
        <p className="ls-subtitle">Escolha o idioma das legendas</p>

        {loading ? (
          <div className="ls-loading">Carregando idiomas...</div>
        ) : error ? (
          <div className="ls-error">
            <p>{error}</p>
            <button className="ls-btn-retry" onClick={loadLanguages}>Tentar novamente</button>
          </div>
        ) : (
          <div className="ls-list">
            {languages.map((lang) => (
              <button
                key={lang.code}
                className={`ls-item ${selected === lang.code ? 'ls-item--selected' : ''}`}
                onClick={() => setSelected(lang.code)}
              >
                <span className="ls-flag">{lang.flag}</span>
                <span className="ls-name">{lang.name}</span>
                {selected === lang.code && <span className="ls-check">✓</span>}
              </button>
            ))}
          </div>
        )}

        <button
          className="ls-btn-primary"
          disabled={loading}
          onClick={() => onSelect(selected)}
        >
          Próximo →
        </button>
      </div>
    </div>
  )
}
