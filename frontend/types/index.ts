export interface Message {
  id: string;
  type: 'sent' | 'received';
  text: string;
  original?: string;
  translated?: string;
  timestamp: string;
  sourceLang?: string;
}

export interface ChatSession {
  roomId: string;
  userType: 'customer' | 'agent';
  language?: string;
  isOnline: boolean;
}
