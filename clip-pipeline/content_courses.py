"""Course videos (English). Each: 15s clip + definition (burned in) + explanation (Read more) + 3 questions."""
import numpy as np, math

TF = ['True', 'False']

def Q(qid, level, prompt, options, correct, expl):
    return dict(id=qid, level=level, type='truefalse' if options == TF else 'mcq',
                prompt=prompt, options=options, correctIndex=correct, explanation=expl)

def V(id, course, title, topic, definition, explanation, visual, questions):
    return dict(id=id, courseId=course, title=title, topic=topic, definition=definition,
                explanation=explanation, visual=visual, questions=questions, lang='en')

def circle_pos(names, r=0.36, aspect=290 / 552):
    n = len(names)
    return {nm: (0.5 + r * math.cos(2 * math.pi * i / n) * aspect * 1.0 / 1.0, 0.5 - r * 1.0 * math.sin(2 * math.pi * i / n) * 1.0)
            for i, nm in enumerate(names)}

VIDEOS = [
# ---------------------------------------------------------------- Calculus 2
V('v8', 'calc2', 'Integration by parts', 'Integrals',
  '∫u dv = uv − ∫v du. Use it when the integrand is a product of two different kinds of functions.',
  'Integration by parts is the product rule run backwards. Choose u as the part that gets simpler when differentiated '
  '(LIATE: Logs, Inverse trig, Algebraic, Trig, Exponential). Example: ∫x·eˣ dx with u = x, dv = eˣ dx gives (x − 1)eˣ + C.',
  dict(kind='formula', lines=['∫ u dv  =  uv − ∫ v du', 'u = x ,   dv = eˣ dx', '∫ x eˣ dx = (x − 1) eˣ + C'], size=34),
  [Q('q8-1', 1, 'What is ∫ 2x dx?', ['x² + C', '2x² + C', 'x + C', '2 + C'], 0,
     'The derivative of x² is 2x, so ∫ 2x dx = x² + C.'),
   Q('q8-2', 2, 'What is ∫ x·eˣ dx?', ['x·eˣ + C', '(x − 1)·eˣ + C', '(x + 1)·eˣ + C', 'x²·eˣ / 2 + C'], 1,
     'u = x, dv = eˣ dx → x·eˣ − ∫ eˣ dx = x·eˣ − eˣ + C = (x − 1)·eˣ + C.'),
   Q('q8-3', 3, 'What is ∫ ln(x) dx?', ['1/x + C', 'x·ln(x) − x + C', 'x·ln(x) + C', '(ln x)² / 2 + C'], 1,
     'u = ln x, dv = dx → x·ln x − ∫ x · (1/x) dx = x·ln x − x + C.')]),

V('v13', 'calc2', 'The definite integral = area', 'Integrals',
  '∫ from a to b of f(x) dx is the signed area between the graph and the x-axis.',
  'The definite integral is the limit of Riemann sums: slice [a, b] into thin rectangles and add f(xᵢ)·Δx. '
  'Area above the x-axis counts as positive and area below as negative. '
  'The Fundamental Theorem of Calculus lets us compute it with an antiderivative: ∫ₐᵇ f = F(b) − F(a).',
  dict(kind='plot', f='0.3*x**2+0.5', xr=(-0.5, 4), yr=(-0.5, 5.5), area=(1, 3), label='∫₁³ f(x) dx'),
  [Q('q13-1', 1, 'What is ∫ from 0 to 2 of 3 dx?', ['3', '5', '6', '9'], 2,
     'It is the area of a rectangle with height 3 and width 2: 3 · 2 = 6.'),
   Q('q13-2', 2, 'What is ∫ from 0 to 1 of x² dx?', ['1/2', '1/3', '1', '2/3'], 1,
     'An antiderivative is x³/3, so the value is 1/3 − 0 = 1/3.'),
   Q('q13-3', 3, 'True or false: ∫ from −1 to 1 of x³ dx = 0.', TF, 0,
     'x³ is an odd function: the negative area on [−1, 0] exactly cancels the positive area on [0, 1].')]),

V('v14', 'calc2', 'Taylor series', 'Series',
  'A Taylor polynomial approximates a function near a point using its derivatives there.',
  'The Taylor series of f around 0 is Σ f⁽ⁿ⁾(0)/n! · xⁿ. Near 0, sin x ≈ x − x³/6, and adding more terms makes the approximation good over a wider range. '
  'The error is controlled by the next term (Lagrange remainder).',
  dict(kind='plot', f='np.sin(x)', f2='x - x**3/6', xr=(-4, 4), yr=(-2, 2), label='sin x   vs   x − x³/6'),
  [Q('q14-1', 1, 'What is the first non-zero term of the Taylor series of sin x around 0?', ['1', 'x', 'x²/2', '−x³/6'], 1,
     'sin 0 = 0 and its derivative cos 0 = 1, so the series starts with x.'),
   Q('q14-2', 2, 'What is the Taylor series of eˣ around 0?', ['Σ xⁿ', 'Σ xⁿ / n!', 'Σ n·xⁿ', 'Σ (−1)ⁿ xⁿ'], 1,
     'Every derivative of eˣ equals 1 at 0, so the coefficients are 1/n!.'),
   Q('q14-3', 3, 'For which x does the geometric series Σ xⁿ converge?', ['All x', '|x| < 1', 'x > 0', '|x| ≤ 1'], 1,
     'It converges to 1/(1 − x) exactly when |x| < 1; at x = ±1 the terms do not go to 0.')]),

# ---------------------------------------------------------------- Vector calculus
V('v9', 'vector-calc', 'The gradient', 'Partial derivatives',
  '∇f is the vector of partial derivatives. It points where f increases fastest.',
  'For f(x, y), ∇f = (∂f/∂x, ∂f/∂y). Its length is the maximal rate of increase, and it is perpendicular to the level curves of f. '
  'For f = x² + y² the gradient (2x, 2y) points straight away from the origin.',
  dict(kind='vectors', fx='x', fy='y', label='∇(x² + y²) = (2x, 2y)'),
  [Q('q9-1', 1, 'What is the gradient of f(x, y) = x² + y²?', ['(2x, 2y)', '(x, y)', '2x + 2y', '(x², y²)'], 0,
     '∇f = (∂f/∂x, ∂f/∂y) = (2x, 2y).'),
   Q('q9-2', 2, 'True or false: the gradient points in the direction in which f increases the fastest.', TF, 0,
     'The directional derivative ∇f · u is largest when u points in the same direction as ∇f.'),
   Q('q9-3', 3, 'For a smooth function f, what is curl(∇f)?', ['The zero vector', '∇f itself', 'The Laplacian of f', 'It depends on f'], 0,
     'Mixed partial derivatives are equal (Schwarz), so every component of ∇ × ∇f cancels out.')]),

V('v15', 'vector-calc', 'Curl: how a field rotates', 'Vector fields',
  'The curl ∇ × F measures how much a vector field spins around a point.',
  'For a 2D field F = (P, Q) the curl is ∂Q/∂x − ∂P/∂y. The field (−y, x) circulates around the origin and has curl 2 everywhere. '
  'Fields with zero curl (on simply connected domains) are gradients of a potential — they are conservative.',
  dict(kind='vectors', fx='-y', fy='x', label='F = (−y, x)   ·   curl F = 2'),
  [Q('q15-1', 1, 'True or false: a field with curl ≠ 0 has some rotation in it.', TF, 0,
     'The curl measures local rotation; non-zero curl means a tiny paddle wheel would spin.'),
   Q('q15-2', 2, 'What is the (2D) curl of F = (−y, x)?', ['0', '1', '2', '−2'], 2,
     'curl = ∂Q/∂x − ∂P/∂y = ∂(x)/∂x − ∂(−y)/∂y = 1 − (−1) = 2.'),
   Q('q15-3', 3, 'Which theorem relates the circulation around a closed curve to the curl inside it (in the plane)?',
     ["Green's theorem", "Gauss's theorem", "Rolle's theorem", 'The mean value theorem'], 0,
     "Green's theorem: ∮ P dx + Q dy = ∬ (∂Q/∂x − ∂P/∂y) dA.")]),

# ---------------------------------------------------------------- Linear algebra 1
V('v10', 'linalg1', 'Determinants, visually', 'Determinants',
  'det(A) is the factor by which A scales area. det = 0 means space gets squashed.',
  'Apply A to the unit square: the image is a parallelogram whose (signed) area is det(A). '
  'A negative determinant means orientation flips. A is invertible exactly when det(A) ≠ 0, and det(AB) = det(A)·det(B).',
  dict(kind='matrix', A=[[2, 1], [0.5, 1.5]]),
  [Q('q10-1', 1, 'What is the determinant of [[1, 2], [3, 4]]?', ['−2', '2', '10', '−10'], 0,
     'det = 1·4 − 2·3 = 4 − 6 = −2.'),
   Q('q10-2', 2, 'True or false: if det(A) = 0, then A is invertible.', TF, 1,
     'It is the opposite: A is invertible exactly when det(A) ≠ 0.'),
   Q('q10-3', 3, 'A is a 3×3 matrix with det(A) = 5. What is det(2A)?', ['10', '20', '40', '30'], 2,
     'Each of the 3 rows is multiplied by 2, so det(2A) = 2³ · det(A) = 8 · 5 = 40.')]),

V('v16', 'linalg1', 'Gaussian elimination', 'Linear systems',
  'Use row operations to turn a system into triangular form, then back-substitute.',
  'Allowed row operations: swap two rows, multiply a row by a non-zero number, add a multiple of one row to another. '
  'They never change the solution set. Once the matrix is in row echelon form, solve from the bottom row up.',
  dict(kind='formula', lines=['x + 2y = 5', '3x + 4y = 11', 'R₂ → R₂ − 3R₁', '−2y = −4  ⇒  y = 2,  x = 1'], size=34),
  [Q('q16-1', 1, 'Which of these is NOT an allowed row operation?', ['Swap two rows', 'Multiply a row by 0', 'Add 2×(row 1) to row 2', 'Multiply a row by 5'], 1,
     'Multiplying a row by 0 destroys information and can change the solution set.'),
   Q('q16-2', 2, 'Solve: x + y = 3, x − y = 1.', ['x = 1, y = 2', 'x = 2, y = 1', 'x = 3, y = 0', 'No solution'], 1,
     'Adding the equations: 2x = 4, so x = 2 and y = 1.'),
   Q('q16-3', 3, 'A 3×3 system has a row 0 0 0 | 5 after elimination. The system has…', ['One solution', 'Infinitely many solutions', 'No solution', 'Exactly 5 solutions'], 2,
     'That row says 0 = 5, a contradiction, so the system is inconsistent.')]),

# ---------------------------------------------------------------- Linear algebra 2
V('v17', 'linalg2', 'Eigenvectors', 'Eigenvalues',
  'An eigenvector keeps its direction under A: Av = λv. λ is the stretch factor.',
  'Find eigenvalues from det(A − λI) = 0, then solve (A − λI)v = 0 for each λ. '
  'For A = [[2, 1], [1, 2]] the eigenvalues are 3 (direction (1, 1)) and 1 (direction (1, −1)). '
  'Symmetric matrices always have real eigenvalues and orthogonal eigenvectors.',
  dict(kind='matrix', A=[[2, 1], [1, 2]], eig=[(1, 1), (1, -1)]),
  [Q('q17-1', 1, 'If Av = 3v, what is the eigenvalue?', ['v', '3', 'A', '0'], 1,
     'In Av = λv the scalar λ is the eigenvalue — here 3.'),
   Q('q17-2', 2, 'What are the eigenvalues of [[2, 0], [0, 5]]?', ['2 and 5', '0 and 7', '7 and 10', '1 and 1'], 0,
     'For a diagonal (or triangular) matrix the eigenvalues are the diagonal entries.'),
   Q('q17-3', 3, 'True or false: the sum of the eigenvalues equals the trace of the matrix.', TF, 0,
     'The trace equals the sum of the eigenvalues (with multiplicity), and the determinant equals their product.')]),

V('v18', 'linalg2', 'Inner product & orthogonality', 'Inner product spaces',
  'u · v = |u||v|cos θ. Two vectors are orthogonal when their inner product is 0.',
  'The inner product measures length (|u|² = u·u) and angle. Orthogonal vectors are linearly independent, '
  'and orthonormal bases make computing coordinates easy: the coordinate of v on eᵢ is just v·eᵢ. Gram–Schmidt turns any basis into an orthonormal one.',
  dict(kind='formula', lines=['u · v = |u| |v| cos θ', 'u · v = 0   ⇔   u ⊥ v', '(1, 2) · (2, −1) = 0'], size=36),
  [Q('q18-1', 1, 'What is (1, 2) · (3, 4)?', ['7', '10', '11', '14'], 2, '1·3 + 2·4 = 3 + 8 = 11.'),
   Q('q18-2', 2, 'Which vector is orthogonal to (1, 1)?', ['(1, 1)', '(1, −1)', '(2, 2)', '(0, 1)'], 1, '(1, 1)·(1, −1) = 1 − 1 = 0.'),
   Q('q18-3', 3, 'Which process converts a basis into an orthonormal basis?', ['Gaussian elimination', 'Gram–Schmidt', 'Diagonalization', "Cramer's rule"], 1,
     'Gram–Schmidt subtracts projections onto earlier vectors and normalizes.')]),

# ---------------------------------------------------------------- Discrete math
V('v7', 'discrete', 'The pigeonhole principle', 'Combinatorics',
  'Put n + 1 items into n boxes, and some box must hold at least two.',
  'General form: if N items go into k boxes, some box has at least ⌈N/k⌉ items. '
  'The trick in proofs is choosing the right “boxes” — e.g. pairs {1,2}, {3,4}, … to show that 51 numbers from 1…100 include two consecutive ones.',
  dict(kind='formula', lines=['13 people', '12 months', '⇒ 2 share a birth month'], size=40),
  [Q('q7-1', 1, 'True or false: in any group of 13 people, at least two were born in the same month.', TF, 0,
     '13 people (pigeons), 12 months (holes). At least one month must get two people.'),
   Q('q7-2', 2, 'A drawer has socks in 3 colors. How many must you take to be sure of a matching pair?', ['2', '3', '4', '6'], 2,
     'With 3 socks you might get one of each color. The 4th sock must match one of them.'),
   Q('q7-3', 3, 'True or false: any 51 numbers chosen from 1…100 include two consecutive numbers.', TF, 0,
     'Split 1…100 into 50 pairs {1,2}, {3,4}, …, {99,100}. 51 numbers in 50 pairs means some pair is fully chosen.')]),

V('v19', 'discrete', 'The handshake lemma', 'Graph theory',
  'In every graph, the sum of all vertex degrees equals twice the number of edges.',
  'Each edge has two ends, so it adds 1 to the degree of two vertices: Σ deg(v) = 2|E|. '
  'Consequence: the number of vertices with odd degree is always even.',
  dict(kind='graph', nodes={'A': (0.2, 0.3), 'B': (0.5, 0.18), 'C': (0.8, 0.3), 'D': (0.68, 0.8), 'E': (0.32, 0.8)},
       edges=[('A', 'B'), ('B', 'C'), ('C', 'D'), ('D', 'E'), ('E', 'A'), ('A', 'C'), ('B', 'D')], order=['A', 'B', 'C', 'D', 'E'],
       label='Σ deg(v) = 2|E| = 14'),
  [Q('q19-1', 1, 'A graph has 5 edges. What is the sum of all degrees?', ['5', '10', '25', 'It depends'], 1, 'Σ deg = 2|E| = 2 · 5 = 10.'),
   Q('q19-2', 2, 'Can a graph have exactly 3 vertices of odd degree?', ['Yes', 'No'], 1,
     'The number of odd-degree vertices is always even, because the total degree sum is even.'),
   Q('q19-3', 3, 'How many edges does the complete graph K₆ have?', ['12', '15', '30', '36'], 1,
     'Each of the 6 vertices has degree 5: Σ deg = 30 = 2|E|, so |E| = 15 (also C(6,2) = 15).')]),

# ---------------------------------------------------------------- Probability
V('v20', 'probability', "Conditional probability & Bayes", 'Conditional probability',
  'P(A|B) is the probability of A given that B happened: P(A∩B) / P(B).',
  "Bayes' theorem flips the condition: P(A|B) = P(B|A)·P(A) / P(B). "
  'Classic example: a test for a rare disease can be very accurate and still give mostly false positives, because P(disease) is tiny.',
  dict(kind='formula', lines=['P(A | B) = P(A ∩ B) / P(B)', 'P(A | B) = P(B | A) · P(A) / P(B)'], size=32),
  [Q('q20-1', 1, 'P(A∩B) = 0.2 and P(B) = 0.5. What is P(A|B)?', ['0.1', '0.4', '0.7', '2.5'], 1, '0.2 / 0.5 = 0.4.'),
   Q('q20-2', 2, 'True or false: if A and B are independent, then P(A|B) = P(A).', TF, 0,
     'Independence means P(A∩B) = P(A)P(B), so P(A|B) = P(A)P(B)/P(B) = P(A).'),
   Q('q20-3', 3, 'A disease affects 1% of people. A test is 99% sensitive and has a 5% false-positive rate. Given a positive test, the chance of disease is about…',
     ['99%', '50%', '17%', '1%'], 2,
     'P(D|+) = 0.99·0.01 / (0.99·0.01 + 0.05·0.99) = 0.0099 / 0.0594 ≈ 0.17.')]),

V('v21', 'probability', 'The binomial distribution', 'Distributions',
  'Number of successes in n independent trials, each with success probability p.',
  'P(X = k) = C(n, k)·pᵏ·(1 − p)ⁿ⁻ᵏ. Its mean is np and its variance is np(1 − p). '
  'For n = 4 coin flips the counts of outcomes are 1, 4, 6, 4, 1 out of 16 — a row of Pascal’s triangle.',
  dict(kind='dist', vals=[1, 4, 6, 4, 1], labels=[0, 1, 2, 3, 4], hl=[2], label='Binomial(4, ½): number of heads'),
  [Q('q21-1', 1, 'You flip a fair coin 4 times. What is P(exactly 4 heads)?', ['1/4', '1/8', '1/16', '1/2'], 2, '(1/2)⁴ = 1/16.'),
   Q('q21-2', 2, 'What is the expected value of Binomial(10, 0.3)?', ['0.3', '3', '7', '10'], 1, 'E[X] = np = 10 · 0.3 = 3.'),
   Q('q21-3', 3, 'What is the variance of Binomial(10, 0.3)?', ['3', '2.1', '0.21', '7'], 1, 'Var = np(1 − p) = 10 · 0.3 · 0.7 = 2.1.')]),

# ---------------------------------------------------------------- ODE
V('v23', 'ode', "Exponential growth & decay: y' = ky", 'First-order ODEs',
  "The solution of y' = ky is y = C·eᵏᵗ. k > 0 grows, k < 0 decays.",
  "Separate variables: dy/y = k dt → ln|y| = kt + c → y = C·eᵏᵗ, where C = y(0). "
  "This models radioactive decay, cooling, populations and continuously compounded interest. Half-life: t½ = ln 2 / |k|.",
  dict(kind='plot', f='2*np.exp(-0.7*x)', xr=(-0.5, 5), yr=(-0.5, 3), label="y' = −0.7·y ,  y(0) = 2"),
  [Q('q23-1', 1, "What is the solution of y' = 2y with y(0) = 1?", ['y = 2t', 'y = e²ᵗ', 'y = t²', 'y = 2eᵗ'], 1, 'y = C·e²ᵗ and y(0) = 1 gives C = 1.'),
   Q('q23-2', 2, "True or false: for y' = −3y, every solution tends to 0 as t → ∞.", TF, 0, 'y = C·e⁻³ᵗ → 0 for every C.'),
   Q('q23-3', 3, 'A substance decays with k = −0.1 per year. Its half-life is about…', ['0.69 years', '5 years', '6.9 years', '10 years'], 2,
     't½ = ln 2 / 0.1 ≈ 0.693 / 0.1 ≈ 6.9 years.')]),

V('v24', 'ode', "The harmonic oscillator: y'' + ω²y = 0", 'Second-order ODEs',
  "Solutions are pure oscillations: y = A·cos(ωt) + B·sin(ωt).",
  "Try y = eʳᵗ: the characteristic equation r² + ω² = 0 gives r = ±iω, which become cos and sin. "
  "This is the equation of springs, pendulums (small angles) and LC circuits. The period is 2π/ω.",
  dict(kind='plot', f='np.cos(2*x)', f2='0.6*np.sin(2*x)', xr=(0, 6.3), yr=(-1.5, 1.5), label="y'' + 4y = 0"),
  [Q('q24-1', 1, "Which function solves y'' + y = 0?", ['eᵗ', 'sin t', 't²', 'ln t'], 1, "(sin t)'' = −sin t, so sin t'' + sin t = 0."),
   Q('q24-2', 2, "What is the period of the solutions of y'' + 4y = 0?", ['π/2', 'π', '2π', '4π'], 1, 'ω = 2, so the period is 2π/2 = π.'),
   Q('q24-3', 3, "The characteristic equation of y'' − 5y' + 6y = 0 has roots…", ['2 and 3', '−2 and −3', '1 and 6', '±i√6'], 0,
     "r² − 5r + 6 = (r − 2)(r − 3) = 0, so y = Ae²ᵗ + Be³ᵗ.")]),

# ---------------------------------------------------------------- Complex functions
V('v25', 'complex', "Euler's formula", 'Complex numbers',
  'e^(iθ) = cos θ + i·sin θ: a point moving around the unit circle.',
  'Multiplying by e^(iθ) rotates a complex number by θ. Every complex number can be written in polar form z = r·e^(iθ), '
  'where r = |z| and θ = arg z. At θ = π we get e^(iπ) + 1 = 0.',
  dict(kind='complex'),
  [Q('q25-1', 1, 'What is |e^(iθ)| for real θ?', ['θ', '1', 'e', '0'], 1, 'cos²θ + sin²θ = 1, so it lies on the unit circle.'),
   Q('q25-2', 2, 'What is e^(iπ/2)?', ['1', '−1', 'i', '−i'], 2, 'cos(π/2) + i·sin(π/2) = 0 + i = i.'),
   Q('q25-3', 3, 'What is (1 + i)⁸?', ['8', '16', '16i', '256'], 1, '1 + i = √2·e^(iπ/4), so (1 + i)⁸ = (√2)⁸·e^(2πi) = 16.')]),

V('v26', 'complex', 'Roots of unity', 'Complex numbers',
  'The n solutions of zⁿ = 1 are evenly spaced on the unit circle.',
  'They are e^(2πik/n) for k = 0, …, n − 1 and form a regular n-gon. With ω = e^(2πi/n), the roots are 1, ω, ω², …, ωⁿ⁻¹, '
  'and their sum is 0 (for n > 1).',
  dict(kind='graph', nodes=circle_pos(['1', 'ω', 'ω²', 'ω³', 'ω⁴', 'ω⁵'], r=0.38),
       edges=[('1', 'ω'), ('ω', 'ω²'), ('ω²', 'ω³'), ('ω³', 'ω⁴'), ('ω⁴', 'ω⁵'), ('ω⁵', '1')],
       order=['1', 'ω', 'ω²', 'ω³', 'ω⁴', 'ω⁵'], step=1.2, label='z⁶ = 1'),
  [Q('q26-1', 1, 'How many solutions does z⁵ = 1 have in ℂ?', ['1', '2', '5', 'Infinitely many'], 2, 'A degree-n polynomial has n complex roots: here 5.'),
   Q('q26-2', 2, 'Which of these is a 4th root of unity?', ['2', 'i', '1 + i', 'i/2'], 1, 'i⁴ = (i²)² = (−1)² = 1.'),
   Q('q26-3', 3, 'What is the sum of all 7th roots of unity?', ['0', '1', '7', '−1'], 0,
     'They are the roots of z⁷ − 1, whose z⁶ coefficient is 0, so their sum is 0.')]),

# ---------------------------------------------------------------- Physics 1
V('v4', 'physics1', 'Newton’s second law', 'Dynamics',
  'ΣF = m·a: the net force on a body equals its mass times its acceleration.',
  'Draw a free-body diagram, choose axes, and write ΣF = ma along each axis. On a frictionless incline only the component mg·sin θ acts along the slope, '
  'so a = g·sin θ, while the normal force balances mg·cos θ.',
  dict(kind='incline', angle=30),
  [Q('q4-1', 1, 'A 2 kg body accelerates at 3 m/s². What is the net force on it?', ['1.5 N', '5 N', '6 N', '9 N'], 2, 'F = m·a = 2 · 3 = 6 N.'),
   Q('q4-2', 2, 'True or false: a body moving at constant velocity must have zero net force acting on it.', TF, 0,
     'Constant velocity means a = 0, and by F = m·a the net force is zero (Newton’s first law).'),
   Q('q4-3', 3, 'A block slides down a frictionless incline at angle θ. What is its acceleration?', ['g', 'g·cos θ', 'g·sin θ', 'g·tan θ'], 2,
     'Only the component of gravity along the incline accelerates the block: m·g·sin θ = m·a, so a = g·sin θ.')]),

V('v27', 'physics1', 'The simple pendulum', 'Oscillations',
  'For small angles the period is T = 2π√(L/g) — it does not depend on the mass.',
  'For small angles sin θ ≈ θ, which turns the equation of motion into a harmonic oscillator with ω = √(g/L). '
  'A longer string means a slower swing; on the Moon (smaller g) the period is longer.',
  dict(kind='pendulum', T=2.5),
  [Q('q27-1', 1, 'True or false: a heavier bob makes a simple pendulum swing faster.', TF, 1, 'T = 2π√(L/g) has no mass in it.'),
   Q('q27-2', 2, 'If the length of a pendulum is multiplied by 4, its period…', ['Halves', 'Doubles', 'Is 4 times longer', 'Stays the same'], 1, 'T ∝ √L, and √4 = 2.'),
   Q('q27-3', 3, 'What is the period of a 1 m pendulum on Earth (g ≈ 9.8 m/s²)?', ['≈ 0.5 s', '≈ 1 s', '≈ 2 s', '≈ 6.3 s'], 2,
     'T = 2π√(1/9.8) ≈ 2π · 0.32 ≈ 2.0 s.')]),

# ---------------------------------------------------------------- Physics 2
V('v5', 'physics2', 'Coulomb’s law', 'Electrostatics',
  'F = k·q₁q₂ / r². Like charges repel, opposite charges attract.',
  'k ≈ 9·10⁹ N·m²/C². The force acts along the line joining the charges and falls off with the square of the distance. '
  'Forces from several charges add as vectors (superposition).',
  dict(kind='charges', q=['+', '+'], move=True),
  [Q('q5-1', 1, 'True or false: two positive charges attract each other.', TF, 1, 'Like charges repel, opposite charges attract.'),
   Q('q5-2', 2, 'If the distance between two charges is doubled, the force between them…', ['Halves', 'Becomes 1/4', 'Doubles', 'Becomes 4 times bigger'], 1,
     'F ∝ 1/r². Doubling r divides the force by 2² = 4.'),
   Q('q5-3', 3, 'What is the electric field inside a conductor in electrostatic equilibrium?', ['Zero', 'Uniform and non-zero', 'Depends on the surface charge', 'Infinite'], 0,
     'If there were a field inside, free charges would move. In equilibrium they stop moving, so the field inside is zero.')]),

V('v29', 'physics2', 'The electric field', 'Electrostatics',
  'E = F / q: the force per unit charge. Field lines leave + charges and end on − charges.',
  'The field of a point charge is E = kQ / r², pointing away from a positive charge. A charge q placed in the field feels F = qE. '
  'Field lines never cross, and they are denser where the field is stronger.',
  dict(kind='charges', q=['+', '−']),
  [Q('q29-1', 1, 'Field lines start on…', ['Negative charges', 'Positive charges', 'Neutral objects', 'Magnets only'], 1,
     'By convention field lines point away from positive charges and toward negative ones.'),
   Q('q29-2', 2, 'An electron is placed in a field pointing to the right. The force on it points…', ['Right', 'Left', 'Up', 'There is no force'], 1,
     'F = qE and q is negative, so the force is opposite to E.'),
   Q('q29-3', 3, "Gauss's law states that the flux of E through a closed surface equals…", ['Zero always', 'Q_enclosed / ε₀', 'The surface area', 'k·Q / r²'], 1,
     '∮ E · dA = Q_enc / ε₀.')]),

# ---------------------------------------------------------------- Physics 3
V('v6', 'physics3', 'Wave speed, frequency, wavelength', 'Waves',
  'v = f·λ. The speed is set by the medium; frequency is set by the source.',
  'The wavelength λ is the distance between crests, f is how many crests pass per second. '
  'When a wave enters a new medium its frequency stays the same, so the wavelength changes with the speed.',
  dict(kind='wave', k=2.0, w=2.0, **{'lambda': True}),
  [Q('q6-1', 1, 'A wave has frequency 10 Hz and wavelength 2 m. What is its speed?', ['5 m/s', '12 m/s', '20 m/s', '0.2 m/s'], 2, 'v = f·λ = 10 · 2 = 20 m/s.'),
   Q('q6-2', 2, 'In the same medium, the frequency of a wave is doubled. The wavelength…', ['Doubles', 'Halves', 'Stays the same', 'Becomes 4 times bigger'], 1,
     'The speed depends on the medium and stays fixed, so λ = v/f halves.'),
   Q('q6-3', 3, 'True or false: shining brighter light below the threshold frequency will eventually eject electrons from a metal.', TF, 1,
     'Photoelectric effect: each photon has energy h·f. Below the threshold frequency no single photon has enough energy, no matter how many photons arrive.')]),

V('v30', 'physics3', 'The photoelectric effect', 'Modern physics',
  'Light comes in photons with energy E = h·f. One photon can free one electron.',
  'An electron escapes only if h·f is larger than the work function φ of the metal; its maximum kinetic energy is K = h·f − φ. '
  'Brighter light means more photons (more electrons), not more energetic ones. Einstein won the 1921 Nobel Prize for this explanation.',
  dict(kind='atom', shells=[2, 8], photon=True, label='E = h·f'),
  [Q('q30-1', 1, 'The energy of one photon depends on its…', ['Brightness', 'Frequency', 'Speed', 'Direction'], 1, 'E = h·f.'),
   Q('q30-2', 2, 'Light with h·f = 5 eV hits a metal with φ = 2 eV. The max kinetic energy of the electrons is…', ['2 eV', '3 eV', '5 eV', '7 eV'], 1, 'K = h·f − φ = 5 − 2 = 3 eV.'),
   Q('q30-3', 3, 'Increasing the intensity (above threshold) increases…', ['The max kinetic energy', 'The number of emitted electrons', 'The work function', 'The photon frequency'], 1,
     'More photons per second free more electrons, each with the same maximum energy.')]),

# ---------------------------------------------------------------- Quantum
V('v31', 'quantum', 'Matter waves (de Broglie)', 'Wave–particle duality',
  'Every particle has a wavelength λ = h / p. Electrons can interfere like waves.',
  'De Broglie (1924) proposed that particles with momentum p behave as waves with λ = h/p. '
  'This was confirmed by electron diffraction. A particle localized in space is described by a wave packet.',
  dict(kind='wave', k=5.0, w=3.0, packet=True),
  [Q('q31-1', 1, 'In λ = h/p, p stands for…', ['Power', 'Momentum', 'Pressure', 'Position'], 1, 'p is the momentum (m·v for slow particles).'),
   Q('q31-2', 2, 'If a particle’s momentum doubles, its de Broglie wavelength…', ['Doubles', 'Halves', 'Stays the same', 'Quadruples'], 1, 'λ ∝ 1/p.'),
   Q('q31-3', 3, 'Which experiment showed the wave nature of electrons?', ['Millikan oil drop', 'Davisson–Germer', 'Michelson–Morley', 'Rutherford scattering'], 1,
     'Davisson and Germer (1927) observed electron diffraction from a nickel crystal.')]),

V('v32', 'quantum', 'The uncertainty principle', 'Foundations',
  'Δx·Δp ≥ ħ/2: position and momentum cannot both be known exactly.',
  'This is not a measurement flaw — it follows from the wave nature of particles. A narrow wave packet (small Δx) is built from many wavelengths, '
  'which means a large spread in momentum (large Δp).',
  dict(kind='formula', lines=['Δx · Δp  ≥  ħ / 2', 'narrow in x  →  wide in p'], size=40),
  [Q('q32-1', 1, 'True or false: the uncertainty principle is caused by bad measuring tools.', TF, 1,
     'It is a fundamental property of quantum states, not an instrument limitation.'),
   Q('q32-2', 2, 'If Δx is made smaller, the minimum possible Δp…', ['Gets smaller', 'Gets larger', 'Stays the same', 'Becomes zero'], 1, 'Δp ≥ ħ / (2Δx).'),
   Q('q32-3', 3, 'ħ is equal to…', ['h · 2π', 'h / 2π', 'h²', '2h'], 1, 'The reduced Planck constant is ħ = h / 2π ≈ 1.05·10⁻³⁴ J·s.')]),

# ---------------------------------------------------------------- Intro to programming
V('v11', 'intro-cs', 'Variables and types', 'Variables',
  'A variable is a name for a value. Every value has a type: int, float, str, bool…',
  'In Python a variable gets its type from the value assigned to it, and type(x) tells you what it is. '
  'Assignment copies the reference to the value, so changing x later does not change a variable that was assigned from it earlier.',
  dict(kind='code', lines=['age = 21', 'name = "Dana"', 'pi = 3.14', 'is_student = True', 'print(type(name))'], out="<class 'str'>"),
  [Q('q11-1', 1, 'Which of these is a string?', ['42', 'true', '"hello"', '3.14'], 2,
     'Text wrapped in quotes is a string. 42 is an integer, true is a boolean, 3.14 is a float.'),
   Q('q11-2', 2, 'In Python: x = 5, then y = x, then x = 7. What is y?', ['5', '7', '12', 'An error'], 0,
     'y got the value 5 when it was assigned. Changing x later does not change y.'),
   Q('q11-3', 3, 'True or false: in Python, 0.1 + 0.2 == 0.3 evaluates to True.', TF, 1,
     'Floating point numbers cannot store 0.1 and 0.2 exactly. 0.1 + 0.2 is 0.30000000000000004, so the comparison is False.')]),

V('v33', 'intro-cs', 'For loops', 'Control flow',
  'A loop repeats a block of code — here once for every value in range(1, 6).',
  'range(a, b) produces a, a+1, …, b−1 (b is not included). The loop body runs once per value. '
  'Accumulating into a variable (total += i) is one of the most common loop patterns.',
  dict(kind='code', lines=['total = 0', 'for i in range(1, 6):', '    total += i', 'print(total)'], out='15'),
  [Q('q33-1', 1, 'How many times does "for i in range(3):" run its body?', ['2', '3', '4', 'Forever'], 1, 'range(3) is 0, 1, 2 — three values.'),
   Q('q33-2', 2, 'What does list(range(2, 8, 2)) produce?', ['[2, 4, 6, 8]', '[2, 4, 6]', '[2, 3, 4, 5, 6, 7]', '[4, 6, 8]'], 1,
     'Start at 2, step 2, stop before 8.'),
   Q('q33-3', 3, 'What is printed?  s = 0; for i in range(4): s += i * i; print(s)', ['6', '14', '30', '16'], 1, '0 + 1 + 4 + 9 = 14.')]),

V('v34', 'intro-cs', 'Recursion', 'Functions',
  'A recursive function calls itself on a smaller input, until it reaches a base case.',
  'Every recursion needs a base case (here n == 0) or it never stops. fact(5) = 5·fact(4) = … = 5·4·3·2·1·1 = 120. '
  'Each call waits on the call stack until the smaller call returns.',
  dict(kind='code', lines=['def fact(n):', '    if n == 0:', '        return 1', '    return n * fact(n - 1)', '', 'print(fact(5))'], out='120'),
  [Q('q34-1', 1, 'What is the part of a recursive function that stops the recursion called?', ['The loop', 'The base case', 'The return type', 'The stack'], 1,
     'The base case returns without calling the function again.'),
   Q('q34-2', 2, 'What does fact(3) return (using the function in the video)?', ['3', '6', '9', '1'], 1, '3 · 2 · 1 · 1 = 6.'),
   Q('q34-3', 3, 'What happens if you call fact(-1)?', ['Returns 1', 'Returns 0', 'Infinite recursion (RecursionError)', 'Returns −1'], 2,
     'n never reaches 0, so Python eventually raises RecursionError.')]),

# ---------------------------------------------------------------- Data structures
V('v35', 'data-structures', 'Linked lists', 'Lists',
  'Each node stores a value and a pointer to the next node. The last one points to null.',
  'Inserting or deleting at the head is O(1), but reaching the k-th element takes O(k) because you must follow the pointers one by one. '
  'Arrays are the opposite: O(1) access by index, but O(n) to insert in the middle.',
  dict(kind='graph', nodes={'3': (0.12, 0.5), '7': (0.37, 0.5), '9': (0.62, 0.5), '∅': (0.88, 0.5)},
       edges=[('3', '7'), ('7', '9'), ('9', '∅')], directed=True, order=['3', '7', '9', '∅'], step=1.8, label='head → 3 → 7 → 9 → null'),
  [Q('q35-1', 1, 'What does the last node of a singly linked list point to?', ['The head', 'null', 'Itself', 'The middle'], 1, 'The last node’s next pointer is null.'),
   Q('q35-2', 2, 'What is the time to access the k-th element of a linked list?', ['O(1)', 'O(log k)', 'O(k)', 'O(k²)'], 2, 'You must follow k pointers from the head.'),
   Q('q35-3', 3, 'Which operation is O(1) for a linked list but O(n) for an array?', ['Access by index', 'Insert at the front', 'Binary search', 'Read the last element'], 1,
     'Prepending only changes the head pointer; an array must shift every element.')]),

V('v36', 'data-structures', 'Binary search trees', 'Trees',
  'Left subtree < node < right subtree. Search by going left or right at each step.',
  'Searching, inserting and deleting take O(h), where h is the height. A balanced tree (AVL, red-black) keeps h = O(log n); '
  'inserting sorted data into a plain BST makes it a chain with h = n. An in-order traversal visits the keys in sorted order.',
  dict(kind='tree', keys=[8, 3, 10, 1, 6, None, 14], path=[0, 1, 4], label='search(6): 8 → 3 → 6'),
  [Q('q36-1', 1, 'In a BST, where are the keys smaller than the root?', ['Right subtree', 'Left subtree', 'Anywhere', 'In the leaves only'], 1, 'Smaller keys go left, larger keys go right.'),
   Q('q36-2', 2, 'Which traversal of a BST visits the keys in sorted order?', ['Pre-order', 'In-order', 'Post-order', 'Level-order'], 1, 'In-order = left, node, right.'),
   Q('q36-3', 3, 'You insert 1, 2, 3, …, n into an empty (unbalanced) BST. Its height is…', ['O(1)', 'O(log n)', 'Θ(n)', 'Θ(n²)'], 2,
     'Each key goes to the right of the previous one, forming a chain.')]),

# ---------------------------------------------------------------- Algorithms
V('v12', 'algorithms', 'Big O in 15 seconds', 'Complexity',
  'Big O describes how running time grows with input size n — ignoring constants.',
  'O(n) grows linearly, O(n²) grows much faster: doubling n quadruples the work. '
  'We keep only the dominant term: 3n² + 5n + 7 = O(n²). Common classes: O(1) < O(log n) < O(n) < O(n log n) < O(n²) < O(2ⁿ).',
  dict(kind='plot', f='x', f2='x**2/4', xr=(0, 8), yr=(0, 8), label='O(n)  vs  O(n²)'),
  [Q('q12-1', 1, 'What is the time complexity of a single loop over n items?', ['O(1)', 'O(n)', 'O(n²)', 'O(log n)'], 1,
     'Each item is visited once, so the work grows linearly with n.'),
   Q('q12-2', 2, 'What is the time complexity of binary search on a sorted array of n items?', ['O(n)', 'O(log n)', 'O(n log n)', 'O(1)'], 1,
     'Each step halves the search range, so the number of steps grows with log n.'),
   Q('q12-3', 3, 'What does T(n) = 2T(n/2) + n solve to?', ['O(n)', 'O(n log n)', 'O(n²)', 'O(log n)'], 1,
     'Master theorem case 2 (like merge sort): log₂2 = 1 matches f(n) = n, so T(n) = Θ(n log n).')]),

V('v37', 'algorithms', 'Binary search', 'Searching',
  'In a sorted array, compare with the middle and throw away half of the range each step.',
  'Keep two indices lo and hi. If a[mid] < target search the right half, otherwise the left half. '
  'At most ⌊log₂ n⌋ + 1 comparisons: about 20 steps for a million items. It only works on sorted data.',
  dict(kind='bars', vals=[2, 5, 8, 12, 16, 23, 38, 45, 56, 72], target=23, step=1.6, label='search 23'),
  [Q('q37-1', 1, 'Binary search requires the array to be…', ['Short', 'Sorted', 'Of even length', 'Made of integers'], 1, 'Discarding half only makes sense if the data is sorted.'),
   Q('q37-2', 2, 'At most how many comparisons does binary search need for 1,000 items?', ['10', '100', '500', '1000'], 0, '2¹⁰ = 1024 ≥ 1000, so about 10.'),
   Q('q37-3', 3, 'Searching for 23 in [2,5,8,12,16,23,38,45,56,72] with mid = (lo+hi)//2, which index is checked first?', ['4', '5', '6', '9'], 0,
     'lo = 0, hi = 9, mid = 4 (value 16). 16 < 23, so the search continues in indices 5…9.')]),

V('v38', 'algorithms', 'Bubble sort', 'Sorting',
  'Repeatedly swap neighbours that are out of order. The largest value bubbles to the end.',
  'After pass i, the last i elements are in their final place. Bubble sort is O(n²) in the worst and average case, '
  'O(n) on already-sorted input if you stop when a pass makes no swaps. It is stable and in-place, but too slow for large inputs.',
  dict(kind='bars', mode='sort', vals=[5, 2, 8, 1, 6, 3], step=0.33, label='bubble sort'),
  [Q('q38-1', 1, 'After the first pass of bubble sort, which element is guaranteed to be in place?', ['The smallest', 'The largest', 'The middle one', 'None'], 1,
     'The largest element keeps being swapped forward until it reaches the end.'),
   Q('q38-2', 2, 'What is the worst-case time complexity of bubble sort?', ['O(n)', 'O(n log n)', 'O(n²)', 'O(2ⁿ)'], 2, 'Up to n − 1 passes of up to n − 1 comparisons.'),
   Q('q38-3', 3, 'Which sort has O(n log n) worst-case time?', ['Bubble sort', 'Insertion sort', 'Merge sort', 'Quick sort'], 2,
     'Merge sort is always O(n log n); quicksort is O(n²) in the worst case.')]),

# ---------------------------------------------------------------- Computational models
V('v39', 'computability', 'Finite automata (DFA)', 'Regular languages',
  'A DFA reads a word letter by letter, moving between states. It accepts if it ends in an accepting state.',
  'Formally (Q, Σ, δ, q₀, F). This DFA accepts binary words with an even number of 1s: reading 1 switches state, reading 0 stays. '
  'The languages DFAs accept are exactly the regular languages.',
  dict(kind='graph', nodes={'q0': (0.28, 0.68), 'q1': (0.72, 0.68)},
       edges=[('q0', 'q1', '1'), ('q1', 'q0', ''), ('q0', 'q0', '0'), ('q1', 'q1', '0')], directed=True, accept=['q0'],
       order=['q0', 'q1'], step=2.0, r=62, fs=30, label='even number of 1s'),
  [Q('q39-1', 1, 'A DFA accepts a word if, after reading it, it is in…', ['The start state', 'An accepting state', 'Any state', 'Two states at once'], 1,
     'Acceptance depends on the final state being in F.'),
   Q('q39-2', 2, 'Does the DFA in the video accept 1011?', ['Yes', 'No'], 1, '1011 has three 1s — odd — so it ends in q1, which is not accepting.'),
   Q('q39-3', 3, 'Which language is NOT regular?', ['Words with an even number of 1s', 'Words ending in 01', '{ 0ⁿ1ⁿ : n ≥ 0 }', 'All binary words'], 2,
     'By the pumping lemma, a finite automaton cannot count an unbounded number of 0s.')]),

V('v40', 'computability', 'The halting problem', 'Decidability',
  'No algorithm can decide, for every program and input, whether the program halts.',
  'Proof idea (Turing, 1936): suppose HALT existed. Build a program D that runs HALT on itself and does the opposite. '
  'D halts ⇔ D does not halt — a contradiction. So HALT is undecidable (though it is recognizable).',
  dict(kind='formula', lines=['HALT(P, x) = ?', 'D(D) halts  ⇔  D(D) loops', '⇒ undecidable'], size=36),
  [Q('q40-1', 1, 'True or false: there is a program that decides for every program and input whether it halts.', TF, 1, 'This is exactly what Turing proved impossible.'),
   Q('q40-2', 2, 'Which proof technique is used for the halting problem?', ['Induction', 'Diagonalization', 'Pigeonhole', 'Contrapositive of Rolle'], 1,
     'The program D “does the opposite” of the prediction about itself — a diagonal argument.'),
   Q('q40-3', 3, 'The halting language HALT is…', ['Decidable', 'Recognizable but not decidable', 'Not recognizable', 'Regular'], 1,
     'Simulate P on x and accept if it halts — that recognizes HALT, but cannot reject the non-halting cases.')]),

# ---------------------------------------------------------------- Electric circuits
V('v41', 'circuits', "Ohm's law", 'DC circuits',
  'V = I·R: the voltage across a resistor equals current times resistance.',
  'Current (amperes) is the flow of charge, voltage (volts) is the push, resistance (ohms) opposes the flow. '
  'Power dissipated in a resistor: P = V·I = I²R = V²/R.',
  dict(kind='circuit', resistors=['R'], label='V = I · R'),
  [Q('q41-1', 1, 'A 10 Ω resistor has 2 A through it. What is the voltage across it?', ['5 V', '12 V', '20 V', '0.2 V'], 2, 'V = I·R = 2 · 10 = 20 V.'),
   Q('q41-2', 2, 'A 12 V battery drives a 4 Ω resistor. What power does the resistor dissipate?', ['3 W', '36 W', '48 W', '16 W'], 1, 'P = V²/R = 144 / 4 = 36 W.'),
   Q('q41-3', 3, 'What is the equivalent resistance of 6 Ω and 3 Ω in parallel?', ['9 Ω', '2 Ω', '4.5 Ω', '18 Ω'], 1, '1/R = 1/6 + 1/3 = 1/2, so R = 2 Ω.')]),

V('v42', 'circuits', "Kirchhoff's laws", 'DC circuits',
  'KVL: voltages around a loop sum to 0. KCL: current into a node = current out.',
  'KCL is conservation of charge, KVL is conservation of energy. In a series loop with a source V and resistors R₁, R₂: '
  'V = I·R₁ + I·R₂, so I = V / (R₁ + R₂). Node and mesh analysis are systematic ways to apply these laws.',
  dict(kind='circuit', resistors=['R₁', 'R₂'], label='ΣV = 0'),
  [Q('q42-1', 1, "Kirchhoff's current law is a statement of conservation of…", ['Energy', 'Charge', 'Momentum', 'Mass'], 1, 'Charge cannot pile up at a node.'),
   Q('q42-2', 2, 'Three wires meet at a node: 2 A and 3 A flow in. How much flows out in the third wire?', ['1 A', '5 A', '6 A', '0 A'], 1, 'In = out: 2 + 3 = 5 A.'),
   Q('q42-3', 3, 'A 9 V source drives R₁ = 1 Ω and R₂ = 2 Ω in series. What is the voltage across R₂?', ['3 V', '4.5 V', '6 V', '9 V'], 2,
     'I = 9 / 3 = 3 A, so V₂ = 3 · 2 = 6 V (a voltage divider).')]),

# ---------------------------------------------------------------- Signals & systems
V('v43', 'signals', 'The Fourier series', 'Frequency domain',
  'Any periodic signal is a sum of sines and cosines at multiples of a base frequency.',
  'x(t) = Σ cₖ e^(ikω₀t). The coefficients cₖ form the spectrum: they say how much of each frequency the signal contains. '
  'A square wave, for example, contains only odd harmonics with amplitudes 1, 1/3, 1/5, …',
  dict(kind='signal', comps=[(1, 1.0), (3, 0.5), (5, 0.3)]),
  [Q('q43-1', 1, 'The Fourier series represents a periodic signal as a sum of…', ['Polynomials', 'Sines and cosines', 'Step functions', 'Exponentials that decay'], 1,
     'It decomposes the signal into harmonics.'),
   Q('q43-2', 2, 'A signal has period 0.01 s. What is its fundamental frequency?', ['0.01 Hz', '10 Hz', '100 Hz', '1000 Hz'], 2, 'f₀ = 1/T = 100 Hz.'),
   Q('q43-3', 3, 'Which harmonics does an ideal square wave (odd symmetry) contain?', ['Only even', 'Only odd', 'All', 'Only the fundamental'], 1,
     'Its series is (4/π)(sin ωt + sin 3ωt/3 + sin 5ωt/5 + …).')]),

V('v44', 'signals', 'Sampling and Nyquist', 'Sampling',
  'To reconstruct a signal, sample faster than twice its highest frequency: fs > 2·f_max.',
  'Sampling below the Nyquist rate causes aliasing: high frequencies masquerade as low ones. '
  'That is why audio CDs use 44.1 kHz — a bit more than twice the 20 kHz limit of human hearing.',
  dict(kind='plot', f='np.sin(x)', xr=(0, 6.5), yr=(-1.5, 1.5), dots=[(x, math.sin(x)) for x in np.arange(0.2, 6.4, 0.7)], label='fs > 2·f_max'),
  [Q('q44-1', 1, 'A signal contains frequencies up to 1 kHz. The minimum sampling rate is…', ['500 Hz', '1 kHz', '2 kHz', '10 kHz'], 2, 'Nyquist: fs > 2 · 1 kHz.'),
   Q('q44-2', 2, 'Sampling too slowly causes…', ['Clipping', 'Aliasing', 'Echo', 'Quantization only'], 1, 'Frequencies above fs/2 fold back as false low frequencies.'),
   Q('q44-3', 3, 'A 7 kHz tone is sampled at 10 kHz. It appears as a tone of…', ['7 kHz', '3 kHz', '10 kHz', '17 kHz'], 1, 'It aliases to |10 − 7| = 3 kHz.')]),

# ---------------------------------------------------------------- General chemistry
V('v45', 'chem', 'Electron shells', 'Atomic structure',
  'Electrons fill shells around the nucleus: 2 in the first, 8 in the second, …',
  'The outermost (valence) electrons decide how an element reacts. Sodium (2, 8, 1) easily loses its single valence electron to become Na⁺; '
  'elements in the same group of the periodic table have the same number of valence electrons.',
  dict(kind='atom', shells=[2, 8, 1], nucleus='Na', label='Na: 2, 8, 1'),
  [Q('q45-1', 1, 'How many electrons fit in the first shell?', ['1', '2', '8', '18'], 1, 'The first shell (1s) holds 2 electrons.'),
   Q('q45-2', 2, 'How many valence electrons does chlorine (Z = 17) have?', ['1', '5', '7', '17'], 2, 'Configuration 2, 8, 7 → 7 valence electrons.'),
   Q('q45-3', 3, 'Which ion does magnesium (Z = 12) usually form?', ['Mg⁺', 'Mg²⁺', 'Mg⁻', 'Mg²⁻'], 1, '2, 8, 2 → it loses two electrons to reach a full shell.')]),

V('v46', 'chem', 'The water molecule', 'Chemical bonding',
  'H₂O is bent (≈104.5°) and polar: oxygen pulls the shared electrons toward itself.',
  'Oxygen has two lone pairs, which push the O–H bonds together (VSEPR). Because O is much more electronegative than H, '
  'the molecule has a partial negative charge on O and partial positive charges on the H atoms — that is what makes hydrogen bonds possible.',
  dict(kind='molecule', atoms=[('O', 0, 0, '#ff453a'), ('H', 37.75, 120, '#8e8e93'), ('H', 142.25, 120, '#8e8e93')], label='H₂O · 104.5°'),
  [Q('q46-1', 1, 'How many hydrogen atoms are in a water molecule?', ['1', '2', '3', '4'], 1, 'H₂O: two hydrogens, one oxygen.'),
   Q('q46-2', 2, 'Why is water a polar molecule?', ['It is linear', 'It is bent and O is more electronegative than H', 'It has no lone pairs', 'H is more electronegative than O'], 1,
     'The bond dipoles do not cancel because of the bent shape.'),
   Q('q46-3', 3, 'What is the electron-pair geometry around the oxygen in water?', ['Linear', 'Trigonal planar', 'Tetrahedral', 'Octahedral'], 2,
     '4 electron domains (2 bonds + 2 lone pairs) → tetrahedral; the molecular shape is bent.')]),
]
