// Keeps the user's chats list (with unread counts) up to date in real time.

import React, { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react';
import type { ConversationSummary } from '../lib/chat';
import { supabase } from '../lib/supabase';
import { useAuth } from './auth';

type ChatContextValue = {
  conversations: ConversationSummary[];
  totalUnread: number;
  loading: boolean;
  refresh: () => Promise<void>;
  // The chat that is open right now (its new messages are not counted as unread).
  setOpenConversation: (id: string | null) => void;
};

const ChatContext = createContext<ChatContextValue | null>(null);

export function ChatProvider({ children }: { children: React.ReactNode }) {
  const { session } = useAuth();
  const userId = session?.user.id;
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const openRef = useRef<string | null>(null);

  const refresh = useCallback(async () => {
    if (!userId) return;
    const { data } = await supabase.rpc('my_conversations');
    const list = ((data as ConversationSummary[]) ?? []).map((c) =>
      c.id === openRef.current ? { ...c, unread: 0 } : c,
    );
    setConversations(list);
    setLoading(false);
  }, [userId]);

  useEffect(() => {
    if (!userId) {
      setConversations([]);
      return;
    }
    refresh();
    // Any new message or membership change → reload the list (bundled).
    let timer: ReturnType<typeof setTimeout> | undefined;
    const soon = () => {
      clearTimeout(timer);
      timer = setTimeout(refresh, 300);
    };
    const channel = supabase
      .channel(`chats-${userId}`)
      .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'messages' }, soon)
      .on('postgres_changes', { event: '*', schema: 'public', table: 'conversation_members' }, soon)
      .subscribe();
    return () => {
      clearTimeout(timer);
      supabase.removeChannel(channel);
    };
  }, [userId, refresh]);

  const setOpenConversation = useCallback((id: string | null) => {
    openRef.current = id;
    if (id) setConversations((list) => list.map((c) => (c.id === id ? { ...c, unread: 0 } : c)));
  }, []);

  const totalUnread = conversations.reduce((n, c) => n + (c.unread || 0), 0);

  const value = useMemo(
    () => ({ conversations, totalUnread, loading, refresh, setOpenConversation }),
    [conversations, totalUnread, loading, refresh, setOpenConversation],
  );
  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
}

export function useChat() {
  const ctx = useContext(ChatContext);
  if (!ctx) throw new Error('useChat must be used inside <ChatProvider>');
  return ctx;
}
