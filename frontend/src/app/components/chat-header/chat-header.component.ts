import { Component, inject } from '@angular/core';

import { ChatStoreService } from '../../services/chat-store.service';

/** Top bar: app name, the model dropdown, and a "New chat" button. */
@Component({
  selector: 'app-chat-header',
  templateUrl: './chat-header.component.html',
  styleUrl: './chat-header.component.scss',
})
export class ChatHeaderComponent {
  protected readonly store = inject(ChatStoreService);
}
