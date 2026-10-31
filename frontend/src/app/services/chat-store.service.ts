import { Service, computed, inject, signal } from '@angular/core';
import { Subscription } from 'rxjs';

import { ChatMessage, ChatRequest, ChatTurn, ModelInfo, StreamEvent } from '../models/chat.model';
import { ChatApiService, describeHttpError } from './chat-api.service';

/**
 * Holds the state of the chat screen and the actions that change it.
 *
 * State lives in *signals*: values that components read like functions
 * (`store.messages()`). When a signal changes, every part of the screen that
 * reads it updates automatically.
 */
@Service()
export class ChatStoreService {
  private readonly api = inject(ChatApiService);

  // ---- State -------------------------------------------------------------
  readonly models = signal<ModelInfo[]>([]);
  readonly selectedModelId = signal('');
  readonly messages = signal<ChatMessage[]>([]);
  readonly isStreaming = signal(false);
  /** Set when the model list can't be loaded (usually: backend not running). */
  readonly loadError = signal<string | null>(null);

  // `computed` signals are worked out from other signals and stay in sync with them.
  readonly selectedModel = computed(() =>
    this.models().find((model) => model.id === this.selectedModelId()),
  );

  private nextId = 1;
  private activeStream: Subscription | null = null;

  // ---- Actions -----------------------------------------------------------

  /** Fetch the model list and pre-select the first model that's ready to use. */
  loadModels(): void {
    this.loadError.set(null);
    this.api.getModels().subscribe({
      next: (models) => {
        this.models.set(models);
        const firstAvailable = models.find((model) => model.available);
        this.selectedModelId.set(firstAvailable?.id ?? '');
      },
      error: (error) => this.loadError.set(describeHttpError(error)),
    });
  }

  /** Send a question and stream the reply into a new assistant message. */
  send(text: string): void {
    const question = text.trim();
    if (!question || this.isStreaming() || !this.selectedModelId()) {
      return;
    }

    const request: ChatRequest = {
      model: this.selectedModelId(),
      system_prompt: '',
      messages: [...toHistory(this.messages()), { role: 'user', content: question }],
    };

    // Show the question, plus an empty reply bubble that fills up as text arrives.
    const reply: ChatMessage = { id: this.nextId++, role: 'assistant', content: '', status: 'streaming' };
    this.messages.update((list) => [
      ...list,
      { id: this.nextId++, role: 'user', content: question, status: 'done' },
      reply,
    ]);
    this.isStreaming.set(true);

    this.activeStream = this.api.streamChat(request).subscribe({
      next: (event) => this.handleEvent(reply.id, event),
      error: (error: Error) => this.finishReply(reply.id, { status: 'error', error: error.message }),
      complete: () => {
        // The stream ended without a "done" or "error" event — e.g. the server crashed.
        if (this.isStreaming()) {
          this.finishReply(reply.id, {
            status: 'error',
            error: 'The connection closed before the reply finished.',
          });
        }
      },
    });
  }

  /** Stop the reply that's being written. Cancelling the request also stops the model. */
  stop(): void {
    const streaming = this.messages().find((message) => message.status === 'streaming');
    this.activeStream?.unsubscribe();
    if (streaming) {
      this.finishReply(streaming.id, { status: 'stopped' });
    }
  }

  /** Start a fresh conversation. */
  clearChat(): void {
    this.stop();
    this.messages.set([]);
  }

  // ---- Helpers -----------------------------------------------------------

  private handleEvent(replyId: number, event: StreamEvent): void {
    switch (event.type) {
      case 'token':
        this.updateMessage(replyId, (message) => ({ ...message, content: message.content + event.text }));
        break;
      case 'done':
        this.finishReply(replyId, { status: 'done' });
        break;
      case 'error':
        this.finishReply(replyId, { status: 'error', error: event.message });
        break;
    }
  }

  private finishReply(replyId: number, changes: Partial<ChatMessage>): void {
    this.updateMessage(replyId, (message) => ({ ...message, ...changes }));
    this.isStreaming.set(false);
    this.activeStream = null;
  }

  /** Replace one message with an updated copy (signals need a new array to notice the change). */
  private updateMessage(id: number, change: (message: ChatMessage) => ChatMessage): void {
    this.messages.update((list) => list.map((message) => (message.id === id ? change(message) : message)));
  }
}

/**
 * The conversation so far, in the shape the backend expects.
 * Only complete question + answer pairs are included, so a reply that failed
 * before writing anything doesn't leave the model with an unanswered question.
 */
export function toHistory(messages: ChatMessage[]): ChatTurn[] {
  const turns: ChatTurn[] = [];
  messages.forEach((message, index) => {
    const reply = messages[index + 1];
    if (message.role === 'user' && reply?.role === 'assistant' && reply.content) {
      turns.push({ role: 'user', content: message.content });
      turns.push({ role: 'assistant', content: reply.content });
    }
  });
  return turns;
}
