// The list of courses a student can pick in Settings.
// Later this will come from the database instead of this file.

export type Course = {
  id: string;
  name: string; // English name (shown in the app)
  nameHe: string; // Hebrew name (shown under it, and searchable)
  field: FieldId;
  factsOnly?: boolean; // enrichment course: facts only, no questions
};

export type FieldId = 'general' | 'math' | 'physics' | 'cs' | 'ee' | 'chem' | 'med' | 'law';

export const FIELDS: { id: FieldId; name: string; nameHe: string; icon: string; color: string }[] = [
  { id: 'general', name: 'General', nameHe: 'העשרה', icon: 'sparkles', color: '#5e5ce6' },
  { id: 'math', name: 'Mathematics', nameHe: 'מתמטיקה', icon: 'calculator', color: '#0a84ff' },
  { id: 'physics', name: 'Physics', nameHe: 'פיזיקה', icon: 'planet', color: '#bf5af2' },
  { id: 'cs', name: 'Computer Science', nameHe: 'מדעי המחשב', icon: 'code-slash', color: '#30d158' },
  { id: 'ee', name: 'Electrical Engineering', nameHe: 'הנדסת חשמל', icon: 'flash', color: '#ff9f0a' },
  { id: 'chem', name: 'Chemistry', nameHe: 'כימיה', icon: 'flask', color: '#ff375f' },
  { id: 'med', name: 'Medicine', nameHe: 'רפואה', icon: 'medkit', color: '#64d2ff' },
  { id: 'law', name: 'Law', nameHe: 'משפטים', icon: 'library', color: '#c08a2e' },
];

export const COURSES: Course[] = [
  // General enrichment
  { id: 'fun-facts', name: 'Fun Facts', nameHe: 'עובדות מעניינות', field: 'general', factsOnly: true },

  // Mathematics
  { id: 'calc1', name: 'Calculus 1', nameHe: 'חדו״א 1 (אינפי 1)', field: 'math' },
  { id: 'calc2', name: 'Calculus 2', nameHe: 'אינפי 2', field: 'math' },
  { id: 'vector-calc', name: 'Vector Calculus', nameHe: 'חדו״א וקטורית', field: 'math' },
  { id: 'linalg1', name: 'Linear Algebra 1', nameHe: 'אלגברה לינארית 1', field: 'math' },
  { id: 'linalg2', name: 'Linear Algebra 2', nameHe: 'אלגברה לינארית 2', field: 'math' },
  { id: 'discrete', name: 'Discrete Math', nameHe: 'מתמטיקה דיסקרטית', field: 'math' },
  { id: 'probability', name: 'Probability', nameHe: 'הסתברות', field: 'math' },
  { id: 'ode', name: 'Differential Equations', nameHe: 'משוואות דיפרנציאליות', field: 'math' },
  { id: 'complex', name: 'Complex Functions', nameHe: 'פונקציות מרוכבות', field: 'math' },

  // Physics
  { id: 'physics1', name: 'Physics 1 · Mechanics', nameHe: 'פיזיקה 1', field: 'physics' },
  { id: 'physics2', name: 'Physics 2 · Electricity & Magnetism', nameHe: 'פיזיקה 2', field: 'physics' },
  { id: 'physics3', name: 'Physics 3 · Waves & Modern Physics', nameHe: 'פיזיקה 3', field: 'physics' },
  { id: 'quantum', name: 'Quantum Mechanics', nameHe: 'מכניקת הקוונטים', field: 'physics' },

  // Computer Science
  { id: 'intro-cs', name: 'Intro to Programming', nameHe: 'מבוא למדעי המחשב', field: 'cs' },
  { id: 'data-structures', name: 'Data Structures', nameHe: 'מבני נתונים', field: 'cs' },
  { id: 'algorithms', name: 'Algorithms', nameHe: 'אלגוריתמים', field: 'cs' },
  { id: 'computability', name: 'Computational Models', nameHe: 'מודלים חישוביים', field: 'cs' },

  // Electrical Engineering
  { id: 'circuits', name: 'Electric Circuits', nameHe: 'מעגלים חשמליים', field: 'ee' },
  { id: 'signals', name: 'Signals & Systems', nameHe: 'אותות ומערכות', field: 'ee' },

  // Chemistry
  { id: 'chem', name: 'General Chemistry', nameHe: 'כימיה כללית', field: 'chem' },

  // Medicine
  { id: 'anatomy', name: 'Anatomy', nameHe: 'אנטומיה', field: 'med' },

  // Law
  { id: 'bar-prep', name: 'Bar Exam Prep', nameHe: 'הכנה לבחינת הלשכה', field: 'law' },
];

export function getCourse(id: string): Course | undefined {
  return COURSES.find((c) => c.id === id);
}

// Question difficulty per course: 0 = no questions, 1 = easy, 2 = medium, 3 = hard.
export type QuestionLevel = 0 | 1 | 2 | 3;

export const LEVEL_LABELS: Record<QuestionLevel, string> = {
  0: 'No questions',
  1: 'Easy',
  2: 'Medium',
  3: 'Hard',
};

export const LEVEL_COLORS: Record<QuestionLevel, string> = {
  0: '#8e8e93',
  1: '#30d158',
  2: '#ffd60a',
  3: '#ff453a',
};
