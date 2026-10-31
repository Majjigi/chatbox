import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Service, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../environments/environment';
import { ChatRequest, ModelInfo, StreamEvent } from '../models/chat.model';
import { SseParser } from '../utils/sse-parser';

/**
 * Talks to the FastAPI backend — one method per endpoint, nothing else.
 * (State and UI logic live in ChatStoreService.)
 *
 * `@Service()` is Angular 22's short form of `@Injectable({ providedIn: 'root' })`:
 * one shared instance that any component or service can `inject()`.
 */
@Service()
export class ChatApiService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = environment.apiUrl;

  /** GET /api/models — the choices for the model dropdown. */
  getModels(): Observable<ModelInfo[]> {
    return this.http.get<ModelInfo[]>(`${this.baseUrl}/models`);
  }

  /**
   * POST /api/chat/stream — emits each event as soon as it arrives.
   *
   * HttpClient hands over a response only once it's complete, so for streaming we
   * use the browser's own `fetch()` and read the body piece by piece.
   * Unsubscribing cancels the request, which also stops the model on the server.
   */
  streamChat(request: ChatRequest): Observable<StreamEvent> {
    return new Observable<StreamEvent>((subscriber) => {
      const abort = new AbortController();

      this.readStream(request, abort.signal, (event) => subscriber.next(event))
        .then(() => subscriber.complete())
        .catch((error) => {
          // An abort is the user pressing Stop, not a failure.
          if (!abort.signal.aborted) {
            subscriber.error(new Error(describeStreamError(error)));
          }
        });

      // Runs when the subscriber unsubscribes.
      return () => abort.abort();
    });
  }

  private async readStream(
    request: ChatRequest,
    signal: AbortSignal,
    onEvent: (event: StreamEvent) => void,
  ): Promise<void> {
    const response = await fetch(`${this.baseUrl}/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
      signal,
    });

    // Problems found before streaming starts come back as normal HTTP errors.
    if (!response.ok || !response.body) {
      throw new Error(await readErrorDetail(response));
    }

    // The body arrives as bytes; TextDecoderStream turns them into text.
    const reader = response.body.pipeThrough(new TextDecoderStream()).getReader();
    const parser = new SseParser();

    while (true) {
      const { value, done } = await reader.read(); // waits for the next piece
      if (done) {
        return;
      }
      for (const event of parser.push(value)) {
        onEvent(event);
      }
    }
  }
}

/** FastAPI puts the reason for an error in `detail`. */
async function readErrorDetail(response: Response): Promise<string> {
  try {
    const body = await response.json();
    if (typeof body.detail === 'string') {
      return body.detail;
    }
  } catch {
    // The body wasn't JSON — fall through to the generic message.
  }
  return `The server had a problem (error ${response.status}).`;
}

function describeStreamError(error: unknown): string {
  // fetch() throws a TypeError when it can't connect at all.
  if (error instanceof TypeError) {
    return `Can't reach the backend at ${environment.apiUrl}. Is it running?`;
  }
  return error instanceof Error ? error.message : 'Something unexpected went wrong.';
}

/** Turns an HttpClient failure into a sentence a person can act on. */
export function describeHttpError(error: unknown): string {
  if (error instanceof HttpErrorResponse && error.status === 0) {
    return `Can't reach the backend at ${environment.apiUrl}. Is it running?`;
  }
  if (error instanceof HttpErrorResponse) {
    return `The server had a problem (error ${error.status}).`;
  }
  return 'Something unexpected went wrong.';
}
