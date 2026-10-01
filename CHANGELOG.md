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
- Stop sending Escape before a `multiplier = 5` placement: dropping the
  selection also discards the click the game defers while it validates the
  building preview, so the x5 placement never happened.
- Drop the redundant `stackable` field from `[shortcuts]`; it is derived from
  the building name. Existing configurations keep working.
- Document that the game multiplies only upgrades and atomic bomb salvos, so
  x5 can never place five new buildings.

## 0.1.0

- Initial Windows console auto-placer with configurable chords and game keys.
- Foreground-only placement, Pause/Break stop, safety limit and standalone build.
