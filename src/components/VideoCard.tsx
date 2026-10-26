import React, { useEffect, useRef, useState } from 'react';
import { Platform, Pressable, StyleSheet, Text, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useVideoPlayer, VideoView } from 'expo-video';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import type { LearningVideo, Question } from '../data/sample';
import ShareSheet from './chat/ShareSheet';
import ExplanationSheet from './ExplanationSheet';
import QuestionModal from './QuestionModal';

type Props = {
  video: LearningVideo;
  courseName: string;
  // The question at the level chosen in Settings, or null when the
  // course is set to 0 (no questions).
  question: Question | null;
  height: number;
  isActive: boolean;
  onAnswered: (questionId: string, correct: boolean) => void;
};

export default function VideoCard({ video, courseName, question, height, isActive, onAnswered }: Props) {
  const [liked, setLiked] = useState(false);
  const [saved, setSaved] = useState(false);
  const [showQuestion, setShowQuestion] = useState(false);
  const [showMore, setShowMore] = useState(false);
  const [showShare, setShowShare] = useState(false);
  const he = video.lang === 'he';
  // Sit just above the floating tab bar (Learn / My courses).
  const insets = useSafeAreaInsets();
  const bottomSpace = insets.bottom + (Platform.OS === 'ios' ? 8 : 40);

  const player = useVideoPlayer(video.video, (p) => {
    p.loop = true;
  });

  // Only the video currently on screen plays.
  useEffect(() => {
    if (isActive) player.play();
    else player.pause();
  }, [isActive, player]);

  // Hold to pause: the video stops while the finger stays on the screen,
  // and continues when it is lifted. A short delay avoids pausing on swipes.
  const [held, setHeld] = useState(false);
  const holdTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  function onHoldStart() {
    holdTimer.current = setTimeout(() => {
      player.pause();
      setHeld(true);
    }, 180);
  }
  function onHoldEnd() {
    if (holdTimer.current) clearTimeout(holdTimer.current);
    holdTimer.current = null;
    if (held && isActive) player.play();
    setHeld(false);
  }

  function onShare() {
    setShowShare(true);
  }

  return (
    <View style={[styles.container, { height }]}>
      <VideoView
        player={player}
        style={StyleSheet.absoluteFill}
        contentFit="cover"
        nativeControls={false}
      />

      {/* Touch layer for hold-to-pause (sits under the buttons) */}
      <Pressable style={StyleSheet.absoluteFill} onPressIn={onHoldStart} onPressOut={onHoldEnd} />
      {held && (
        <View style={styles.pauseBadge} pointerEvents="none">
          <Ionicons name="pause" size={34} color="#fff" />
        </View>
      )}

      {/* Floating controls at the bottom – below the text in the clip, so nothing is hidden */}
      <View style={[styles.bottom, { paddingBottom: bottomSpace }]} pointerEvents="box-none">
        <View style={styles.stack} pointerEvents="box-none">
          <View style={[styles.buttonRow, he && { flexDirection: 'row-reverse' }]}>
            <Pressable
              style={({ pressed }) => [styles.button, styles.moreButton, pressed && styles.pressed]}
              onPress={() => setShowMore(true)}>
              <Ionicons name="book-outline" size={16} color="#fff" />
              <Text style={styles.buttonText}>{he ? 'קרא עוד' : 'Read more'}</Text>
            </Pressable>
            {question && (
              <Pressable
                style={({ pressed }) => [styles.button, styles.questionButton, pressed && styles.pressed]}
                onPress={() => setShowQuestion(true)}>
                <Ionicons name="help-circle-outline" size={17} color="#fff" />
                <Text style={styles.buttonText}>{he ? 'בחן את עצמך' : 'Test yourself'}</Text>
              </Pressable>
            )}
          </View>
          <View style={[styles.actionsRow, he && { flexDirection: 'row-reverse' }]}>
            <Action
              icon={liked ? 'heart' : 'heart-outline'}
              color={liked ? '#ff375f' : '#fff'}
              label={formatCount(video.likes + (liked ? 1 : 0))}
              onPress={() => setLiked(!liked)}
            />
            <Action
              icon={saved ? 'bookmark' : 'bookmark-outline'}
              color={saved ? '#ffd60a' : '#fff'}
              label={he ? (saved ? 'נשמר' : 'שמור') : saved ? 'Saved' : 'Save'}
              onPress={() => setSaved(!saved)}
            />
            <Action icon="chatbubble-ellipses-outline" label={he ? 'תגובות' : 'Comments'} />
            <Action icon="paper-plane-outline" label={he ? 'שתף' : 'Share'} onPress={onShare} />
          </View>

        </View>
      </View>

      <ShareSheet visible={showShare} video={video} courseName={courseName} onClose={() => setShowShare(false)} />

      <ExplanationSheet
        visible={showMore}
        video={video}
        courseName={courseName}
        onClose={() => setShowMore(false)}
      />

      {question && (
        <QuestionModal
          visible={showQuestion}
          question={question}
          onClose={() => setShowQuestion(false)}
          onAnswered={onAnswered}
        />
      )}
    </View>
  );
}

// 1234 -> "1.2K"
function formatCount(n: number) {
  return n >= 1000 ? `${(n / 1000).toFixed(1).replace(/\.0$/, '')}K` : String(n);
}

type ActionProps = {
  icon: keyof typeof Ionicons.glyphMap;
  label: string;
  color?: string;
  onPress?: () => void;
};

function Action({ icon, label, color = '#fff', onPress }: ActionProps) {
  return (
    <Pressable
      onPress={onPress}
      hitSlop={6}
      style={({ pressed }) => [styles.action, pressed && styles.pressed]}>
      <Ionicons name={icon} size={22} color={color} style={styles.iconShadow} />
      <Text style={styles.actionText}>{label}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  container: { width: '100%', backgroundColor: '#0b1220', justifyContent: 'flex-end' },
  bottom: { paddingHorizontal: 14 },
  stack: { gap: 12 },
  actionsRow: { flexDirection: 'row', justifyContent: 'space-around' },
  action: { alignItems: 'center', minWidth: 56, gap: 1 },
  iconShadow: { textShadowColor: 'rgba(0,0,0,0.7)', textShadowRadius: 8, textShadowOffset: { width: 0, height: 1 } },
  actionText: {
    color: '#fff',
    fontSize: 11,
    fontWeight: '600',
    textShadowColor: 'rgba(0,0,0,0.8)',
    textShadowRadius: 6,
    textShadowOffset: { width: 0, height: 1 },
  },
  buttonRow: { flexDirection: 'row', gap: 8 },
  button: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 6,
    height: 36,
    borderRadius: 999,
  },
  moreButton: {
    backgroundColor: 'rgba(255,255,255,0.16)',
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: 'rgba(255,255,255,0.35)',
  },
  questionButton: { backgroundColor: '#30d158' },
  buttonText: { color: '#fff', fontSize: 14, fontWeight: '700' },
  pressed: { opacity: 0.6, transform: [{ scale: 0.96 }] },
  pauseBadge: {
    position: 'absolute',
    alignSelf: 'center',
    top: '42%',
    width: 72,
    height: 72,
    borderRadius: 36,
    backgroundColor: 'rgba(0,0,0,0.45)',
    alignItems: 'center',
    justifyContent: 'center',
  },
});
