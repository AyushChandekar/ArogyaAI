// API types for ArogyaAI
export interface QueryRequest {
  query: string;
  user_id?: string;
}

export interface QueryResponse {
  status: string;
  response?: string;
  query?: string;
  source?: string;
  message?: string;
  detected_language?: string;
  was_translated?: boolean;
  english_query?: string;
}

export interface DiseasesResponse {
  status: string;
  diseases?: string[];
  message?: string;
}

export interface Message {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
}

export interface ChatState {
  messages: Message[];
  loading: boolean;
  error: string | null;
}