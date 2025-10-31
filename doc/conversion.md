# Conversion

[hydrogenesis.py](../src/hydrogenesis.py) can be used to convert IT/MPTM tracks to Hydrogen's song format. The main purpose for doing so is to be able to use Hydrogen to render the track as an audio file.

Here is how to convert one of the [example](../examples/) tracks (run from the root of this repository):

```sh
python3 src/hydrogenesis.py --template examples/GMRockKit_template.h2song --output out.h2song examples/Were_not_gonna_take_it.it
```

The template `GMRockKit_template.h2song` serves a double purpose -- both to load the drum kit for [playback](./playback.md) and to provide a song skeleton for the converter.

However, there is nothing special about the template. It is mainly provided here to bootstrap the conversion process. Once we have generated our `out.h2song`, we can just as well use that as the template for subsequent conversions:

```sh
python3 src/hydrogenesis.py --template out.h2song --output out.h2song examples/Were_not_gonna_take_it.it
```

The template is only read by Hydrogenesis, not written. However, when using the same file as both template and output (as above), then the converter will first read the file and then overwrite it. This is not a problem; the new file is equivalent to the old file when viewed as a template.
