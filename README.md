*Note: Hydrogenesis is not yet done, but this document describes the goal.*

![](./logo.png)

# Hydrogenesis

[Hydrogen](http://hydrogen-music.org) is great for realistic drum track generation.

[OpenMPT](https://openmpt.org) has an efficient keyboard-friendly editing experience.

Did you ever wish you could combine the two? *Well, now you can!*

## Basic idea

Editing:

  * Set up Hydrogen as a MIDI back end for OpenMPT (see [this guide](./doc/playback_setup.md))
  * Enjoy real-time Hydrogen playback while editing in OpenMPT

Rendering:

  * Once done with editing, use [hydrogenesis.py](./src/hydrogenesis.py) to convert the track to a Hydrogen song
  * Use Hydrogen to generate a sound file

## But why?

*Q:* Why not stick to Hydrogen alone?

*A:* Because Hydrogen is not ideal for manual editing of entire songs. It takes a lot of clicking in the UI to add beats and make changes. Using the piano roll (e.g. for bass guitar) is especially cumbersome.

*Q:* Why not stick to OpenMPT alone?

*A:* Because OpenMPT does not have realistic sound generation with velocities and randomly variating samples.

## Examples

See [this page](./doc/examples.md).

## Bonus

As an added bonus, Hydrogenesis supports *tempo changes at arbitrary points in the track*. Hydrogen only allows tempo changes between measures. Hydrogenesis achieves arbitrary-point tempo changes by simply breaking measures as needed when generating Hydrogen songs.

## Parser

The [MPTM parser](./src/mptm_parser.py) could potentially be of wider use than for the conversion in Hydrogenesis. It does not parse all parts of an MPTM file, but it does handle some things that [libopenmpt](https://lib.openmpt.org/libopenmpt/) doesn't (as of version 0.8.3), in particular:

  * The "rows per beat" value, stored in patterns

I have no plans on extending the parser beyond the need of Hydrogenesis, but I'd welcome pull requests if someone wants to extend it.
