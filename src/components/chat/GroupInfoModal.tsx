// Group details: rename, see members, add / remove people, leave.
// (Every member can manage the group.)

import { Ionicons } from '@expo/vector-icons';
import React, { useState } from 'react';
import { ActivityIndicator, Modal, Pressable, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useAuth } from '../../context/auth';
import { displayName, type PersonProfile } from '../../lib/chat';
import { supabase } from '../../lib/supabase';
import Avatar from './Avatar';
import UserPicker from './UserPicker';

type Props = {
  conversationId: string;
  name: string | null;
  members: PersonProfile[];
  onClose: () => void;
  onChanged: () => void;
  onLeft: () => void;
};

export default function GroupInfoModal({ conversationId, name, members, onClose, onChanged, onLeft }: Props) {
  const insets = useSafeAreaInsets();
  const { session } = useAuth();
  const me = session?.user.id;
  const [groupName, setGroupName] = useState(name ?? '');
  const [adding, setAdding] = useState(false);
  const [toAdd, setToAdd] = useState<PersonProfile[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function saveName() {
    const n = groupName.trim();
    if (!n || n === name) return;
    setBusy(true);
    const { error: err } = await supabase.from('conversations').update({ name: n }).eq('id', conversationId);
    if (!err) await supabase.from('messages').insert({ conversation_id: conversationId, kind: 'system', body: `renamed the group to “${n}”` });
    setBusy(false);
    if (err) setError(err.message);
    else onChanged();
  }

  async function remove(p: PersonProfile) {
    setBusy(true);
    await supabase.from('messages').insert({ conversation_id: conversationId, kind: 'system', body: `removed ${displayName(p)}` });
    const { error: err } = await supabase
      .from('conversation_members')
      .delete()
      .eq('conversation_id', conversationId)
      .eq('user_id', p.id);
    setBusy(false);
    if (err) setError(err.message);
    else onChanged();
  }

  async function leave() {
    if (!me) return;
    setBusy(true);
    await supabase.from('messages').insert({ conversation_id: conversationId, kind: 'system', body: 'left the group' });
    await supabase.from('conversation_members').delete().eq('conversation_id', conversationId).eq('user_id', me);
    setBusy(false);
    onLeft();
  }

  async function addSelected() {
    if (toAdd.length === 0) return setAdding(false);
    setBusy(true);
    const { error: err } = await supabase.rpc('add_group_members', {
      conv: conversationId,
      member_ids: toAdd.map((p) => p.id),
    });
    setBusy(false);
    if (err) return setError(err.message);
    setToAdd([]);
    setAdding(false);
    onChanged();
  }

  const toggle = (p: PersonProfile) =>
    setToAdd((list) => (list.some((s) => s.id === p.id) ? list.filter((s) => s.id !== p.id) : [...list, p]));

  return (
    <Modal visible animationType="slide" presentationStyle="pageSheet" onRequestClose={onClose}>
      <View style={[styles.screen, { paddingBottom: insets.bottom }]}>
        <View style={styles.header}>
          <Pressable onPress={adding ? () => setAdding(false) : onClose} hitSlop={10}>
            <Text style={styles.link}>{adding ? 'Back' : 'Done'}</Text>
          </Pressable>
          <Text style={styles.title}>{adding ? 'Add people' : 'Group info'}</Text>
          {adding ? (
            <Pressable onPress={addSelected} hitSlop={10}>
              <Text style={[styles.link, { fontWeight: '800' }]}>Add{toAdd.length ? ` (${toAdd.length})` : ''}</Text>
            </Pressable>
          ) : busy ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <View style={{ width: 40 }} />
          )}
        </View>

        {error && <Text style={styles.error}>{error}</Text>}

        {adding ? (
          <UserPicker multi selected={toAdd} onToggle={toggle} exclude={members.map((m) => m.id)} />
        ) : (
          <ScrollView contentContainerStyle={{ padding: 16 }} keyboardShouldPersistTaps="handled">
            <View style={{ alignItems: 'center', marginBottom: 18 }}>
              <Avatar group seed={conversationId} size={80} />
            </View>

            <Text style={styles.label}>Group name</Text>
            <View style={styles.nameRow}>
              <TextInput value={groupName} onChangeText={setGroupName} style={styles.nameInput} onSubmitEditing={saveName} />
              {groupName.trim() !== (name ?? '') && (
                <Pressable onPress={saveName} style={styles.saveButton}>
                  <Text style={styles.saveText}>Save</Text>
                </Pressable>
              )}
            </View>

            <Text style={[styles.label, { marginTop: 22 }]}>{members.length} members</Text>
            <Pressable style={styles.memberRow} onPress={() => setAdding(true)}>
              <View style={styles.addIcon}>
                <Ionicons name="person-add" size={18} color="#fff" />
              </View>
              <Text style={[styles.memberName, { color: '#5e5ce6' }]}>Add people</Text>
            </Pressable>
            {members.map((p) => (
              <View key={p.id} style={styles.memberRow}>
                <Avatar name={displayName(p)} url={p.avatar_url} seed={p.id} size={40} />
                <View style={{ flex: 1 }}>
                  <Text style={styles.memberName}>
                    {displayName(p)}
                    {p.id === me ? ' (you)' : ''}
                  </Text>
                  {p.username ? <Text style={styles.username}>@{p.username}</Text> : null}
                </View>
                {p.id !== me && (
                  <Pressable onPress={() => remove(p)} hitSlop={8}>
                    <Text style={styles.remove}>Remove</Text>
                  </Pressable>
                )}
              </View>
            ))}

            <Pressable style={styles.leave} onPress={leave}>
              <Ionicons name="exit-outline" size={20} color="#ff453a" />
              <Text style={styles.leaveText}>Leave group</Text>
            </Pressable>
          </ScrollView>
        )}
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#000', paddingTop: 12 },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 16, marginBottom: 12 },
  link: { color: '#0a84ff', fontSize: 16 },
  title: { color: '#fff', fontSize: 17, fontWeight: '800' },
  error: { color: '#ff453a', paddingHorizontal: 16, marginBottom: 8 },
  label: { color: '#8e8e93', fontSize: 13, fontWeight: '700', marginBottom: 8 },
  nameRow: { flexDirection: 'row', gap: 8 },
  nameInput: { flex: 1, backgroundColor: '#1c1c1e', borderRadius: 12, color: '#fff', fontSize: 16, paddingHorizontal: 14, paddingVertical: 12 },
  saveButton: { backgroundColor: '#5e5ce6', borderRadius: 12, paddingHorizontal: 16, justifyContent: 'center' },
  saveText: { color: '#fff', fontWeight: '700' },
  memberRow: { flexDirection: 'row', alignItems: 'center', gap: 12, paddingVertical: 8 },
  addIcon: { width: 40, height: 40, borderRadius: 20, backgroundColor: '#2c2c2e', alignItems: 'center', justifyContent: 'center' },
  memberName: { color: '#fff', fontSize: 16, fontWeight: '600' },
  username: { color: '#8e8e93', fontSize: 13 },
  remove: { color: '#ff453a', fontSize: 14, fontWeight: '600' },
  leave: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8, marginTop: 28, paddingVertical: 14, borderRadius: 12, backgroundColor: '#1c1c1e' },
  leaveText: { color: '#ff453a', fontSize: 16, fontWeight: '700' },
});
