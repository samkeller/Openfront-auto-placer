# Changelog

## Unreleased

- Send game keys by virtual-key code instead of character, so selections reach
  the game on layouts where digits need a modifier (AZERTY, for example).
- Hold each simulated key and mouse button briefly, and wait
  `double_press_delay_ms` after the last selection key before clicking.
- Cancel the current selection with Escape before a ×5 placement, so the
  game's ×5 toggle is always armed instead of alternating with ×1.
- Replace the hidden `target > 5` trigger with an explicit `multiplier` of 1
  or 5.
- Log every simulated step at DEBUG level, and document that the game applies
  ×5 only to upgrades and atomic bombs.
- Reject `Esc` as a hotkey trigger when a building uses `multiplier = 5`,
  since the placement sequence sends Escape itself.

## 0.1.0

- Initial Windows console auto-placer with configurable chords and game keys.
- Foreground-only placement, Pause/Break stop, safety limit and standalone build.
