// Chats: your private chats and groups, with unread counts.

import { Ionicons } from '@expo/vector-icons';
import React, { useState } from 'react';
import { ActivityIndicator, FlatList, Pressable, StatusBar, StyleSheet, Text, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import Avatar from '../components/chat/Avatar';
import ConversationView from '../components/chat/ConversationView';
import NewChatModal from '../components/chat/NewChatModal';
import { useChat } from '../context/chat';
import { isRTL } from '../data/sample';
import { conversationTitle, formatTime } from '../lib/chat';

export default function ChatsScreen() {
  const insets = useSafeAreaInsets();
  const { conversations, loading, refresh } = useChat();
  const [openId, setOpenId] = useState<string | null>(null);
  const [newChat, setNewChat] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  async function onRefresh() {
    setRefreshing(true);
    await refresh();
    setRefreshing(false);
  }

  return (
    <View style={styles.screen}>
      <StatusBar barStyle="light-content" />
      <View style={[styles.header, { paddingTop: insets.top + 10 }]}>
        <Text style={styles.title}>Chats</Text>
        <Pressable style={styles.newButton} onPress={() => setNewChat(true)} hitSlop={8}>
          <Ionicons name="create-outline" size={22} color="#fff" />
        </Pressable>
      </View>

      {loading ? (
        <View style={styles.center}>
          <ActivityIndicator color="#fff" />
        </View>
      ) : (
        <FlatList
          data={conversations}
          keyExtractor={(c) => c.id}
          refreshing={refreshing}
          onRefresh={onRefresh}
          contentContainerStyle={{ paddingBottom: insets.bottom + 100, flexGrow: 1 }}
          ListEmptyComponent={
            <View style={styles.empty}>
              <View style={styles.emptyIcon}>
                <Ionicons name="chatbubbles" size={40} color="#fff" />
              </View>
              <Text style={styles.emptyTitle}>No chats yet</Text>
              <Text style={styles.emptyText}>Message a classmate or start a study group.</Text>
              <Pressable style={styles.startButton} onPress={() => setNewChat(true)}>
                <Text style={styles.startText}>Start a chat</Text>
              </Pressable>
            </View>
          }
          renderItem={({ item }) => {
            const preview = item.last_message_preview ?? (item.is_group ? 'Group created' : 'New chat');
            const unread = item.unread > 0;
            return (
              <Pressable style={({ pressed }) => [styles.row, pressed && { backgroundColor: '#111114' }]} onPress={() => setOpenId(item.id)}>
                <Avatar
                  name={conversationTitle(item)}
                  url={item.is_group ? null : item.other_avatar}
                  group={item.is_group}
                  seed={item.is_group ? item.id : item.other_id ?? item.id}
                  size={54}
                />
                <View style={{ flex: 1 }}>
                  <View style={styles.rowTop}>
                    <Text style={styles.name} numberOfLines={1}>
                      {conversationTitle(item)}
                    </Text>
                    <Text style={[styles.time, unread && { color: '#5e5ce6' }]}>{formatTime(item.last_message_at)}</Text>
                  </View>
                  <View style={styles.rowBottom}>
                    <Text
                      style={[styles.preview, unread && styles.previewUnread, isRTL(preview) && { textAlign: 'right' }]}
                      numberOfLines={1}>
                      {preview}
                    </Text>
                    {unread && (
                      <View style={styles.badge}>
                        <Text style={styles.badgeText}>{item.unread > 99 ? '99+' : item.unread}</Text>
                      </View>
                    )}
                  </View>
                </View>
              </Pressable>
            );
          }}
        />
      )}

      <NewChatModal
        visible={newChat}
        onClose={() => setNewChat(false)}
        onOpen={(id) => {
          setNewChat(false);
          refresh();
          setTimeout(() => setOpenId(id), 350);
        }}
      />
      {openId && <ConversationView conversationId={openId} onClose={() => setOpenId(null)} />}
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#000' },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 16, paddingBottom: 10 },
  title: { color: '#fff', fontSize: 30, fontWeight: '900' },
  newButton: { width: 40, height: 40, borderRadius: 20, backgroundColor: '#1c1c1e', alignItems: 'center', justifyContent: 'center' },
  row: { flexDirection: 'row', alignItems: 'center', gap: 12, paddingHorizontal: 16, paddingVertical: 10 },
  rowTop: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  rowBottom: { flexDirection: 'row', alignItems: 'center', gap: 8, marginTop: 3 },
  name: { flex: 1, color: '#fff', fontSize: 16, fontWeight: '700' },
  time: { color: '#8e8e93', fontSize: 12 },
  preview: { flex: 1, color: '#8e8e93', fontSize: 14 },
  previewUnread: { color: '#fff', fontWeight: '600' },
  badge: { minWidth: 22, height: 22, borderRadius: 11, backgroundColor: '#5e5ce6', alignItems: 'center', justifyContent: 'center', paddingHorizontal: 6 },
  badgeText: { color: '#fff', fontSize: 12, fontWeight: '800' },
  empty: { flex: 1, alignItems: 'center', justifyContent: 'center', paddingHorizontal: 40, paddingBottom: 80 },
  emptyIcon: { width: 84, height: 84, borderRadius: 42, backgroundColor: '#5e5ce6', alignItems: 'center', justifyContent: 'center', marginBottom: 16 },
  emptyTitle: { color: '#fff', fontSize: 22, fontWeight: '800' },
  emptyText: { color: '#8e8e93', fontSize: 15, textAlign: 'center', marginTop: 6 },
  startButton: { marginTop: 20, backgroundColor: '#5e5ce6', borderRadius: 999, paddingHorizontal: 24, paddingVertical: 12 },
  startText: { color: '#fff', fontSize: 16, fontWeight: '800' },
});
