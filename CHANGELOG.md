# Changelog

## Unreleased

- Send game keys by virtual-key code instead of character, so selections reach
  the game on layouts where digits need a modifier (AZERTY, for example).
- Hold each simulated key and mouse button briefly, and wait
  `double_press_delay_ms` after the last selection key before clicking.
- Cancel the current selection with Escape before a `target > 5` placement, so
  the game's ×5 toggle is always armed instead of alternating with ×1.

## 0.1.0

- Initial Windows console auto-placer with configurable chords and game keys.
- Foreground-only placement, Pause/Break stop, safety limit and standalone build.
