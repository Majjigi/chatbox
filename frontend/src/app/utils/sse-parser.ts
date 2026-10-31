import { StreamEvent } from '../models/chat.model';

/**
 * Turns the raw text of a Server-Sent Events stream into event objects.
 *
 * The backend sends events like this, each ending with a blank line:
 *
 *     data: {"type": "token", "text": "Hel"}
 *
 *     data: {"type": "token", "text": "lo"}
 *
 * The network delivers that text in arbitrary pieces: one piece may hold half an
 * event, or three events at once. So the parser keeps any unfinished text in
 * `buffer` until the rest of it arrives.
 */
export class SseParser {
  private buffer = '';

  /** Feed in the next piece of text; get back every event that is now complete. */
  push(text: string): StreamEvent[] {
    this.buffer += text;
    const events: StreamEvent[] = [];

    // A blank line ("\n\n") marks the end of an event.
    let end = this.buffer.indexOf('\n\n');
    while (end !== -1) {
      const block = this.buffer.slice(0, end);
      this.buffer = this.buffer.slice(end + 2);

      const event = parseBlock(block);
      if (event) {
        events.push(event);
      }
      end = this.buffer.indexOf('\n\n');
    }
    return events;
  }
}

/** Read the JSON from the `data:` line(s) of one event. */
function parseBlock(block: string): StreamEvent | null {
  const data = block
    .split('\n')
    .filter((line) => line.startsWith('data:'))
    .map((line) => line.slice('data:'.length).trimStart())
    .join('\n');

  return data ? (JSON.parse(data) as StreamEvent) : null;
}
