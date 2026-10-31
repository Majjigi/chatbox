import { Component, computed, inject, signal } from '@angular/core';

import { ChatStoreService } from '../../services/chat-store.service';

/** The text box at the bottom, with a Send button (or Stop while a reply is streaming). */
@Component({
  selector: 'app-chat-input',
  templateUrl: './chat-input.component.html',
  styleUrl: './chat-input.component.scss',
})
export class ChatInputComponent {
  protected readonly store = inject(ChatStoreService);

  /** What the user has typed so far. */
  protected readonly draft = signal('');
  protected readonly canSend = computed(
    () =>
      this.draft().trim().length > 0 && !!this.store.selectedModelId() && !this.store.isStreaming(),
  );

  protected send(): void {
    if (!this.canSend()) {
      return;
    }
    this.store.send(this.draft());
    this.draft.set('');
  }

  /** Enter sends; Shift+Enter starts a new line. */
  protected onKeydown(event: KeyboardEvent): void {
    // isComposing: the user is still typing a character with an input method (e.g. Japanese).
    if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) {
      event.preventDefault();
      this.send();
    }
  }
}
