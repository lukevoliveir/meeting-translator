import { useRef, useState } from 'react'

export function useSession() {
  const startTime = useRef(Date.now())
  const [phraseCount, setPhraseCount] = useState(0)

  const addPhrase = () => setPhraseCount((n) => n + 1)

  const getStats = () => ({
    duration_minutes: Math.round((Date.now() - startTime.current) / 60000),
    phrases_translated: phraseCount,
  })

  return { phraseCount, addPhrase, getStats }
}
