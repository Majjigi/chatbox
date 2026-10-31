import { DecimalPipe } from '@angular/common';
import { Component, input } from '@angular/core';

import { ChatMessage } from '../../models/chat.model';
import { DurationPipe } from '../../pipes/duration.pipe';

/** One message: a bubble with the text, plus a line of details under each reply. */
@Component({
  selector: 'app-message-bubble',
  // DecimalPipe is Angular's `number` pipe: 1234 → "1,234".
  imports: [DecimalPipe, DurationPipe],
  templateUrl: './message-bubble.component.html',
  styleUrl: './message-bubble.component.scss',
})
export class MessageBubbleComponent {
  /** The message to show, passed in by the parent: `<app-message-bubble [message]="...">` */
  readonly message = input.required<ChatMessage>();
}
