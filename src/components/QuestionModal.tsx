import React, { useEffect, useState } from 'react';
import { Modal, Pressable, StyleSheet, Text, View } from 'react-native';
import MathText from './MathText';
import { isRTL, type Question } from '../data/sample';

type Props = {
  visible: boolean;
  question: Question;
  onClose: () => void;
  // Called once per question when the user picks an answer.
  onAnswered: (questionId: string, correct: boolean) => void;
};

export default function QuestionModal({ visible, question, onClose, onAnswered }: Props) {
  const [selected, setSelected] = useState<number | null>(null);

  // Reset whenever a new question is opened.
  useEffect(() => {
    if (visible) setSelected(null);
  }, [visible, question.id]);

  const answered = selected !== null;
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
    <Modal visible={visible} transparent animationType="slide" onRequestClose={onClose}>
      <View style={styles.backdrop}>
        <View style={styles.sheet}>
          <Text style={[styles.label, dir]}>
            {he
              ? question.type === 'truefalse' ? 'נכון / לא נכון' : 'שאלה אמריקאית'
              : question.type === 'truefalse' ? 'TRUE / FALSE' : 'MULTIPLE CHOICE'}
          </Text>
          <MathText style={[styles.prompt, dir]} text={question.prompt} />

          {question.options.map((option, i) => (
            <Pressable key={i} style={optionStyle(i)} onPress={() => choose(i)}>
              <MathText style={[styles.optionText, dir]} text={option} mode="inline" />
            </Pressable>
          ))}

          {answered && (
            <View style={styles.feedback}>
              <Text style={[styles.feedbackTitle, dir]}>
                {selected === question.correctIndex ? (he ? 'נכון!' : 'Correct!') : he ? 'לא בדיוק' : 'Not quite'}
              </Text>
              <MathText style={[styles.feedbackText, dir]} text={question.explanation} />
            </View>
          )}

          <Pressable style={styles.closeButton} onPress={onClose}>
            <Text style={styles.closeText}>{answered ? (he ? 'המשך' : 'Continue') : he ? 'דלג' : 'Skip'}</Text>
          </Pressable>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  rtl: { textAlign: 'right', writingDirection: 'rtl' },
  backdrop: { flex: 1, justifyContent: 'flex-end', backgroundColor: 'rgba(0,0,0,0.6)' },
  sheet: {
    backgroundColor: '#1c1c1e',
    padding: 20,
    paddingBottom: 36,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
  },
  label: { color: '#8e8e93', fontSize: 12, fontWeight: '700', letterSpacing: 1, marginBottom: 8 },
  prompt: { color: '#fff', fontSize: 20, fontWeight: '700', marginBottom: 16 },
  option: {
    backgroundColor: '#2c2c2e',
    padding: 14,
    borderRadius: 12,
    marginBottom: 10,
    borderWidth: 2,
    borderColor: 'transparent',
  },
  optionCorrect: { borderColor: '#30d158', backgroundColor: '#12351d' },
  optionWrong: { borderColor: '#ff453a', backgroundColor: '#3a1614' },
  optionDim: { opacity: 0.5 },
  optionText: { color: '#fff', fontSize: 16 },
  feedback: { marginTop: 6, marginBottom: 6 },
  feedbackTitle: { color: '#fff', fontSize: 16, fontWeight: '700', marginBottom: 4 },
  feedbackText: { color: '#d1d1d6', fontSize: 15, lineHeight: 21 },
  closeButton: {
    marginTop: 14,
    backgroundColor: '#0a84ff',
    padding: 14,
    borderRadius: 12,
    alignItems: 'center',
  },
  closeText: { color: '#fff', fontSize: 16, fontWeight: '700' },
});
