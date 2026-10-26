// A full-screen quiz card that appears in the feed between videos
// (how often is set in Settings → "How often to quiz me").

import { Ionicons } from '@expo/vector-icons';
import React, { useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { LEVEL_COLORS, LEVEL_LABELS } from '../data/courses';
import { isRTL, type Question } from '../data/sample';
import MathText from './MathText';

type Props = {
  question: Question;
  courseName: string;
  videoTitle: string;
  height: number;
  onAnswered: (questionId: string, correct: boolean) => void;
};

export default function QuestionCard({ question, courseName, videoTitle, height, onAnswered }: Props) {
  const [selected, setSelected] = useState<number | null>(null);
  const insets = useSafeAreaInsets();
  const answered = selected !== null;
  const isCorrect = selected === question.correctIndex;
  const he = isRTL(question.prompt);
  const dir = he ? styles.rtl : null;

  function choose(index: number) {
    if (answered) return;
    setSelected(index);
    onAnswered(question.id, index === question.correctIndex);
  }

  function optionStyle(index: number) {
    if (!answered) return styles.option;
    if (index === question.correctIndex) return [styles.option, styles.optionCorrect];
    if (index === selected) return [styles.option, styles.optionWrong];
    return [styles.option, styles.optionDim];
  }

  return (
    <View style={[styles.container, { height, paddingTop: insets.top + 70, paddingBottom: insets.bottom + 100 }]}>
      <View style={[styles.headerRow, he && { flexDirection: 'row-reverse' }]}>
        <View style={styles.quizBadge}>
          <Ionicons name="flash" size={14} color="#000" />
          <Text style={styles.quizBadgeText}>{he ? 'זמן חידון' : 'QUIZ TIME'}</Text>
        </View>
        <View style={[styles.levelBadge, { borderColor: LEVEL_COLORS[question.level] }]}>
          <Text style={[styles.levelText, { color: LEVEL_COLORS[question.level] }]}>
            {LEVEL_LABELS[question.level]}
          </Text>
        </View>
      </View>

      <Text style={[styles.context, dir]}>
        {courseName} · from “{videoTitle}”
      </Text>
      <MathText style={[styles.prompt, dir]} text={question.prompt} />

      {question.options.map((option, i) => (
        <Pressable key={i} style={optionStyle(i)} onPress={() => choose(i)}>
          <MathText style={[styles.optionText, dir]} text={option} mode="inline" />
        </Pressable>
      ))}

      {answered && (
        <View style={styles.feedback}>
          <Text style={[styles.feedbackTitle, dir, { color: isCorrect ? '#30d158' : '#ff453a' }]}>
            {isCorrect ? (he ? 'נכון!' : 'Correct!') : he ? 'לא בדיוק' : 'Not quite'}
          </Text>
          <MathText style={[styles.feedbackText, dir]} text={question.explanation} />
        </View>
      )}

      <View style={styles.swipeHint}>
        <Ionicons name="chevron-up" size={18} color="#8e8e93" />
        <Text style={styles.swipeText}>{answered ? (he ? 'החלק למעלה להמשך' : 'Swipe up to keep going') : he ? 'החלק למעלה כדי לדלג' : 'Swipe up to skip'}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  rtl: { textAlign: 'right', writingDirection: 'rtl' },
  container: { width: '100%', backgroundColor: '#0b0b1a', paddingHorizontal: 20 },
  headerRow: { flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 14 },
  quizBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    backgroundColor: '#ffd60a',
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 999,
  },
  quizBadgeText: { color: '#000', fontSize: 12, fontWeight: '900', letterSpacing: 1 },
  levelBadge: { borderWidth: 1.5, borderRadius: 999, paddingHorizontal: 10, paddingVertical: 4 },
  levelText: { fontSize: 12, fontWeight: '800' },
  context: { color: '#8e8e93', fontSize: 13, marginBottom: 8 },
  prompt: { color: '#fff', fontSize: 22, fontWeight: '800', marginBottom: 20, lineHeight: 29 },
  option: {
    backgroundColor: '#1c1c1e',
    padding: 15,
    borderRadius: 14,
    marginBottom: 10,
    borderWidth: 2,
    borderColor: 'transparent',
  },
  optionCorrect: { borderColor: '#30d158', backgroundColor: '#12351d' },
  optionWrong: { borderColor: '#ff453a', backgroundColor: '#3a1614' },
  optionDim: { opacity: 0.5 },
  optionText: { color: '#fff', fontSize: 16 },
  feedback: { marginTop: 6 },
  feedbackTitle: { fontSize: 17, fontWeight: '800', marginBottom: 4 },
  feedbackText: { color: '#d1d1d6', fontSize: 15, lineHeight: 21 },
  swipeHint: { marginTop: 'auto', alignItems: 'center' },
  swipeText: { color: '#8e8e93', fontSize: 13, fontWeight: '600' },
});
