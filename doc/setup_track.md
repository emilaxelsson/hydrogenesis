# Set up track from scratch

This guide explains how to set up [OpenMPT](https://openmpt.org) and [Hydrogen](http://hydrogen-music.org) for live playback.



Hydrogen
------------------------------------------------------------------------------------------

Hydrogen will be used for playing notes sent from OpenMPT as MIDI events.

Start by opening up Hydrogen's MIDI settings and check that a suitable input port is selected. The following settings have been tested to work well on Ubuntu 24.04 (Hydrogen 1.2.4).

![](./images/h2_midi_settings.png)

Next, create a new song and load a drum kit. Adjust mixer settings as needed.

In principle, nothing else is needed on the Hydrogen side. However, it is advised to save the song after setting up the drum kit. The resulting `.h2song` file can be used as a template by the [Hydrogenesis](../src/hydrogenesis.py) converter.



OpenMPT
------------------------------------------------------------------------------------------

We will now set up an OpenMPT track from scratch in such a way that it can be used to drive Hydrogen for playback as well as be [converted](./conversion.md) to a Hydrogen song using [Hydrogenesis](../src/hydrogenesis.py).

Start by creating a new track in OpenMPT. The default format, IT (Impulse Tracker), works fine. The [MPTM extensions](#mptm-extensions) section explains additional features offered by the MPTM format. However, the instrument set up is the same regardless of format.

### Set up instruments

We will create one OpenMPT instrument for each instrument in the Hydrogen drum kit loaded [above](#hydrogen). The instruments should appear in the same order in OpenMPT and Hydrogen.

To create the first instrument:

  * Create a new instrument
  * Name it according to the corresponding instrument in the Hydrogen drum kit

    ![](./images/mpt_instr_name.png) ![](./images/h2_instr_name.png)

  * In the "Plugin / MIDI" section:
      - Select "FX1" in the dropdown

        ![](./images/mpt_instr_midi_fx1.png)

      - The plugin manager window opens. Select "MIDI Input Output" and click "Put in FX01".

        ![](./images/mpt_plugin_manager_midi.png)

      - Click "Editor"

        ![](./images/mpt_instr_midi_editor.png)

      - A settings window opens. Set "MIDI Output Device" to the same port as the MIDI input port [configured for Hydrogen](#hydrogen). Also, uncheck "Send timing messages". Timing messages are anyway ignored by Hydrogen, and they tend to bloat Hydrogen's debug log.

        ![](./images/mpt_fx1_midi_output.png)

      - Set "MIDI Program" to the same number as the instrument<sup>[1](#fn1)</sup>

        ![](./images/mpt_instr_midi.png) ![](./images/mpt_instr_number.png)

      - Set "Volume Command Handling" to "MIDI volume", and make sure that "Volume commands with note are Velocities" is checked

        ![](./images/mpt_instr_midi_volume.png)

The remaining instruments can created by duplicating the first instrument as many times as needed, and just updating the name and MIDI program number for each one.

![](./images/mpt_duplicate_instr.png)

### Tempo mode

The MPTM format supports overriding the [rows per beat](./features.md#rows-per-beat) value for individual patterns. However, this feature only has effect if the track's tempo mode is set to "Modern (accurate)".

To select modern tempo mode, go to the General tab and click the field that shows the track format (e.g. "IT (Impulse Tracker)" or "MPTM (OpenMPT)").

![](./images/mpt_general_song_properties.png)

In the Song Properties dialog:

  * Ensure that track type is set to "OpenMPT MPTM"
  * Set Tempo Mode to "Modern (accurate)"

![](./images/mpt_song_properties.png)



<br/>

#### Footnotes

<a name="fn1">1</a>:
Instruments in Hydrogen are shown in the GUI as an ordered list which can be rearranged using the mouse. The *instrument index* refers to the position in the list (starting from 1).
The MIDI program number gets interpreted by Hydrogen as the instrument index. Hence, the program number should be the same as the instrument number in OpenMPT.
Note that the instrument index is not necessarily the same as the *instrument id*. The index is simply the instrument's position in the list. The id is an internal property in Hydrogen which can be seen when viewing an `.h2song` file in an XML editor. The ids can become unordered and fragmented due to re-ordering and removal of instruments. Hydrogenesis users need not be concerned with instrument ids.
