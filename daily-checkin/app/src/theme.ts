// Clari's look, taken from the logo: navy for text and buttons, and the
// logo's blue-to-mint gradient for graphics only (white text on it would be
// too faint). Large type and strong contrast for older eyes and shaky hands:
// every text colour here reads at 7:1 or better on the background and on its
// own soft tint (WCAG AAA), and no status is shown by colour alone: each one
// also has an icon and a word.
export const colors = {
  bg: '#F4F8FB',
  card: '#FFFFFF',
  text: '#0F2236',
  muted: '#3A4B5E',
  primary: '#1A457D', // the wordmark's navy
  primaryPressed: '#12335E',
  primaryText: '#FFFFFF',
  primarySoft: '#E6F0F9',
  border: '#D3DEE8',
  green: '#185736',
  greenSoft: '#E3F2E8',
  amber: '#734100',
  amberSoft: '#FCEFD9',
  red: '#8F1D17',
  redSoft: '#FBE4E1',
  grey: '#4B4B4B',
  greySoft: '#ECEEF1',
};

// The logo's gradient, lower left to upper right. Decoration only.
export const brand = { blue: '#1D7FD2', teal: '#40B5B2', mint: '#59CBAD', glow: '#BFE6E0' };
export const brandGradient = [brand.blue, brand.teal, brand.mint] as const;

export const statusColor: Record<string, string> = {
  unlikely: colors.green,
  possible_impairment: colors.amber,
  possible_delirium: colors.red,
  missed: colors.red,
  pending: colors.grey,
  day_off: colors.grey,
};

export const statusSoft: Record<string, string> = {
  unlikely: colors.greenSoft,
  possible_impairment: colors.amberSoft,
  possible_delirium: colors.redSoft,
  missed: colors.redSoft,
  pending: colors.greySoft,
  day_off: colors.greySoft,
};

// Which icon each status gets (see graphics.tsx), so it reads without colour too.
export const statusIcon: Record<string, 'check' | 'alert' | 'question' | 'dots' | 'dash'> = {
  unlikely: 'check',
  possible_impairment: 'alert',
  possible_delirium: 'alert',
  missed: 'question',
  pending: 'dots',
  day_off: 'dash',
};

// Nunito's rounded letters match the wordmark; Atkinson Hyperlegible was
// designed for readers with low vision. Loaded in App.tsx.
export const font = {
  display: 'Nunito_800ExtraBold',
  heading: 'Nunito_700Bold',
  body: 'AtkinsonHyperlegible_400Regular',
  bodyBold: 'AtkinsonHyperlegible_700Bold',
};

export const type = { giant: 44, huge: 34, big: 27, body: 22, small: 18 };

export const space = { xs: 6, s: 12, m: 20, l: 28, xl: 40 };

export const radius = { m: 16, l: 24, xl: 32, round: 999 };

// Shared motion timings (ms). Quick press feedback, calm entrances, exits a
// little faster than entrances, and slow ambient loops. All of it is turned
// off when the phone asks for reduced motion (motion.ts).
export const motion = { press: 120, enter: 380, exit: 240, stagger: 45, breathe: 2400, ambient: 9000 };

// Text still grows with the phone's own text-size setting, but headings and
// buttons stop at 1.5x so a big setting can't push the main button off screen.
export const maxScale = { heading: 1.5, button: 1.5, tight: 1.2 };
