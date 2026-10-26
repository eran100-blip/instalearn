// "Read more" bottom sheet: the full explanation of the video's definition,
// plus a memory tip when there is one.

import { Ionicons } from '@expo/vector-icons';
import React from 'react';
import { Modal, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import MathText from './MathText';
import type { LearningVideo } from '../data/sample';

type Props = {
  visible: boolean;
  video: LearningVideo;
  courseName: string;
  onClose: () => void;
};

export default function ExplanationSheet({ visible, video, courseName, onClose }: Props) {
  const he = video.lang === 'he';
  const dir = he ? styles.rtl : null;

  return (
    <Modal visible={visible} transparent animationType="slide" onRequestClose={onClose}>
      <Pressable style={styles.backdrop} onPress={onClose}>
        <Pressable style={styles.sheet} onPress={() => {}}>
          <View style={styles.handle} />
          <ScrollView showsVerticalScrollIndicator={false}>
            <Text style={[styles.course, dir]}>
              {courseName} · {video.topic}
            </Text>
            <Text style={[styles.title, dir]}>{video.title}</Text>
            {video.subtitle && <Text style={[styles.subtitle, dir]}>{video.subtitle}</Text>}

            <View style={styles.defBox}>
              <Text style={[styles.defLabel, dir]}>{he ? 'הגדרה' : 'DEFINITION'}</Text>
              <MathText style={[styles.defText, dir]} text={video.definition} />
            </View>

            <MathText style={[styles.body, dir]} text={video.explanation} />

            {video.tip && (
              <View style={[styles.tipBox, he && { flexDirection: 'row-reverse' }]}>
                <Ionicons name="bulb" size={22} color="#ffd60a" />
                <View style={{ flex: 1 }}>
                  <Text style={[styles.tipLabel, dir]}>{he ? 'טיפ לזכירה' : 'MEMORY TIP'}</Text>
                  <MathText style={[styles.tipText, dir]} text={video.tip} />
                </View>
              </View>
            )}
          </ScrollView>

          <Pressable style={styles.closeButton} onPress={onClose}>
            <Text style={styles.closeText}>{he ? 'הבנתי' : 'Got it'}</Text>
          </Pressable>
        </Pressable>
      </Pressable>
    </Modal>
  );
}

const styles = StyleSheet.create({
  rtl: { textAlign: 'right', writingDirection: 'rtl' },
  backdrop: { flex: 1, justifyContent: 'flex-end', backgroundColor: 'rgba(0,0,0,0.6)' },
  sheet: {
    backgroundColor: '#1c1c1e',
    paddingHorizontal: 20,
    paddingTop: 10,
    paddingBottom: 36,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    maxHeight: '80%',
  },
  handle: { alignSelf: 'center', width: 40, height: 5, borderRadius: 3, backgroundColor: '#48484a', marginBottom: 14 },
  course: { color: '#8e8e93', fontSize: 13, fontWeight: '600', marginBottom: 4 },
  title: { color: '#fff', fontSize: 24, fontWeight: '800' },
  subtitle: { color: '#64d2ff', fontSize: 17, fontWeight: '600', marginTop: 2 },
  defBox: { backgroundColor: '#2c2c2e', borderRadius: 14, padding: 14, marginTop: 14 },
  defLabel: { color: '#8e8e93', fontSize: 11, fontWeight: '800', letterSpacing: 1, marginBottom: 4 },
  defText: { color: '#fff', fontSize: 16, fontWeight: '600', lineHeight: 22 },
  body: { color: '#d1d1d6', fontSize: 16, lineHeight: 24, marginTop: 14 },
  tipBox: {
    flexDirection: 'row',
    gap: 10,
    backgroundColor: '#3a3000',
    borderRadius: 14,
    padding: 14,
    marginTop: 16,
    borderWidth: 1,
    borderColor: '#665400',
  },
  tipLabel: { color: '#ffd60a', fontSize: 11, fontWeight: '800', letterSpacing: 1, marginBottom: 4 },
  tipText: { color: '#fff', fontSize: 15, lineHeight: 21 },
  closeButton: { marginTop: 14, backgroundColor: '#0a84ff', padding: 14, borderRadius: 12, alignItems: 'center' },
  closeText: { color: '#fff', fontSize: 16, fontWeight: '700' },
});
