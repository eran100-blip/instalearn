// "Share" from the feed: send the video to one of your chats, or to other apps.

import { Ionicons } from '@expo/vector-icons';
import React, { useState } from 'react';
import { FlatList, Modal, Pressable, Share, StyleSheet, Text, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useChat } from '../../context/chat';
import type { LearningVideo } from '../../data/sample';
import { conversationTitle, sendVideo } from '../../lib/chat';
import Avatar from './Avatar';

type Props = { visible: boolean; video: LearningVideo; courseName: string; onClose: () => void };

export default function ShareSheet({ visible, video, courseName, onClose }: Props) {
  const insets = useSafeAreaInsets();
  const { conversations } = useChat();
  const [sent, setSent] = useState<Record<string, boolean>>({});

  async function send(id: string) {
    if (sent[id]) return;
    setSent((s) => ({ ...s, [id]: true }));
    const err = await sendVideo(id, video.id);
    if (err) setSent((s) => ({ ...s, [id]: false }));
  }

  function close() {
    setSent({});
    onClose();
  }

  return (
    <Modal visible={visible} transparent animationType="slide" onRequestClose={close}>
      <Pressable style={styles.backdrop} onPress={close}>
        <Pressable style={[styles.sheet, { paddingBottom: insets.bottom + 12 }]} onPress={() => {}}>
          <View style={styles.handle} />
          <Text style={styles.title}>Share</Text>

          {conversations.length === 0 ? (
            <Text style={styles.empty}>No chats yet – start one in the Chats tab.</Text>
          ) : (
            <FlatList
              data={conversations}
              keyExtractor={(c) => c.id}
              style={{ maxHeight: 320 }}
              renderItem={({ item }) => (
                <View style={styles.row}>
                  <Avatar
                    name={conversationTitle(item)}
                    url={item.is_group ? null : item.other_avatar}
                    group={item.is_group}
                    seed={item.is_group ? item.id : item.other_id ?? item.id}
                    size={40}
                  />
                  <Text style={styles.name} numberOfLines={1}>
                    {conversationTitle(item)}
                  </Text>
                  <Pressable
                    style={[styles.sendButton, sent[item.id] && styles.sentButton]}
                    onPress={() => send(item.id)}>
                    <Text style={styles.sendText}>{sent[item.id] ? 'Sent ✓' : 'Send'}</Text>
                  </Pressable>
                </View>
              )}
            />
          )}

          <Pressable
            style={styles.other}
            onPress={() => Share.share({ message: `${video.title} (${courseName}) - watch it on InstaLearn` })}>
            <Ionicons name="share-outline" size={20} color="#fff" />
            <Text style={styles.otherText}>Other apps…</Text>
          </Pressable>
        </Pressable>
      </Pressable>
    </Modal>
  );
}

const styles = StyleSheet.create({
  backdrop: { flex: 1, justifyContent: 'flex-end', backgroundColor: 'rgba(0,0,0,0.5)' },
  sheet: { backgroundColor: '#1c1c1e', borderTopLeftRadius: 24, borderTopRightRadius: 24, paddingHorizontal: 16, paddingTop: 10 },
  handle: { alignSelf: 'center', width: 40, height: 5, borderRadius: 3, backgroundColor: '#48484a', marginBottom: 12 },
  title: { color: '#fff', fontSize: 18, fontWeight: '800', marginBottom: 10 },
  empty: { color: '#8e8e93', fontSize: 14, paddingVertical: 16 },
  row: { flexDirection: 'row', alignItems: 'center', gap: 12, paddingVertical: 8 },
  name: { flex: 1, color: '#fff', fontSize: 16, fontWeight: '600' },
  sendButton: { backgroundColor: '#5e5ce6', borderRadius: 999, paddingHorizontal: 16, paddingVertical: 7 },
  sentButton: { backgroundColor: '#3a3a3c' },
  sendText: { color: '#fff', fontWeight: '700', fontSize: 14 },
  other: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8, marginTop: 12, paddingVertical: 13, borderRadius: 12, backgroundColor: '#2c2c2e' },
  otherText: { color: '#fff', fontSize: 15, fontWeight: '700' },
});
