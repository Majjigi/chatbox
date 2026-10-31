import { Component, ElementRef, afterRenderEffect, inject, viewChild } from '@angular/core';

import { ChatStoreService } from '../../services/chat-store.service';
import { MessageBubbleComponent } from '../message-bubble/message-bubble.component';

/** The scrolling list of messages, or a welcome screen when the chat is empty. */
@Component({
  selector: 'app-message-list',
  imports: [MessageBubbleComponent],
  templateUrl: './message-list.component.html',
  styleUrl: './message-list.component.scss',
})
export class MessageListComponent {
  protected readonly store = inject(ChatStoreService);

  /** Clickable starter questions shown on the empty screen. */
  protected readonly examples = [
    'Explain streaming like I am five',
    'Write a haiku about coffee',
    'Give me 3 tips for learning Python',
  ];

  private readonly scroller = viewChild.required<ElementRef<HTMLElement>>('scroller');
  /** True while the user is looking at the newest message. */
  private followNewText = true;

  constructor() {
    // Runs after the screen has updated. Reading `messages()` here means it runs
    // again whenever a message or a new piece of text is added.
    afterRenderEffect(() => {
      this.store.messages();
      if (this.followNewText) {
        const element = this.scroller().nativeElement;
        element.scrollTop = element.scrollHeight;
      }
    });
  }

  /** Stop auto-scrolling if the user scrolls up to read; resume when they scroll back down. */
  protected onScroll(): void {
    const element = this.scroller().nativeElement;
    const distanceFromBottom = element.scrollHeight - element.scrollTop - element.clientHeight;
    this.followNewText = distanceFromBottom < 80;
  }
}
