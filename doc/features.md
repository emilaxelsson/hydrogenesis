# Features and limitations

[Hydrogenesis](../src/hydrogenesis.py) can handle both IT and MPTM tracks saved from OpenMPT. No other tracker has been tested. However, not all aspects of the tracks are translated.

What gets converted?

  * Basic meta data (title, tempo, etc.)
  * Patterns
      - name
      - notes (key, instrument, volume, [commands](#note-commands))
  * Orders (pattern sequences)
  * MPTM extensions:
      - [Rows per beat](#rows-per-beat)

What does not get converted?

  * Samples and instruments
  * Mixer settings
  * Most note commands and panning
  * Etc.



Note commands
------------------------------------------------------------------------------------------

Hydrogenesis supports the following note commands:

  * Tempo change
  * Note delay

The example track [Dyers_eve.mptm](../examples/Dyers_eve.mptm) demonstrates both tempo changes and note delays.

### Tempo change

Tempo changes can occur anywhere in a pattern. This may seem surprising given that Hydrogen only allows tempo changes at the beginning of patterns. The converter solves this limitation by splitting patterns upon tempo changes. For example, say pattern "A" contains one tempo change somewhere after the first row. Then it will get converted into two Hydrogen patterns: "A#0" and "A#1".

  * Note: Relative tempo changes are supported, but do not work properly when looping patterns. The accumulative change caused by looping a pattern cannot be replicated in Hydrogen.



Rows per beat
------------------------------------------------------------------------------------------

The MPTM format has an extension that allows overriding the default number of *rows per beat* (RPB) for individual patterns, providing a kind of dynamic resolution. Patterns with a lot of action can use e.g. 4 rows per beat (meaning each row is separated by a 16th note) while other patterns can make do with a lower RPB. Using a lower number where possible makes navigation and editing easier.

Hydrogenesis always respects RPB for MPTM tracks. However, OpenMPT itself only caters for RPB when the track's tempo mode is set to "Modern (accurate)". Hence, modern tempo mode must be used in order to get consistent playback and conversion when patterns override the default RPB.

The [Tempo mode](./setup_track.md#tempo-mode) section explains how to set modern tempo mode.

The example track [Were_not_gonna_take_it.mptm](../examples/Were_not_gonna_take_it.mptm) demonstrates the use of pattern-specific RPB. (Compare to [Were_not_gonna_take_it.it](../examples/Were_not_gonna_take_it.it) which does not use custom RPB.)

### Track-wide rows per beat

The parser cannot read the track-wide rows per beat value (the value that is set in Song Properties on the General tab). I wasn't able to figure out how to parse this value (available information doesn't match what I see in example files). The converter will assume 4 rows per beat unless this value is overridden in individual patterns.
