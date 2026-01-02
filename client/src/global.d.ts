/* Global type declarations */
import { WebSocketClient } from './api/websocket'

declare global {
  interface Window {
    wsClient?: WebSocketClient
  }
}

export {}
