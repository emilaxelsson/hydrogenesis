# Examples

The [examples](../examples/) folder contains an example track and a Hydrogen template using the GMRockKit drum kit. You can use the example to try out both playback and conversion.

## Playback

First open up Hydrogen and load the template [GMRockKit_template.h2song](../examples/GMRockKit_template.h2song). The template does not contain any beats, but it ensures that the appropriate drum kit is loaded.

Next, open the track [Were_not_gonna_take_it.it](../examples/Were_not_gonna_take_it.it) in OpenMPT.

  * You may need to set the MIDI output for the FX1 plugin to match what Hydrogen is set up to listen to on your system. The settings are found on the General tab down in the Plugins section.
      - Select FX1
      - Click "Editor" and set "MIDI Output Device" to the desired device

Now, you should be able to play the track in OpenMPT and hear the sound generated from Hydrogen.

## Conversion

In addition to listening via Hydrogen, we can also convert the track to a Hydrogen song. The main purpose for doing so is so that we can use Hydrogen to render the track as an audio file. Here is how to do the conversion:

```sh
python3 src/hydrogenesis.py --template examples/GMRockKit_template.h2song --output out.h2song examples/Were_not_gonna_take_it.it
```

Note that `GMRockKit_template.h2song` serves a double purpose -- both to load the drum kit for [playback](#playback) and to provide a song skeleton for the converter.

However, there is nothing special about the template. It is mainly provided here to bootstrap the conversion process. Once we have generated our `out.h2song`, we can just as well use that as the template for subsequent conversions:

```sh
python3 src/hydrogenesis.py --template out.h2song --output out.h2song examples/Were_not_gonna_take_it.it
```

The template is only read by Hydrogenesis, not written. However, when using the same file as both template and output (as above), then the converter will first read the file and then overwrite it.
