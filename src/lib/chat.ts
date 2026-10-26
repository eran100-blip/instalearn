// Chat helpers: types, sending messages, images, time formatting.

import * as ImagePicker from 'expo-image-picker';
import { supabase } from './supabase';

export type ConversationSummary = {
  id: string;
  is_group: boolean;
  name: string | null;
  last_message_at: string;
  last_message_preview: string | null;
  unread: number;
  member_count: number;
  other_id: string | null;
  other_name: string | null;
  other_username: string | null;
  other_avatar: string | null;
};

export type Message = {
  id: number;
  conversation_id: string;
  sender_id: string;
  kind: 'text' | 'video' | 'image' | 'system';
  body: string | null;
  video_id: string | null;
  image_path: string | null;
  created_at: string;
};

export type PersonProfile = {
  id: string;
  full_name: string | null;
  username: string | null;
  avatar_url: string | null;
};

export function conversationTitle(c: ConversationSummary) {
  if (c.is_group) return c.name || 'Group';
  return c.other_name || (c.other_username ? `@${c.other_username}` : 'Student');
}

export function displayName(p?: PersonProfile | null) {
  return p?.full_name || (p?.username ? `@${p.username}` : 'Student');
}

// "14:05" for today, "Yesterday", or "7/10".
export function formatTime(iso: string) {
  const d = new Date(iso);
  const now = new Date();
  const sameDay = d.toDateString() === now.toDateString();
  if (sameDay) return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  const y = new Date(now);
  y.setDate(now.getDate() - 1);
  if (d.toDateString() === y.toDateString()) return 'Yesterday';
  return `${d.getDate()}/${d.getMonth() + 1}`;
}

export async function sendText(conversationId: string, text: string) {
  const body = text.trim();
  if (!body) return null;
  const { error } = await supabase.from('messages').insert({ conversation_id: conversationId, kind: 'text', body });
  return error?.message ?? null;
}

export async function sendVideo(conversationId: string, videoId: string) {
  const { error } = await supabase.from('messages').insert({ conversation_id: conversationId, kind: 'video', video_id: videoId });
  return error?.message ?? null;
}

export async function markRead(conversationId: string, userId: string) {
  await supabase
    .from('conversation_members')
    .update({ last_read_at: new Date().toISOString() })
    .eq('conversation_id', conversationId)
    .eq('user_id', userId);
}

// ---- Images ---------------------------------------------------------------

const B64 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
function base64ToBytes(b64: string): Uint8Array {
  const clean = b64.replace(/[^A-Za-z0-9+/]/g, '');
  const out = new Uint8Array(Math.floor((clean.length * 3) / 4));
  let o = 0;
  for (let i = 0; i < clean.length; i += 4) {
    const n =
      (B64.indexOf(clean[i]) << 18) |
      (B64.indexOf(clean[i + 1]) << 12) |
      ((B64.indexOf(clean[i + 2]) & 63) << 6) |
      (B64.indexOf(clean[i + 3]) & 63);
    out[o++] = (n >> 16) & 255;
    if (i + 2 < clean.length) out[o++] = (n >> 8) & 255;
    if (i + 3 < clean.length) out[o++] = n & 255;
  }
  return out.slice(0, o);
}

// Let the user pick a photo, upload it, and send it. Returns an error message or null.
export async function pickAndSendImage(conversationId: string): Promise<string | null> {
  const res = await ImagePicker.launchImageLibraryAsync({ mediaTypes: ['images'], base64: true, quality: 0.6 });
  if (res.canceled || !res.assets?.[0]?.base64) return null;
  const asset = res.assets[0];
  const type = asset.mimeType ?? 'image/jpeg';
  const ext = type.includes('png') ? 'png' : 'jpg';
  const path = `${conversationId}/${Date.now()}-${Math.random().toString(36).slice(2, 8)}.${ext}`;
  const { error: upErr } = await supabase.storage
    .from('chat-images')
    .upload(path, base64ToBytes(asset.base64!), { contentType: type });
  if (upErr) return upErr.message;
  const { error } = await supabase.from('messages').insert({ conversation_id: conversationId, kind: 'image', image_path: path });
  return error?.message ?? null;
}

// Signed (temporary) links for private images, cached for the session.
const urlCache = new Map<string, { url: string; expires: number }>();
export async function imageUrl(path: string): Promise<string | null> {
  const hit = urlCache.get(path);
  if (hit && hit.expires > Date.now()) return hit.url;
  const { data } = await supabase.storage.from('chat-images').createSignedUrl(path, 3600);
  if (!data?.signedUrl) return null;
  urlCache.set(path, { url: data.signedUrl, expires: Date.now() + 50 * 60 * 1000 });
  return data.signedUrl;
}
