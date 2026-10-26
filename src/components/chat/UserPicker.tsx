// Search students by name, @username or full email address. Single tap (private chat) or multi-select (groups).

import { Ionicons } from '@expo/vector-icons';
import React, { useEffect, useState } from 'react';
import { ActivityIndicator, FlatList, Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import { useAuth } from '../../context/auth';
import { displayName, type PersonProfile } from '../../lib/chat';
import { supabase } from '../../lib/supabase';
import Avatar from './Avatar';

type Props = {
  multi?: boolean;
  selected?: PersonProfile[];
  onToggle?: (p: PersonProfile) => void;
  onPick?: (p: PersonProfile) => void;
  exclude?: string[]; // user ids to hide (e.g. people already in the group)
};

export default function UserPicker({ multi, selected = [], onToggle, onPick, exclude = [] }: Props) {
  const { session } = useAuth();
  const me = session?.user.id;
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<PersonProfile[]>([]);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    const q = query.trim().replace(/[%,()]/g, '');
    if (q.length < 2) {
      setResults([]);
      return;
    }
    setBusy(true);
    const t = setTimeout(async () => {
      // Server-side search: name, @username, or the person's full email address.
      let { data, error } = await supabase.rpc('search_people', { q });
      if (error) {
        // search_people not installed yet (supabase/people.sql) – fall back to name/username search.
        ({ data, error } = await supabase
          .from('profiles')
          .select('id, full_name, username, avatar_url')
          .or(`full_name.ilike.%${q}%,username.ilike.%${q.replace('@', '')}%`)
          .neq('id', me ?? '')
          .limit(30));
      }
      if (error) console.warn('User search failed:', error.message);
      setResults(((data as PersonProfile[]) ?? []).filter((p) => p.id !== me && !exclude.includes(p.id)));
      setBusy(false);
    }, 300);
    return () => clearTimeout(t);
  }, [query, me, exclude.join(',')]);

  const isSelected = (id: string) => selected.some((s) => s.id === id);

  return (
    <View style={{ flex: 1 }}>
      <View style={styles.search}>
        <Ionicons name="search" size={18} color="#8e8e93" />
        <TextInput
          value={query}
          onChangeText={setQuery}
          placeholder="Name, @username or full email"
          placeholderTextColor="#8e8e93"
          style={styles.input}
          autoCapitalize="none"
          autoCorrect={false}
          autoFocus
        />
        {busy && <ActivityIndicator size="small" color="#8e8e93" />}
      </View>

      <FlatList
        data={results}
        keyExtractor={(p) => p.id}
        keyboardShouldPersistTaps="handled"
        ListEmptyComponent={
          <Text style={styles.empty}>
            {query.trim().length < 2 ? 'Type at least 2 letters to search' : busy ? '' : 'No students found. Try their full email address.'}
          </Text>
        }
        renderItem={({ item }) => {
          const on = isSelected(item.id);
          return (
            <Pressable
              style={({ pressed }) => [styles.row, pressed && { opacity: 0.6 }]}
              onPress={() => (multi ? onToggle?.(item) : onPick?.(item))}>
              <Avatar name={displayName(item)} url={item.avatar_url} seed={item.id} size={44} />
              <View style={{ flex: 1 }}>
                <Text style={styles.name}>{displayName(item)}</Text>
                {item.username ? <Text style={styles.username}>@{item.username}</Text> : null}
              </View>
              {multi && (
                <View style={[styles.check, on && styles.checkOn]}>
                  {on && <Ionicons name="checkmark" size={16} color="#fff" />}
                </View>
              )}
            </Pressable>
          );
        }}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  search: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    backgroundColor: '#1c1c1e',
    borderRadius: 12,
    paddingHorizontal: 12,
    marginHorizontal: 16,
    marginBottom: 8,
  },
  input: { flex: 1, color: '#fff', fontSize: 16, paddingVertical: 11 },
  empty: { color: '#8e8e93', textAlign: 'center', marginTop: 30, fontSize: 14 },
  row: { flexDirection: 'row', alignItems: 'center', gap: 12, paddingHorizontal: 16, paddingVertical: 10 },
  name: { color: '#fff', fontSize: 16, fontWeight: '700' },
  username: { color: '#8e8e93', fontSize: 13 },
  check: { width: 24, height: 24, borderRadius: 12, borderWidth: 2, borderColor: '#48484a', alignItems: 'center', justifyContent: 'center' },
  checkOn: { backgroundColor: '#5e5ce6', borderColor: '#5e5ce6' },
});
