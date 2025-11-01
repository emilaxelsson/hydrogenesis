# Features and limitations

[Hydrogenesis](../src/hydrogenesis.py) can handle both IT and MPTM tracks saved from OpenMPT. No other tracker has been tested. However, not all aspects of the tracks are translated.

What gets converted?

  * Basic meta data (title, tempo, etc.)
  * Patterns
      - name
      - notes (key, instrument, volume)
  * Orders (pattern sequences)
  * MPTM extensions:
      - [Rows per beat](#rows-per-beat)

What does not get converted?

  * Samples and instruments
  * Mixer settings
  * Note commands and panning
  * Etc.



Rows per beat
------------------------------------------------------------------------------------------

The MPTM format has an extension that allows overriding the default number of *rows per beat* (RPB) for individual patterns. This is a really nice feature that provides a kind of dynamic resolution. Patterns with a lot of action can use e.g. 4 rows per beat (meaning each row is separated by a 16th note) while other patterns can make do with a lower RPB. Using a lower number where possible makes navigation and editing easier.

Hydrogenesis will always respect RPB for MPTM tracks. However, OpenMPT itself only caters for RPB when the track's tempo mode is set to "Modern (accurate)". Hence, modern tempo mode must be used in order to get consistent playback and conversion when patterns override the default RPB.

The [Tempo mode](./setup_track.md#tempo-mode) section explains how to set modern tempo mode.

The example track [Were_not_gonna_take_it.mptm](../examples/Were_not_gonna_take_it.mptm) demonstrates the use of pattern-specific RPB. (Compare to [Were_not_gonna_take_it.it](../examples/Were_not_gonna_take_it.it) which does not use custom RPB.)
