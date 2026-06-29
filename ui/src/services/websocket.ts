import { io, Socket } from 'socket.io-client'

class WebSocketService {
  private socket: Socket | null = null

  connect() {
    this.socket = io('ws://localhost:8000/ws/dashboard', {
      transports: ['websocket'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 10,
    })

    this.socket.on('connect', () => console.log('[WS] Connected'))
    this.socket.on('disconnect', () => console.log('[WS] Disconnected'))

    return this.socket
  }

  on(event: string, handler: (data: unknown) => void) {
    this.socket?.on(event, handler)
  }

  off(event: string) {
    this.socket?.off(event)
  }

  disconnect() {
    this.socket?.disconnect()
    this.socket = null
  }

  get connected() {
    return this.socket?.connected ?? false
  }
}

export const wsService = new WebSocketService()
