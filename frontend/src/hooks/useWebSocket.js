import { useEffect, useState, useRef, useCallback } from 'react'

export function useWebSocket(url, onMessage) {
  const [connected, setConnected] = useState(false)
  const ws = useRef(null)
  const onMessageRef = useRef(onMessage)
  onMessageRef.current = onMessage

  useEffect(() => {
    ws.current = new WebSocket(url)
    ws.current.onopen = () => setConnected(true)
    ws.current.onmessage = (e) => onMessageRef.current(JSON.parse(e.data))
    ws.current.onclose = () => setConnected(false)
    ws.current.onerror = () => setConnected(false)
    return () => ws.current?.close()
  }, [url])

  const send = useCallback((data) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(data))
    }
  }, [])

  return { connected, send }
}
