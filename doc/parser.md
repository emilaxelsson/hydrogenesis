# Parser

The [MPTM parser](../src/mptm_parser.py) is made specifically for Hydrogenesis and largely ignores aspects of the tracks that are not needed in the conversion to Hydrogen (see [Features and limitations](./features.md)).

A noteworthy feature of Hydrogenesis' parser is that it is able to read the pattern-specific "rows per beat" value provided by MPTM extensions. I wasn't able to find any other parser in the wild that does this. Even [libopenmpt](https://lib.openmpt.org/libopenmpt/) doesn't give access to "rows per beat", as far as I could tell (checked version 0.8.3).

The parser has a generic architecture, and it should be quite easy to extend it to cover more features. I have no plans on enhancing the parser beyond the needs of Hydrogenesis, but I'd welcome pull requests if someone wants to extend it.
