// Full-screen player for a video that was shared in a chat.

import { Ionicons } from '@expo/vector-icons';
import { useVideoPlayer, VideoView } from 'expo-video';
import React, { useState } from 'react';
import { Modal, Pressable, StyleSheet, Text, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import ExplanationSheet from '../ExplanationSheet';
import { getCourse } from '../../data/courses';
import type { LearningVideo } from '../../data/sample';

export default function VideoPlayerModal({ video, onClose }: { video: LearningVideo; onClose: () => void }) {
  const insets = useSafeAreaInsets();
  const [more, setMore] = useState(false);
  const player = useVideoPlayer(video.video, (p) => {
    p.loop = true;
    p.play();
  });
  const course = getCourse(video.courseId);
  const courseName = (video.lang === 'he' ? course?.nameHe : course?.name) ?? '';

  return (
    <Modal visible animationType="slide" presentationStyle="fullScreen" onRequestClose={onClose}>
      <View style={styles.screen}>
        <VideoView player={player} style={StyleSheet.absoluteFill} contentFit="cover" nativeControls={false} />
        <Pressable style={[styles.close, { top: insets.top + 8 }]} onPress={onClose} hitSlop={10}>
          <Ionicons name="close" size={26} color="#fff" />
        </Pressable>
        <Pressable style={[styles.more, { bottom: insets.bottom + 24 }]} onPress={() => setMore(true)}>
          <Ionicons name="book-outline" size={16} color="#fff" />
          <Text style={styles.moreText}>{video.lang === 'he' ? 'קרא עוד' : 'Read more'}</Text>
        </Pressable>
        <ExplanationSheet visible={more} video={video} courseName={courseName} onClose={() => setMore(false)} />
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#000' },
  close: {
    position: 'absolute',
    left: 14,
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(0,0,0,0.5)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  more: {
    position: 'absolute',
    alignSelf: 'center',
    flexDirection: 'row',
    gap: 6,
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.18)',
    borderRadius: 999,
    paddingHorizontal: 18,
    height: 40,
  },
  moreText: { color: '#fff', fontSize: 15, fontWeight: '700' },
});
