// Copies Arc UI's design tokens next to the bundle. The page overrides the
// colours, fonts and glows with Clari's own (see the style block in index.html).
import { copyFileSync } from 'node:fs';
copyFileSync('node_modules/@arclux/arc-ui/src/base.css', 'vendor/arc-tokens.css');
