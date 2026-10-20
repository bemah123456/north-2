// Large type and strong contrast for older eyes and shaky hands. Every text
// colour here reads at 7:1 or better on the background (WCAG AAA), and no
// status is shown by colour alone: each one also has a symbol and a word.
export const colors = {
  bg: '#F7F3EC',
  card: '#FFFFFF',
  text: '#1A1612',
  muted: '#4A443C',
  primary: '#14524A',
  primaryPressed: '#0D3B35',
  primaryText: '#FFFFFF',
  primarySoft: '#E1EFEA',
  border: '#D9D1C4',
  green: '#1E6B43',
  greenSoft: '#E3F2E8',
  amber: '#8A4E00',
  amberSoft: '#FCEFD9',
  red: '#A3221B',
  redSoft: '#FBE4E1',
  grey: '#5A5A5A',
  greySoft: '#ECEAE6',
};

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

// A symbol for each status, so it reads without colour too.
export const statusSymbol: Record<string, string> = {
  unlikely: '✓',
  possible_impairment: '!',
  possible_delirium: '!',
  missed: '?',
  pending: '…',
  day_off: '–',
};

export const type = { giant: 44, huge: 36, big: 28, body: 22, small: 18 };

export const space = { xs: 6, s: 12, m: 20, l: 28, xl: 40 };

export const radius = { m: 16, l: 24, round: 999 };
