// Types shared by the services and components.
// The API shapes mirror backend/app/schemas/chat.py.

/** A model the user can pick (from GET /api/models). */
export interface ModelInfo {
  id: string;
  label: string;
  provider: 'demo' | 'gemini' | 'claude';
  /** False when the backend has no API key for it. */
  available: boolean;
}

/** One message as the backend expects it. */
export interface ChatTurn {
  role: 'user' | 'assistant';
  content: string;
}

/** Body of POST /api/chat/stream. */
export interface ChatRequest {
  model: string;
  system_prompt: string;
  /** The whole conversation, oldest first. The last one is the new question. */
  messages: ChatTurn[];
}

/** The events the backend streams back while a reply is being written. */
export type StreamEvent = TokenEvent | DoneEvent | StreamErrorEvent;

/** The next piece of the reply text. */
export interface TokenEvent {
  type: 'token';
  text: string;
}

/** The reply finished. */
export interface DoneEvent {
  type: 'done';
  input_tokens: number | null;
  output_tokens: number | null;
  total_ms: number;
  first_token_ms: number | null;
}

/** Something went wrong mid-reply. (Named so it doesn't clash with the browser's own ErrorEvent.) */
export interface StreamErrorEvent {
  type: 'error';
  message: string;
}

/** A message as shown on screen. */
export interface ChatMessage {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  /** streaming = text is still arriving; stopped = the user pressed Stop. */
  status: 'streaming' | 'done' | 'stopped' | 'error';
  error?: string;
}
