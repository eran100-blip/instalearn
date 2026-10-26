// One chat (private or group): messages in real time, text / photos / shared videos.

import { Ionicons } from '@expo/vector-icons';
import { Image } from 'expo-image';
import React, { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  FlatList,
  KeyboardAvoidingView,
  Modal,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useAuth } from '../../context/auth';
import { useChat } from '../../context/chat';
import { getCourse } from '../../data/courses';
import { isRTL, VIDEOS, type LearningVideo } from '../../data/sample';
import {
  displayName,
  formatTime,
  imageUrl,
  markRead,
  pickAndSendImage,
  sendText,
  type Message,
  type PersonProfile,
} from '../../lib/chat';
import { supabase } from '../../lib/supabase';
import Avatar from './Avatar';
import GroupInfoModal from './GroupInfoModal';
import VideoPlayerModal from './VideoPlayerModal';

type Props = { conversationId: string; onClose: () => void };

type ConvInfo = { id: string; is_group: boolean; name: string | null };

export default function ConversationView({ conversationId, onClose }: Props) {
  const insets = useSafeAreaInsets();
  const { session } = useAuth();
  const me = session?.user.id ?? '';
  const { setOpenConversation, refresh } = useChat();

  const [conv, setConv] = useState<ConvInfo | null>(null);
  const [members, setMembers] = useState<Record<string, PersonProfile>>({});
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);
  const [text, setText] = useState('');
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [playing, setPlaying] = useState<LearningVideo | null>(null);
  const [info, setInfo] = useState(false);

  // Load conversation, members and the latest messages.
  const loadMeta = useCallback(async () => {
    const [{ data: c }, { data: mem }] = await Promise.all([
      supabase.from('conversations').select('id, is_group, name').eq('id', conversationId).single(),
      supabase.from('conversation_members').select('user_id').eq('conversation_id', conversationId),
    ]);
    setConv(c as ConvInfo);
    const ids = (mem ?? []).map((m: { user_id: string }) => m.user_id);
    if (ids.length) {
      const { data: profs } = await supabase.from('profiles').select('id, full_name, username, avatar_url').in('id', ids);
      const map: Record<string, PersonProfile> = {};
      (profs as PersonProfile[] | null)?.forEach((p) => (map[p.id] = p));
      setMembers(map);
    }
  }, [conversationId]);

  useEffect(() => {
    setOpenConversation(conversationId);
    loadMeta();
    supabase
      .from('messages')
      .select('*')
      .eq('conversation_id', conversationId)
      .order('created_at', { ascending: false })
      .limit(100)
      .then(({ data }) => {
        setMessages((data as Message[]) ?? []);
        setLoading(false);
      });
    markRead(conversationId, me);

    // New messages in real time.
    const channel = supabase
      .channel(`conv-${conversationId}`)
      .on(
        'postgres_changes',
        { event: 'INSERT', schema: 'public', table: 'messages', filter: `conversation_id=eq.${conversationId}` },
        (payload) => {
          const m = payload.new as Message;
          setMessages((list) => (list.some((x) => x.id === m.id) ? list : [m, ...list]));
          markRead(conversationId, me);
          if (m.kind === 'system') loadMeta();
        },
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
      setOpenConversation(null);
      markRead(conversationId, me).then(refresh);
    };
  }, [conversationId, me, loadMeta, setOpenConversation, refresh]);

  // Title: group name, or the other person.
  const other = (Object.values(members) as PersonProfile[]).find((p) => p.id !== me);
  const title = conv?.is_group ? conv.name || 'Group' : displayName(other);
  const subtitle = conv?.is_group
    ? `${Object.keys(members).length} members`
    : other?.username
      ? `@${other.username}`
      : '';

  async function onSend() {
    if (!text.trim() || sending) return;
    setSending(true);
    setError(null);
    const body = text;
    setText('');
    const err = await sendText(conversationId, body);
    setSending(false);
    if (err) {
      setError(err);
      setText(body);
    }
  }

  async function onPhoto() {
    setError(null);
    setSending(true);
    const err = await pickAndSendImage(conversationId);
    setSending(false);
    if (err) setError(err);
  }

  function renderMessage({ item, index }: { item: Message; index: number }) {
    if (item.kind === 'system') {
      return (
        <Text style={styles.system}>
          {displayName(members[item.sender_id])} {item.body}
        </Text>
      );
    }
    const mine = item.sender_id === me;
    // Show the sender's name in groups, above the first message of a run.
    const older = messages[index + 1];
    const showName = conv?.is_group && !mine && (!older || older.sender_id !== item.sender_id || older.kind === 'system');
    const sender = members[item.sender_id];

    return (
      <View style={[styles.row, mine ? styles.rowMine : styles.rowTheirs]}>
        {conv?.is_group && !mine && (
          <View style={{ width: 30 }}>
            {showName && <Avatar name={displayName(sender)} url={sender?.avatar_url} seed={item.sender_id} size={28} />}
          </View>
        )}
        <View style={{ maxWidth: '78%' }}>
          {showName && <Text style={styles.sender}>{displayName(sender)}</Text>}
          <Bubble message={item} mine={mine} onPlay={setPlaying} />
        </View>
      </View>
    );
  }

  return (
    <Modal visible animationType="slide" presentationStyle="fullScreen" onRequestClose={onClose}>
      <KeyboardAvoidingView style={styles.screen} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
        {/* Header */}
        <View style={[styles.header, { paddingTop: insets.top + 6 }]}>
          <Pressable onPress={onClose} hitSlop={10} style={styles.back}>
            <Ionicons name="chevron-back" size={28} color="#fff" />
          </Pressable>
          <Pressable style={styles.headerCenter} onPress={() => conv?.is_group && setInfo(true)}>
            <Avatar
              name={title}
              url={conv?.is_group ? null : other?.avatar_url}
              group={conv?.is_group}
              seed={conv?.is_group ? conversationId : other?.id}
              size={38}
            />
            <View style={{ flex: 1 }}>
              <Text style={styles.title} numberOfLines={1}>
                {title}
              </Text>
              {!!subtitle && <Text style={styles.subtitle}>{subtitle}</Text>}
            </View>
          </Pressable>
          {conv?.is_group && (
            <Pressable onPress={() => setInfo(true)} hitSlop={10}>
              <Ionicons name="information-circle-outline" size={26} color="#fff" />
            </Pressable>
          )}
        </View>

        {/* Messages (newest at the bottom) */}
        {loading ? (
          <View style={styles.center}>
            <ActivityIndicator color="#fff" />
          </View>
        ) : (
          <FlatList
            data={messages}
            inverted
            keyExtractor={(m) => String(m.id)}
            renderItem={renderMessage}
            contentContainerStyle={{ paddingHorizontal: 12, paddingVertical: 10 }}
            ListEmptyComponent={
              <View style={[styles.center, { transform: [{ scaleY: -1 }] }]}>
                <Text style={styles.emptyText}>Say hi 👋</Text>
              </View>
            }
          />
        )}

        {error && <Text style={styles.error}>{error}</Text>}

        {/* Composer */}
        <View style={[styles.composer, { paddingBottom: Math.max(insets.bottom, 10) }]}>
          <Pressable onPress={onPhoto} hitSlop={8} style={styles.iconButton} disabled={sending}>
            <Ionicons name="image-outline" size={24} color="#aeaeb2" />
          </Pressable>
          <TextInput
            value={text}
            onChangeText={setText}
            placeholder="Message"
            placeholderTextColor="#8e8e93"
            style={[styles.input, isRTL(text) && { textAlign: 'right' }]}
            multiline
          />
          <Pressable
            onPress={onSend}
            disabled={!text.trim() || sending}
            style={[styles.send, (!text.trim() || sending) && { opacity: 0.4 }]}>
            {sending ? <ActivityIndicator color="#fff" size="small" /> : <Ionicons name="arrow-up" size={20} color="#fff" />}
          </Pressable>
        </View>
      </KeyboardAvoidingView>

      {playing && <VideoPlayerModal video={playing} onClose={() => setPlaying(null)} />}
      {info && conv?.is_group && (
        <GroupInfoModal
          conversationId={conversationId}
          name={conv.name}
          members={Object.values(members) as PersonProfile[]}
          onClose={() => setInfo(false)}
          onChanged={loadMeta}
          onLeft={() => {
            setInfo(false);
            onClose();
          }}
        />
      )}
    </Modal>
  );
}

// ---- One message bubble ----------------------------------------------------

function Bubble({ message, mine, onPlay }: { message: Message; mine: boolean; onPlay: (v: LearningVideo) => void }) {
  const time = formatTime(message.created_at);

  if (message.kind === 'image' && message.image_path) {
    return (
      <View style={[styles.bubble, mine ? styles.mine : styles.theirs, { padding: 4 }]}>
        <ChatImage path={message.image_path} />
        <Text style={[styles.time, { marginRight: 6 }]}>{time}</Text>
      </View>
    );
  }

  if (message.kind === 'video' && message.video_id) {
    const v = VIDEOS.find((x) => x.id === message.video_id);
    if (!v) return null;
    const course = getCourse(v.courseId);
    return (
      <Pressable onPress={() => onPlay(v)} style={[styles.bubble, mine ? styles.mine : styles.theirs, styles.videoCard]}>
        <View style={styles.videoThumb}>
          <Ionicons name="play" size={26} color="#fff" />
        </View>
        <View style={{ flex: 1 }}>
          <Text style={styles.videoCourse}>{(v.lang === 'he' ? course?.nameHe : course?.name) ?? ''}</Text>
          <Text style={[styles.videoTitle, v.lang === 'he' && styles.rtl]} numberOfLines={2}>
            {v.title}
          </Text>
          <Text style={styles.time}>{time}</Text>
        </View>
      </Pressable>
    );
  }

  const body = message.body ?? '';
  return (
    <View style={[styles.bubble, mine ? styles.mine : styles.theirs]}>
      <Text style={[styles.text, isRTL(body) && styles.rtl]}>{body}</Text>
      <Text style={styles.time}>{time}</Text>
    </View>
  );
}

function ChatImage({ path }: { path: string }) {
  const [url, setUrl] = useState<string | null>(null);
  const [full, setFull] = useState(false);
  useEffect(() => {
    imageUrl(path).then(setUrl);
  }, [path]);
  if (!url) return <View style={[styles.image, styles.center]}><ActivityIndicator color="#fff" /></View>;
  return (
    <>
      <Pressable onPress={() => setFull(true)}>
        <Image source={{ uri: url }} style={styles.image} contentFit="cover" />
      </Pressable>
      <Modal visible={full} transparent animationType="fade" onRequestClose={() => setFull(false)}>
        <Pressable style={styles.fullBackdrop} onPress={() => setFull(false)}>
          <Image source={{ uri: url }} style={StyleSheet.absoluteFill} contentFit="contain" />
        </Pressable>
      </Modal>
    </>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#000' },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingHorizontal: 10,
    paddingBottom: 10,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: '#2c2c2e',
    backgroundColor: '#0b0b0f',
  },
  back: { padding: 2 },
  headerCenter: { flex: 1, flexDirection: 'row', alignItems: 'center', gap: 10 },
  title: { color: '#fff', fontSize: 17, fontWeight: '800' },
  subtitle: { color: '#8e8e93', fontSize: 12 },
  row: { flexDirection: 'row', alignItems: 'flex-end', gap: 6, marginVertical: 2 },
  rowMine: { justifyContent: 'flex-end' },
  rowTheirs: { justifyContent: 'flex-start' },
  sender: { color: '#64d2ff', fontSize: 12, fontWeight: '700', marginBottom: 2, marginLeft: 8 },
  bubble: { borderRadius: 18, paddingHorizontal: 12, paddingVertical: 8 },
  mine: { backgroundColor: '#5e5ce6', borderBottomRightRadius: 6 },
  theirs: { backgroundColor: '#26262b', borderBottomLeftRadius: 6 },
  text: { color: '#fff', fontSize: 16, lineHeight: 21 },
  rtl: { textAlign: 'right', writingDirection: 'rtl' },
  time: { color: 'rgba(255,255,255,0.6)', fontSize: 10, alignSelf: 'flex-end', marginTop: 2 },
  system: { color: '#8e8e93', fontSize: 12, textAlign: 'center', marginVertical: 8 },
  videoCard: { flexDirection: 'row', alignItems: 'center', gap: 10, width: 250 },
  videoThumb: { width: 54, height: 76, borderRadius: 10, backgroundColor: 'rgba(0,0,0,0.35)', alignItems: 'center', justifyContent: 'center' },
  videoCourse: { color: 'rgba(255,255,255,0.7)', fontSize: 11, fontWeight: '700' },
  videoTitle: { color: '#fff', fontSize: 15, fontWeight: '800' },
  image: { width: 220, height: 260, borderRadius: 14, backgroundColor: '#1c1c1e' },
  fullBackdrop: { flex: 1, backgroundColor: '#000' },
  emptyText: { color: '#8e8e93', fontSize: 15, marginTop: 40 },
  error: { color: '#ff453a', fontSize: 13, paddingHorizontal: 16, paddingBottom: 4 },
  composer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    gap: 8,
    paddingHorizontal: 10,
    paddingTop: 8,
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: '#2c2c2e',
    backgroundColor: '#0b0b0f',
  },
  iconButton: { height: 40, justifyContent: 'center', paddingHorizontal: 4 },
  input: {
    flex: 1,
    color: '#fff',
    fontSize: 16,
    backgroundColor: '#1c1c1e',
    borderRadius: 20,
    paddingHorizontal: 14,
    paddingTop: 10,
    paddingBottom: 10,
    maxHeight: 120,
  },
  send: { width: 40, height: 40, borderRadius: 20, backgroundColor: '#5e5ce6', alignItems: 'center', justifyContent: 'center' },
});
