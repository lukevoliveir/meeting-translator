import { useState } from 'react'
import Prerequisites from './pages/Prerequisites'
import LanguageSelector from './pages/LanguageSelector'
import SpeakerProfile from './pages/SpeakerProfile'
import CallOverlay from './pages/CallOverlay'
import SessionSummary from './pages/SessionSummary'
import PopupOverlay from './pages/PopupOverlay'

const isPopup = new URLSearchParams(window.location.search).has('popup')

export default function App() {
  if (isPopup) return <PopupOverlay />
  const [page, setPage] = useState('prerequisites')
  const [targetLang, setTargetLang] = useState(null)
  const [profile, setProfile] = useState(null)
  const [sessionId, setSessionId] = useState(null)
  const [sessionData, setSessionData] = useState(null)

  const startSession = () => {
    setSessionId(`session-${Date.now()}`)
    setPage('call')
  }

  const handlePrerequisitesReady = () => setPage('language')

  const handleLanguageSelect = (lang) => {
    setTargetLang(lang)
    setPage('profile')
  }

  const handleProfileSkip = () => startSession()

  const handleProfileComplete = (prof) => {
    setProfile(prof)
    startSession()
  }

  const handleSessionEnd = (data) => {
    setSessionData(data)
    setPage('summary')
  }

  const handleRestart = () => {
    setPage('prerequisites')
    setTargetLang(null)
    setProfile(null)
    setSessionId(null)
    setSessionData(null)
  }

  return (
    <div className="app">
      {page === 'prerequisites' && (
        <Prerequisites onReady={handlePrerequisitesReady} />
      )}
      {page === 'language' && (
        <LanguageSelector onSelect={handleLanguageSelect} />
      )}
      {page === 'profile' && (
        <SpeakerProfile onSkip={handleProfileSkip} onComplete={handleProfileComplete} />
      )}
      {page === 'call' && (
        <CallOverlay
          sessionId={sessionId}
          targetLang={targetLang}
          profile={profile}
          onSessionEnd={handleSessionEnd}
        />
      )}
      {page === 'summary' && (
        <SessionSummary
          sessionData={sessionData}
          profile={profile}
          onClose={handleRestart}
        />
      )}
    </div>
  )
}
