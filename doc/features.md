# Features and limitations

[Hydrogenesis](../src/hydrogenesis.py) can handle both IT and MPTM tracks saved from OpenMPT. No other tracker has been tested. However, not all aspects of the tracks are translated.

What gets converted?

  * Basic meta data (title, tempo, etc.)
  * Patterns
      - name
      - notes (key, instrument, volume)
  * Orders (pattern sequences)
  * MPTM extensions:
      - Rows per beat

What does not get converted?

  * Samples and instruments
  * Mixer settings
  * Note commands and panning
  * Etc.



Rows per beat
------------------------------------------------------------------------------------------

The MPTM format has an extension that allows overriding default number of *rows per beat* for individual patterns. This is a really nice feature that provides a kind of dynamic resolution. Patterns with a lot of action can use e.g. 4 rows per beat (meaning each row is separated by a 16th note) while other patterns can make do with fewer rows per beat. Using a lower number where possible makes navigation and editing easier.

Hydrogenesis will always respect rows per beat for MPTM tracks. However, OpenMPT itself only caters for *rows per beat* when the track's tempo mode is set to "Modern (accurate)".
