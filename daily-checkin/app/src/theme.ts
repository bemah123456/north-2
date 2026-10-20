// Large type and strong contrast for older eyes and shaky hands.
export const colors = {
  bg: '#FBF8F3',
  card: '#FFFFFF',
  text: '#1F1B16',
  muted: '#5C554C',
  primary: '#1D5C4D',
  primaryText: '#FFFFFF',
  border: '#E3DDD3',
  green: '#2E7D4F',
  amber: '#A86200',
  red: '#B3261E',
  grey: '#6B6B6B',
};

export const statusColor: Record<string, string> = {
  unlikely: colors.green,
  possible_impairment: colors.amber,
  possible_delirium: colors.red,
  missed: colors.red,
  pending: colors.grey,
  day_off: colors.grey,
};

export const type = { huge: 34, big: 26, body: 20, small: 16 };
