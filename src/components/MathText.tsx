// Shows Hebrew text that contains math so the math stays readable:
// - every formula is wrapped in a bidi isolate, so its characters keep their LTR order;
// - in "block" mode, a real equation (has =, <, ≥ … or is long) is moved to its own line,
//   kept on ONE line (it shrinks to fit instead of wrapping), left-to-right.

import React from 'react';
import { StyleSheet, Text, View, type StyleProp, type TextStyle } from 'react-native';

const HEB = /[֐-׿]/;
const RUN = /[^֐-׿]+/g;
const MATHY = /[A-Za-z0-9∞π∫ε-ωᵃ-ᶻ√]/;
const RELATION = /[=≈≤≥<>≠→]/;
const LRI = '⁦';
const PDI = '⁩';
const EDGE_L = ' ,.:;!?״)=≈';
const EDGE_R = ' ,.:;!?״(=≈';

type Piece = { kind: 'text'; value: string } | { kind: 'math'; value: string };

/** Splits one paragraph into plain-text pieces and math pieces. */
function split(line: string): Piece[] {
  const out: Piece[] = [];
  let i = 0;
  for (const m of line.matchAll(RUN)) {
    const seg = m[0];
    const start = m.index ?? 0;
    let a = 0;
    let b = seg.length;
    for (let k = 0; k < 3; k++) {
      while (a < b && EDGE_L.includes(seg[a])) a++;
      while (b > a && EDGE_R.includes(seg[b - 1])) b--;
      const core = seg.slice(a, b);
      const open = (core.match(/\(/g) || []).length;
      const close = (core.match(/\)/g) || []).length;
      if (core.startsWith('(') && open > close) a++;
      if (core.endsWith(')') && close > open) b--;
    }
    const core = seg.slice(a, b);
    if (core && MATHY.test(core)) {
      if (start + a > i) out.push({ kind: 'text', value: line.slice(i, start + a) });
      out.push({ kind: 'math', value: core });
      i = start + b;
    }
  }
  if (i < line.length) out.push({ kind: 'text', value: line.slice(i) });
  return out;
}

function isEquation(s: string) {
  return (RELATION.test(s) && s.length >= 8) || s.length >= 16;
}

/** Text with every math run wrapped in an LTR isolate (for short strings like answer options). */
export function isolateMath(text: string): string {
  if (!HEB.test(text)) return text;
  return split(text)
    .map((p) => (p.kind === 'math' ? LRI + p.value + PDI : p.value))
    .join('');
}

type Props = {
  text: string;
  style?: StyleProp<TextStyle>;
  mode?: 'block' | 'inline';
};

export default function MathText({ text, style, mode = 'block' }: Props) {
  if (!HEB.test(text)) return <Text style={style}>{text}</Text>;
  if (mode === 'inline') return <Text style={style}>{isolateMath(text)}</Text>;

  // Margins belong to the whole block, not to every line inside it.
  const { margin, marginTop, marginBottom, marginVertical, ...textStyle } = StyleSheet.flatten(style) || {};
  style = textStyle;
  const nodes: React.ReactNode[] = [];
  let key = 0;
  for (const para of text.split('\n')) {
    if (!para.trim()) {
      nodes.push(<View key={key++} style={styles.gap} />);
      continue;
    }
    let buf = '';
    const pieces = split(para);
    for (let k = 0; k < pieces.length; k++) {
      const p = pieces[k];
      if (p.kind === 'math' && isEquation(p.value)) {
        if (buf.trim()) nodes.push(<Text key={key++} style={style}>{buf.trim()}</Text>);
        buf = '';
        let formula = p.value;
        // Punctuation right after the formula: keep "?"/"!" with it, drop separators.
        const next = pieces[k + 1];
        if (next && next.kind === 'text') {
          const q = next.value.match(/^\s*([?!])/);
          if (q) {
            formula += q[1];
            next.value = next.value.slice(q[0].length);
          }
          next.value = next.value.replace(/^\s*[,.:;]+\s*/, '');
        }
        nodes.push(
          <View key={key++} style={styles.formulaBox}>
            <Text style={[style, styles.formula]} numberOfLines={1} adjustsFontSizeToFit minimumFontScale={0.5}>
              {formula}
            </Text>
          </View>,
        );
      } else {
        buf += p.kind === 'math' ? LRI + p.value + PDI : p.value;
      }
    }
    if (buf.trim()) nodes.push(<Text key={key++} style={style}>{buf.trim()}</Text>);
  }
  return <View style={{ margin, marginTop, marginBottom, marginVertical }}>{nodes}</View>;
}

const styles = StyleSheet.create({
  gap: { height: 10 },
  formulaBox: {
    alignSelf: 'stretch',
    backgroundColor: 'rgba(255,255,255,0.07)',
    borderRadius: 10,
    paddingHorizontal: 12,
    paddingVertical: 6,
    marginVertical: 6,
  },
  formula: {
    textAlign: 'center',
    writingDirection: 'ltr',
    marginBottom: 0,
    marginTop: 0,
  },
});
