import { Component, input } from '@angular/core';

import { ChatMessage } from '../../models/chat.model';

/** One message: a bubble with the text, plus a status line under replies. */
@Component({
  selector: 'app-message-bubble',
  templateUrl: './message-bubble.component.html',
  styleUrl: './message-bubble.component.scss',
})
export class MessageBubbleComponent {
  /** The message to show, passed in by the parent: `<app-message-bubble [message]="...">` */
  readonly message = input.required<ChatMessage>();
}
