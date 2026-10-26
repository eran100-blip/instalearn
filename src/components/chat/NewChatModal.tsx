// Start a private chat or create a group.

import { Ionicons } from '@expo/vector-icons';
import React, { useState } from 'react';
import { ActivityIndicator, Modal, Pressable, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { displayName, type PersonProfile } from '../../lib/chat';
import { supabase } from '../../lib/supabase';
import Avatar from './Avatar';
import UserPicker from './UserPicker';

type Props = { visible: boolean; onClose: () => void; onOpen: (conversationId: string) => void };

export default function NewChatModal({ visible, onClose, onOpen }: Props) {
  const insets = useSafeAreaInsets();
  const [group, setGroup] = useState(false);
  const [selected, setSelected] = useState<PersonProfile[]>([]);
  const [name, setName] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function reset() {
    setGroup(false);
    setSelected([]);
    setName('');
    setError(null);
  }
  function close() {
    reset();
    onClose();
  }

  async function startDirect(p: PersonProfile) {
    setBusy(true);
    const { data, error: err } = await supabase.rpc('start_direct_chat', { other: p.id });
    setBusy(false);
    if (err) return setError(err.message);
    reset();
    onOpen(data as string);
  }

  async function createGroup() {
    if (selected.length < 1) return setError('Pick at least one person.');
    if (name.trim().length < 2) return setError('Give the group a name.');
    setBusy(true);
    const { data, error: err } = await supabase.rpc('create_group', {
      group_name: name.trim(),
      member_ids: selected.map((s) => s.id),
    });
    setBusy(false);
    if (err) return setError(err.message);
    reset();
    onOpen(data as string);
  }

  const toggle = (p: PersonProfile) =>
    setSelected((list) => (list.some((s) => s.id === p.id) ? list.filter((s) => s.id !== p.id) : [...list, p]));

  return (
    <Modal visible={visible} animationType="slide" presentationStyle="pageSheet" onRequestClose={close}>
      <View style={[styles.screen, { paddingBottom: insets.bottom }]}>
        <View style={styles.header}>
          <Pressable onPress={close} hitSlop={10}>
            <Text style={styles.cancel}>Cancel</Text>
          </Pressable>
          <Text style={styles.title}>{group ? 'New group' : 'New chat'}</Text>
          {group ? (
            <Pressable onPress={createGroup} disabled={busy} hitSlop={10}>
              {busy ? <ActivityIndicator color="#5e5ce6" /> : <Text style={styles.create}>Create</Text>}
            </Pressable>
          ) : (
            <View style={{ width: 52 }} />
          )}
        </View>

        {!group && (
          <Pressable style={styles.groupRow} onPress={() => setGroup(true)}>
            <View style={styles.groupIcon}>
              <Ionicons name="people" size={20} color="#fff" />
            </View>
            <Text style={styles.groupText}>New group</Text>
            <Ionicons name="chevron-forward" size={18} color="#8e8e93" />
          </Pressable>
        )}

        {group && (
          <View style={{ paddingHorizontal: 16, marginBottom: 8 }}>
            <TextInput
              value={name}
              onChangeText={setName}
              placeholder="Group name (e.g. Calculus 1 study group)"
              placeholderTextColor="#8e8e93"
              style={styles.nameInput}
            />
            {selected.length > 0 && (
              <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ gap: 8, paddingTop: 10 }}>
                {selected.map((p) => (
                  <Pressable key={p.id} style={styles.chip} onPress={() => toggle(p)}>
                    <Avatar name={displayName(p)} url={p.avatar_url} seed={p.id} size={22} />
                    <Text style={styles.chipText}>{displayName(p)}</Text>
                    <Ionicons name="close" size={14} color="#aeaeb2" />
                  </Pressable>
                ))}
              </ScrollView>
            )}
          </View>
        )}

        {error && <Text style={styles.error}>{error}</Text>}

        <UserPicker multi={group} selected={selected} onToggle={toggle} onPick={startDirect} />
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#000', paddingTop: 12 },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 16, marginBottom: 14 },
  cancel: { color: '#0a84ff', fontSize: 16 },
  title: { color: '#fff', fontSize: 17, fontWeight: '800' },
  create: { color: '#5e5ce6', fontSize: 16, fontWeight: '800' },
  groupRow: { flexDirection: 'row', alignItems: 'center', gap: 12, paddingHorizontal: 16, paddingVertical: 10, marginBottom: 6 },
  groupIcon: { width: 44, height: 44, borderRadius: 22, backgroundColor: '#5e5ce6', alignItems: 'center', justifyContent: 'center' },
  groupText: { flex: 1, color: '#fff', fontSize: 16, fontWeight: '700' },
  nameInput: { backgroundColor: '#1c1c1e', borderRadius: 12, color: '#fff', fontSize: 16, paddingHorizontal: 14, paddingVertical: 12 },
  chip: { flexDirection: 'row', alignItems: 'center', gap: 6, backgroundColor: '#2c2c2e', borderRadius: 999, paddingLeft: 4, paddingRight: 10, paddingVertical: 4 },
  chipText: { color: '#fff', fontSize: 13, fontWeight: '600' },
  error: { color: '#ff453a', paddingHorizontal: 16, marginBottom: 8 },
});
