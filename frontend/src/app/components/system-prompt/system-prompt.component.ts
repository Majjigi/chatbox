import { Component, inject } from '@angular/core';

import { ChatStoreService } from '../../services/chat-store.service';

/** A fold-out box for the system prompt: instructions the model follows for every reply. */
@Component({
  selector: 'app-system-prompt',
  templateUrl: './system-prompt.component.html',
  styleUrl: './system-prompt.component.scss',
})
export class SystemPromptComponent {
  protected readonly store = inject(ChatStoreService);
}
