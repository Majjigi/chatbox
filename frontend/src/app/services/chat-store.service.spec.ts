import { TestBed } from '@angular/core/testing';
import { Subject, of } from 'rxjs';

import { ChatRequest, ModelInfo, StreamEvent } from '../models/chat.model';
import { ChatApiService } from './chat-api.service';
import { ChatStoreService } from './chat-store.service';

const MODELS: ModelInfo[] = [
  { id: 'gemini-flash-latest', label: 'Gemini', provider: 'gemini', available: false },
  { id: 'demo', label: 'Demo model (offline)', provider: 'demo', available: true },
];

describe('ChatStoreService', () => {
  let store: ChatStoreService;
  // Stands in for the backend stream: the test pushes events into it by hand.
  let events: Subject<StreamEvent>;
  let sentRequests: ChatRequest[];

  beforeEach(() => {
    sentRequests = [];
    const fakeApi = {
      getModels: () => of(MODELS),
      streamChat: (request: ChatRequest) => {
        sentRequests.push(request);
        events = new Subject<StreamEvent>();
        return events;
      },
    };
    TestBed.configureTestingModule({
      providers: [{ provide: ChatApiService, useValue: fakeApi }],
    });
    store = TestBed.inject(ChatStoreService);
    store.loadModels();
  });

  function finishReply(): void {
    events.next({ type: 'done', input_tokens: 4, output_tokens: 2, total_ms: 900, first_token_ms: 300 });
    events.complete();
  }

  it('pre-selects the first model that has an API key', () => {
    expect(store.selectedModelId()).toBe('demo');
  });

  it('adds the question and fills the reply as tokens arrive', () => {
    store.send('Hi');
    events.next({ type: 'token', text: 'Hel' });
    events.next({ type: 'token', text: 'lo' });

    const [question, reply] = store.messages();
    expect(question.content).toBe('Hi');
    expect(reply.content).toBe('Hello');
    expect(reply.status).toBe('streaming');
    expect(store.isStreaming()).toBe(true);

    finishReply();
    expect(store.messages()[1].status).toBe('done');
    expect(store.isStreaming()).toBe(false);
  });

  it('sends the earlier conversation along with a new question', () => {
    store.send('Hi');
    events.next({ type: 'token', text: 'Hello!' });
    finishReply();

    store.send('How are you?');

    expect(sentRequests[1].messages).toEqual([
      { role: 'user', content: 'Hi' },
      { role: 'assistant', content: 'Hello!' },
      { role: 'user', content: 'How are you?' },
    ]);
  });

  it('shows an error event under the reply', () => {
    store.send('Hi');
    events.next({ type: 'error', message: 'Rate limit reached.' });

    const reply = store.messages()[1];
    expect(reply.status).toBe('error');
    expect(reply.error).toBe('Rate limit reached.');
    expect(store.isStreaming()).toBe(false);
  });

  it('marks the reply as stopped when the user presses Stop', () => {
    store.send('Hi');
    events.next({ type: 'token', text: 'Once upon' });

    store.stop();

    expect(store.messages()[1].status).toBe('stopped');
    expect(store.isStreaming()).toBe(false);
  });
});
