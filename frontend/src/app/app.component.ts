import { Component, inject } from '@angular/core';

import { ChatHeaderComponent } from './components/chat-header/chat-header.component';
import { ChatInputComponent } from './components/chat-input/chat-input.component';
import { MessageListComponent } from './components/message-list/message-list.component';
import { ChatStoreService } from './services/chat-store.service';

/** The whole chat screen: header on top, messages in the middle, text box at the bottom. */
@Component({
  selector: 'app-root',
  imports: [ChatHeaderComponent, MessageListComponent, ChatInputComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss',
})
export class AppComponent {
  private readonly store = inject(ChatStoreService);

  constructor() {
    this.store.loadModels();
  }
}
