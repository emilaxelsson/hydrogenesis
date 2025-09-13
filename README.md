*Note: Hydrogenesis is not yet done, but this document describes the goal.*

![](./logo.png)

# Hydrogenesis

[Hydrogen](http://hydrogen-music.org/) is great for realistic drum track generation.

[OpenMPT](https://openmpt.org/) has an efficient keyboard-friendly editing experience.

Did you ever wish you could combine the two? *Well, now you can!*

## Basic idea

Editing:

  * Set up Hydrogen as a MIDI back end for OpenMPT (see [this guide](./doc/playback.md))
  * Enjoy real-time Hydrogen playback while editing in OpenMPT

Rendering:

  * Once done with editing, use [hydrogenesis.py](./TODO) to convert the track to a Hydrogen song
  * Use Hydrogen to generate a sound file

## But why?

*Q:* Why not stick to Hydrogen alone?

*A:* Because Hydrogen is not well-suited for manual editing. It takes a lot of clicking in the UI to make just a few beats. Using the piano roll (e.g. for bass guitar) is especially cumbersome.

*Q:* Why not stick to OpenMPT alone?

*A:* Because OpenMPT does not have realistic sound generation with velocities and randomly variating samples.

## Bonus

As an added bonus, Hydrogenesis supports *tempo changes at arbitrary points in the track*. Hydrogen only allows tempo changes between measures. Hydrogenesis achieves arbitrary-point tempo changes by simply breaking measures as needed when generating Hydrogen songs.
