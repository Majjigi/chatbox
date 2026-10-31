import { SseParser } from './sse-parser';

describe('SseParser', () => {
  it('reads complete events', () => {
    const parser = new SseParser();

    const events = parser.push(
      'data: {"type": "token", "text": "Hi"}\n\ndata: {"type": "token", "text": "!"}\n\n',
    );

    expect(events).toEqual([
      { type: 'token', text: 'Hi' },
      { type: 'token', text: '!' },
    ]);
  });

  it('waits for the rest of an event that arrives in pieces', () => {
    const parser = new SseParser();

    expect(parser.push('data: {"type": "tok')).toEqual([]);
    expect(parser.push('en", "text": "Hi"}\n')).toEqual([]);
    expect(parser.push('\n')).toEqual([{ type: 'token', text: 'Hi' }]);
  });

  it('reads the done event with its stats', () => {
    const parser = new SseParser();

    const [event] = parser.push(
      'data: {"type": "done", "input_tokens": 5, "output_tokens": 9, "total_ms": 812, "first_token_ms": 230}\n\n',
    );

    expect(event).toEqual({
      type: 'done',
      input_tokens: 5,
      output_tokens: 9,
      total_ms: 812,
      first_token_ms: 230,
    });
  });
});
