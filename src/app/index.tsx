import { Ionicons } from '@expo/vector-icons';
import { router } from 'expo-router';
import React, { useCallback, useMemo, useRef, useState } from 'react';
import {
  ActivityIndicator,
  FlatList,
  LayoutChangeEvent,
  Pressable,
  StatusBar,
  StyleSheet,
  Text,
  View,
  ViewToken,
} from 'react-native';

import GradCap from '../components/GradCap';
import QuestionCard from '../components/QuestionCard';
import VideoCard from '../components/VideoCard';
import { useAuth } from '../context/auth';
import { useSettings } from '../context/settings';
import { supabase } from '../lib/supabase';
import { getCourse } from '../data/courses';
import { pickQuestion, VIDEOS, type LearningVideo, type Question } from '../data/sample';

// The feed is a list of videos, with quiz cards mixed in between them.
type FeedItem =
  | { kind: 'video'; key: string; video: LearningVideo; question: Question | null }
  | { kind: 'quiz'; key: string; video: LearningVideo; question: Question };

export default function FeedScreen() {
  const { settings, loaded, levelFor } = useSettings();
  const [height, setHeight] = useState(0);
  const [activeIndex, setActiveIndex] = useState(0);

  // Every answer is recorded here. Later this will be saved to the database
  // (the "attempts" table) so we can find the user's weak topics.
  const attempts = useRef<{ questionId: string; correct: boolean; at: number }[]>([]);

  const { session } = useAuth();
  const userId = session?.user.id;

  const onAnswered = useCallback((questionId: string, isCorrect: boolean) => {
    attempts.current.push({ questionId, correct: isCorrect, at: Date.now() });
    // Save the answer to the user's account (used for stats and weak topics).
    if (userId) {
      const video = VIDEOS.find((v) => v.questions.some((q) => q.id === questionId));
      supabase
        .from('attempts')
        .insert({ user_id: userId, question_id: questionId, video_id: video?.id, course_id: video?.courseId, correct: isCorrect })
        .then(() => {});
    }
  }, [userId]);

  // Build the feed from the courses chosen in Settings.
  const feed = useMemo<FeedItem[]>(() => {
    // Mix the courses: take one video from each selected course in turn,
    // so the feed doesn't show all of one course before the next.
    const byCourse = settings.selectedCourses.map((id) => VIDEOS.filter((v) => v.courseId === id));
    const videos: LearningVideo[] = [];
    for (let round = 0; byCourse.some((list) => round < list.length); round++) {
      byCourse.forEach((list) => {
        if (round < list.length) videos.push(list[round]);
      });
    }
    const items: FeedItem[] = [];
    let lastWithQuestion: { video: LearningVideo; question: Question } | null = null;

    videos.forEach((video, i) => {
      const question = pickQuestion(video, levelFor(video.courseId));
      items.push({ kind: 'video', key: video.id, video, question });
      if (question) lastWithQuestion = { video, question };

      // After every N videos, add a quiz card about a video the student just watched.
      const every = settings.questionEvery;
      if (every > 0 && (i + 1) % every === 0 && lastWithQuestion) {
        items.push({ kind: 'quiz', key: `quiz-${video.id}`, ...lastWithQuestion });
        lastWithQuestion = null;
      }
    });
    return items;
  }, [settings.selectedCourses, settings.questionEvery, levelFor]);

  // Start from the top whenever the settings change the feed.
  const feedKey = useMemo(() => feed.map((f) => f.key).join(','), [feed]);

  const onViewableItemsChanged = useRef(({ viewableItems }: { viewableItems: ViewToken[] }) => {
    if (viewableItems.length > 0 && viewableItems[0].index != null) {
      setActiveIndex(viewableItems[0].index);
    }
  }).current;

  const viewabilityConfig = useRef({ itemVisiblePercentThreshold: 80 }).current;

  function onLayout(e: LayoutChangeEvent) {
    setHeight(e.nativeEvent.layout.height);
  }

  // Hebrew videos show the Hebrew course name.
  const courseName = (v: LearningVideo) => {
    const c = getCourse(v.courseId);
    return (v.lang === 'he' ? c?.nameHe : c?.name) ?? v.courseId;
  };
  const goToSettings = () => router.navigate('/settings');

  // ---- Empty states -------------------------------------------------------

  if (!loaded) {
    return (
      <View style={[styles.container, styles.center]}>
        <ActivityIndicator color="#fff" />
      </View>
    );
  }

  if (settings.selectedCourses.length === 0 || feed.length === 0) {
    const noCourses = settings.selectedCourses.length === 0;
    return (
      <View style={[styles.container, styles.center, styles.emptyPadding]}>
        <StatusBar barStyle="light-content" />
        <GradCap size={110} onPress={goToSettings} />
        <Text style={styles.emptyTitle}>
          {noCourses ? 'Welcome to InstaLearn' : 'No videos here yet'}
        </Text>
        <Text style={styles.emptyText}>
          {noCourses
            ? 'Choose the courses you are studying, and your feed will fill up with short lessons from them.'
            : 'We don’t have videos for the courses you picked yet. Add another course to keep learning.'}
        </Text>
        <Pressable style={styles.emptyButton} onPress={goToSettings}>
          <Ionicons name="options" size={20} color="#fff" />
          <Text style={styles.emptyButtonText}>{noCourses ? 'Choose courses' : 'Edit my courses'}</Text>
        </Pressable>
      </View>
    );
  }

  // ---- The feed -----------------------------------------------------------

  return (
    <View style={styles.container} onLayout={onLayout}>
      <StatusBar barStyle="light-content" />
      {height > 0 && (
        <FlatList
          key={feedKey}
          data={feed}
          keyExtractor={(item) => item.key}
          renderItem={({ item, index }) =>
            item.kind === 'video' ? (
              <VideoCard
                video={item.video}
                courseName={courseName(item.video)}
                question={item.question}
                height={height}
                isActive={index === activeIndex}
                onAnswered={onAnswered}
              />
            ) : (
              <QuestionCard
                question={item.question}
                courseName={courseName(item.video)}
                videoTitle={item.video.title}
                height={height}
                onAnswered={onAnswered}
              />
            )
          }
          pagingEnabled
          snapToInterval={height}
          decelerationRate="fast"
          showsVerticalScrollIndicator={false}
          onViewableItemsChanged={onViewableItemsChanged}
          viewabilityConfig={viewabilityConfig}
          getItemLayout={(_, index) => ({ length: height, offset: height * index, index })}
          windowSize={3}
          maxToRenderPerBatch={2}
          initialNumToRender={1}
        />
      )}

    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000' },
  center: { alignItems: 'center', justifyContent: 'center' },
  emptyPadding: { paddingHorizontal: 32, paddingBottom: 60 },
  emptyTitle: { color: '#fff', fontSize: 26, fontWeight: '800', marginTop: 4, textAlign: 'center' },
  emptyText: { color: '#aeaeb2', fontSize: 16, lineHeight: 22, textAlign: 'center', marginTop: 10 },
  emptyButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    backgroundColor: '#5e5ce6',
    paddingHorizontal: 22,
    paddingVertical: 14,
    borderRadius: 999,
    marginTop: 24,
  },
  emptyButtonText: { color: '#fff', fontSize: 17, fontWeight: '800' },
});
