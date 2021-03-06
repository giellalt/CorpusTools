""" Python Character Mapping Codec cp1251 generated from 'MAPPINGS/VENDORS/MICSFT/WINDOWS/CP1251.TXT' with gencodec.py.

"""  # "

import codecs

#  Codec APIs


class Codec(codecs.Codec):
    """Implement the interface for stateless encoders/decoders."""

    def encode(self, instring, errors="strict"):
        """Encode the object instring.

        Args:
            instring (str): the string that should be encoded with this
                codec.
            errors (str): define the error handling to apply. One of
                'strict', 'replace', 'ignore',  'xmlcharrefreplace' or
                'backslashreplace'.

        Returns:
            tuple (output object, length consumed)
        """
        return codecs.charmap_encode(instring, errors, encoding_table)

    def decode(self, instring, errors="strict"):
        """Decode the object instring.

        Args:
            instring (str): the string that should be decoded with this
                codec.
            errors (str): define the error handling to apply. One of
                'strict', 'replace' or 'ignore'.

        Returns:
            tuple (output object, length consumed)
        """
        return codecs.charmap_decode(instring, errors, decoding_table)


class IncrementalEncoder(codecs.IncrementalEncoder):
    """Implement an IncrementalEncoder."""

    def encode(self, instring, final=False):
        """Encode instring.

        Args:
            instring (str): the string that should be encoded with this
                codec.

        Returns:
            output object.
        """
        return codecs.charmap_encode(instring, self.errors, encoding_table)[0]


class IncrementalDecoder(codecs.IncrementalDecoder):
    """Implement an IncrementalDecoder."""

    def decode(self, instring, final=False):
        """Decode instring.

        Args:
            instring (str): the string that should be decoded with this
                codec.

        Returns:
            output object.
        """
        return codecs.charmap_decode(instring, self.errors, decoding_table)[0]


#  encodings module API


def getregentry():
    """Get the info for this encoding."""
    return codecs.CodecInfo(
        name="meadowmari",
        encode=Codec().encode,
        decode=Codec().decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=codecs.StreamReader,
        streamwriter=codecs.StreamWriter,
    )


#  Decoding Table

decoding_table = (
    "\x00"  # 0x00 -> NULL
    "\x01"  # 0x01 -> START OF HEADING
    "\x02"  # 0x02 -> START OF TEXT
    "\x03"  # 0x03 -> END OF TEXT
    "\x04"  # 0x04 -> END OF TRANSMISSION
    "\x05"  # 0x05 -> ENQUIRY
    "\x06"  # 0x06 -> ACKNOWLEDGE
    "\x07"  # 0x07 -> BELL
    "\x08"  # 0x08 -> BACKSPACE
    "\t"  # 0x09 -> HORIZONTAL TABULATION
    "\n"  # 0x0A -> LINE FEED
    "\x0b"  # 0x0B -> VERTICAL TABULATION
    "\x0c"  # 0x0C -> FORM FEED
    "\r"  # 0x0D -> CARRIAGE RETURN
    "\x0e"  # 0x0E -> SHIFT OUT
    "\x0f"  # 0x0F -> SHIFT IN
    "\x10"  # 0x10 -> DATA LINK ESCAPE
    "\x11"  # 0x11 -> DEVICE CONTROL ONE
    "\x12"  # 0x12 -> DEVICE CONTROL TWO
    "\x13"  # 0x13 -> DEVICE CONTROL THREE
    "\x14"  # 0x14 -> DEVICE CONTROL FOUR
    "\x15"  # 0x15 -> NEGATIVE ACKNOWLEDGE
    "\x16"  # 0x16 -> SYNCHRONOUS IDLE
    "\x17"  # 0x17 -> END OF TRANSMISSION BLOCK
    "\x18"  # 0x18 -> CANCEL
    "\x19"  # 0x19 -> END OF MEDIUM
    "\x1a"  # 0x1A -> SUBSTITUTE
    "\x1b"  # 0x1B -> ESCAPE
    "\x1c"  # 0x1C -> FILE SEPARATOR
    "\x1d"  # 0x1D -> GROUP SEPARATOR
    "\x1e"  # 0x1E -> RECORD SEPARATOR
    "\x1f"  # 0x1F -> UNIT SEPARATOR
    " "  # 0x20 -> SPACE
    "!"  # 0x21 -> EXCLAMATION MARK
    '"'  # 0x22 -> QUOTATION MARK
    "#"  # 0x23 -> NUMBER SIGN
    "$"  # 0x24 -> DOLLAR SIGN
    "%"  # 0x25 -> PERCENT SIGN
    "&"  # 0x26 -> AMPERSAND
    "'"  # 0x27 -> APOSTROPHE
    "("  # 0x28 -> LEFT PARENTHESIS
    ")"  # 0x29 -> RIGHT PARENTHESIS
    "*"  # 0x2A -> ASTERISK
    "+"  # 0x2B -> PLUS SIGN
    ","  # 0x2C -> COMMA
    "-"  # 0x2D -> HYPHEN-MINUS
    "."  # 0x2E -> FULL STOP
    "/"  # 0x2F -> SOLIDUS
    "0"  # 0x30 -> DIGIT ZERO
    "1"  # 0x31 -> DIGIT ONE
    "2"  # 0x32 -> DIGIT TWO
    "3"  # 0x33 -> DIGIT THREE
    "4"  # 0x34 -> DIGIT FOUR
    "5"  # 0x35 -> DIGIT FIVE
    "6"  # 0x36 -> DIGIT SIX
    "7"  # 0x37 -> DIGIT SEVEN
    "8"  # 0x38 -> DIGIT EIGHT
    "9"  # 0x39 -> DIGIT NINE
    ":"  # 0x3A -> COLON
    ";"  # 0x3B -> SEMICOLON
    "<"  # 0x3C -> LESS-THAN SIGN
    "="  # 0x3D -> EQUALS SIGN
    ">"  # 0x3E -> GREATER-THAN SIGN
    "?"  # 0x3F -> QUESTION MARK
    "@"  # 0x40 -> COMMERCIAL AT
    "A"  # 0x41 -> LATIN CAPITAL LETTER A
    "B"  # 0x42 -> LATIN CAPITAL LETTER B
    "C"  # 0x43 -> LATIN CAPITAL LETTER C
    "D"  # 0x44 -> LATIN CAPITAL LETTER D
    "E"  # 0x45 -> LATIN CAPITAL LETTER E
    "F"  # 0x46 -> LATIN CAPITAL LETTER F
    "G"  # 0x47 -> LATIN CAPITAL LETTER G
    "H"  # 0x48 -> LATIN CAPITAL LETTER H
    "I"  # 0x49 -> LATIN CAPITAL LETTER I
    "J"  # 0x4A -> LATIN CAPITAL LETTER J
    "K"  # 0x4B -> LATIN CAPITAL LETTER K
    "L"  # 0x4C -> LATIN CAPITAL LETTER L
    "M"  # 0x4D -> LATIN CAPITAL LETTER M
    "N"  # 0x4E -> LATIN CAPITAL LETTER N
    "O"  # 0x4F -> LATIN CAPITAL LETTER O
    "P"  # 0x50 -> LATIN CAPITAL LETTER P
    "Q"  # 0x51 -> LATIN CAPITAL LETTER Q
    "R"  # 0x52 -> LATIN CAPITAL LETTER R
    "S"  # 0x53 -> LATIN CAPITAL LETTER S
    "T"  # 0x54 -> LATIN CAPITAL LETTER T
    "U"  # 0x55 -> LATIN CAPITAL LETTER U
    "V"  # 0x56 -> LATIN CAPITAL LETTER V
    "W"  # 0x57 -> LATIN CAPITAL LETTER W
    "X"  # 0x58 -> LATIN CAPITAL LETTER X
    "Y"  # 0x59 -> LATIN CAPITAL LETTER Y
    "Z"  # 0x5A -> LATIN CAPITAL LETTER Z
    "["  # 0x5B -> LEFT SQUARE BRACKET
    "\\"  # 0x5C -> REVERSE SOLIDUS
    "]"  # 0x5D -> RIGHT SQUARE BRACKET
    "^"  # 0x5E -> CIRCUMFLEX ACCENT
    "_"  # 0x5F -> LOW LINE
    "`"  # 0x60 -> GRAVE ACCENT
    "a"  # 0x61 -> LATIN SMALL LETTER A
    "b"  # 0x62 -> LATIN SMALL LETTER B
    "c"  # 0x63 -> LATIN SMALL LETTER C
    "d"  # 0x64 -> LATIN SMALL LETTER D
    "e"  # 0x65 -> LATIN SMALL LETTER E
    "f"  # 0x66 -> LATIN SMALL LETTER F
    "g"  # 0x67 -> LATIN SMALL LETTER G
    "h"  # 0x68 -> LATIN SMALL LETTER H
    "i"  # 0x69 -> LATIN SMALL LETTER I
    "j"  # 0x6A -> LATIN SMALL LETTER J
    "k"  # 0x6B -> LATIN SMALL LETTER K
    "l"  # 0x6C -> LATIN SMALL LETTER L
    "m"  # 0x6D -> LATIN SMALL LETTER M
    "n"  # 0x6E -> LATIN SMALL LETTER N
    "o"  # 0x6F -> LATIN SMALL LETTER O
    "p"  # 0x70 -> LATIN SMALL LETTER P
    "q"  # 0x71 -> LATIN SMALL LETTER Q
    "r"  # 0x72 -> LATIN SMALL LETTER R
    "s"  # 0x73 -> LATIN SMALL LETTER S
    "t"  # 0x74 -> LATIN SMALL LETTER T
    "u"  # 0x75 -> LATIN SMALL LETTER U
    "v"  # 0x76 -> LATIN SMALL LETTER V
    "w"  # 0x77 -> LATIN SMALL LETTER W
    "x"  # 0x78 -> LATIN SMALL LETTER X
    "y"  # 0x79 -> LATIN SMALL LETTER Y
    "z"  # 0x7A -> LATIN SMALL LETTER Z
    "{"  # 0x7B -> LEFT CURLY BRACKET
    "|"  # 0x7C -> VERTICAL LINE
    "}"  # 0x7D -> RIGHT CURLY BRACKET
    "~"  # 0x7E -> TILDE
    "\x7f"  # 0x7F -> DELETE
    "??"  # 0x80 -> CYRILLIC CAPITAL LETTER DJE
    "??"  # 0x81 -> CYRILLIC CAPITAL LETTER GJE
    "???"  # 0x82 -> SINGLE LOW-9 QUOTATION MARK
    "??"  # 0x83 -> CYRILLIC SMALL LETTER GJE
    "???"  # 0x84 -> DOUBLE LOW-9 QUOTATION MARK
    "???"  # 0x85 -> HORIZONTAL ELLIPSIS
    "???"  # 0x86 -> DAGGER
    "???"  # 0x87 -> DOUBLE DAGGER
    "??"  # 0x88 -> CYRILLIC CAPITAL LIGATURE EN GHE
    "??"  # 0x89 -> CYRILLIC SMALL LIGATURE EN
    "??"  # 0x8A -> CYRILLIC CAPITAL LETTER LJE
    "???"  # 0x8B -> SINGLE LEFT-POINTING ANGLE QUOTATION MARK
    "??"  # 0x8C -> CYRILLIC CAPITAL LETTER NJE
    "??"  # 0x8D -> CYRILLIC CAPITAL LETTER KJE
    "??"  # 0x8E -> CYRILLIC CAPITAL LETTER TSHE
    "??"  # 0x8F -> CYRILLIC CAPITAL LETTER DZHE
    "??"  # 0x90 -> CYRILLIC SMALL LETTER DJE
    "\u2018"  # 0x91 -> LEFT SINGLE QUOTATION MARK
    "\u2019"  # 0x92 -> RIGHT SINGLE QUOTATION MARK
    "\u201c"  # 0x93 -> LEFT DOUBLE QUOTATION MARK
    "\u201d"  # 0x94 -> RIGHT DOUBLE QUOTATION MARK
    "\u2022"  # 0x95 -> BULLET
    "\u2013"  # 0x96 -> EN DASH
    "\u2014"  # 0x97 -> EM DASH
    "\ufffe"  # 0x98 -> UNDEFINED
    "??"  # 0x99 -> CYRILLIC CAPITAL LETTER U WITH DIAERESIS
    "??"  # 0x9A -> CYRILLIC SMALL LETTER LJE
    "???"  # 0x9B -> SINGLE RIGHT-POINTING ANGLE QUOTATION MARK
    "??"  # 0x9C -> CYRILLIC SMALL LETTER NJE
    "??"  # 0x9D -> CYRILLIC SMALL LETTER KJE
    "??"  # 0x9E -> CYRILLIC SMALL LETTER TSHE
    "??"  # 0x9F -> CYRILLIC SMALL LETTER DZHE
    "\xa0"  # 0xA0 -> NO-BREAK SPACE
    "??"  # 0xA1 -> CYRILLIC CAPITAL LETTER SHORT U
    "??"  # 0xA2 -> CYRILLIC SMALL LETTER U WITH DIAERESIS
    "??"  # 0xA3 -> CYRILLIC CAPITAL LETTER JE
    "\xa4"  # 0xA4 -> CURRENCY SIGN
    "??"  # 0xA5 -> CYRILLIC CAPITAL LETTER GHE WITH UPTURN
    "\xa6"  # 0xA6 -> BROKEN BAR
    "\xa7"  # 0xA7 -> SECTION SIGN
    "??"  # 0xA8 -> CYRILLIC CAPITAL LETTER IO
    "\xa9"  # 0xA9 -> COPYRIGHT SIGN
    "??"  # 0xAA -> CYRILLIC CAPITAL LETTER O WITH DIAERESIS
    "\xab"  # 0xAB -> LEFT-POINTING DOUBLE ANGLE QUOTATION MARK
    "\xac"  # 0xAC -> NOT SIGN
    "\xad"  # 0xAD -> SOFT HYPHEN
    "??"  # 0xAE -> REGISTERED SIGN
    "??"  # 0xAF -> CYRILLIC CAPITAL LETTER YI
    "\xb0"  # 0xB0 -> DEGREE SIGN
    "\xb1"  # 0xB1 -> PLUS-MINUS SIGN
    "??"  # 0xB2 -> CYRILLIC CAPITAL LETTER BYELORUSSIAN-UKRAINIAN I
    "??"  # 0xB3 -> CYRILLIC SMALL LETTER BYELORUSSIAN-UKRAINIAN I
    "??"  # 0xB4 -> CYRILLIC SMALL LETTER GHE WITH UPTURN
    "\xb5"  # 0xB5 -> MICRO SIGN
    "\xb6"  # 0xB6 -> PILCROW SIGN
    "\xb7"  # 0xB7 -> MIDDLE DOT
    "??"  # 0xB8 -> CYRILLIC SMALL LETTER IO
    "\u2116"  # 0xB9 -> NUMERO SIGN
    "??"  # 0xBA -> CYRILLIC SMALL LETTER O WITH DIAERESIS
    "\xbb"  # 0xBB -> RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK
    "??"  # 0xBC -> CYRILLIC SMALL LETTER JE
    "??"  # 0xBD -> CYRILLIC CAPITAL LETTER DZE
    "??"  # 0xBE -> CYRILLIC SMALL LETTER DZE
    "??"  # 0xBF -> CYRILLIC SMALL LETTER YI
    "??"  # 0xC0 -> CYRILLIC CAPITAL LETTER A
    "??"  # 0xC1 -> CYRILLIC CAPITAL LETTER BE
    "??"  # 0xC2 -> CYRILLIC CAPITAL LETTER VE
    "??"  # 0xC3 -> CYRILLIC CAPITAL LETTER GHE
    "??"  # 0xC4 -> CYRILLIC CAPITAL LETTER DE
    "??"  # 0xC5 -> CYRILLIC CAPITAL LETTER IE
    "??"  # 0xC6 -> CYRILLIC CAPITAL LETTER ZHE
    "??"  # 0xC7 -> CYRILLIC CAPITAL LETTER ZE
    "??"  # 0xC8 -> CYRILLIC CAPITAL LETTER I
    "??"  # 0xC9 -> CYRILLIC CAPITAL LETTER SHORT I
    "??"  # 0xCA -> CYRILLIC CAPITAL LETTER KA
    "??"  # 0xCB -> CYRILLIC CAPITAL LETTER EL
    "??"  # 0xCC -> CYRILLIC CAPITAL LETTER EM
    "??"  # 0xCD -> CYRILLIC CAPITAL LETTER EN
    "??"  # 0xCE -> CYRILLIC CAPITAL LETTER O
    "??"  # 0xCF -> CYRILLIC CAPITAL LETTER PE
    "??"  # 0xD0 -> CYRILLIC CAPITAL LETTER ER
    "??"  # 0xD1 -> CYRILLIC CAPITAL LETTER ES
    "??"  # 0xD2 -> CYRILLIC CAPITAL LETTER TE
    "??"  # 0xD3 -> CYRILLIC CAPITAL LETTER U
    "??"  # 0xD4 -> CYRILLIC CAPITAL LETTER EF
    "??"  # 0xD5 -> CYRILLIC CAPITAL LETTER HA
    "??"  # 0xD6 -> CYRILLIC CAPITAL LETTER TSE
    "??"  # 0xD7 -> CYRILLIC CAPITAL LETTER CHE
    "??"  # 0xD8 -> CYRILLIC CAPITAL LETTER SHA
    "??"  # 0xD9 -> CYRILLIC CAPITAL LETTER SHCHA
    "??"  # 0xDA -> CYRILLIC CAPITAL LETTER HARD SIGN
    "??"  # 0xDB -> CYRILLIC CAPITAL LETTER YERU
    "??"  # 0xDC -> CYRILLIC CAPITAL LETTER SOFT SIGN
    "??"  # 0xDD -> CYRILLIC CAPITAL LETTER E
    "??"  # 0xDE -> CYRILLIC CAPITAL LETTER YU
    "??"  # 0xDF -> CYRILLIC CAPITAL LETTER YA
    "??"  # 0xE0 -> CYRILLIC SMALL LETTER A
    "??"  # 0xE1 -> CYRILLIC SMALL LETTER BE
    "??"  # 0xE2 -> CYRILLIC SMALL LETTER VE
    "??"  # 0xE3 -> CYRILLIC SMALL LETTER GHE
    "??"  # 0xE4 -> CYRILLIC SMALL LETTER DE
    "??"  # 0xE5 -> CYRILLIC SMALL LETTER IE
    "??"  # 0xE6 -> CYRILLIC SMALL LETTER ZHE
    "??"  # 0xE7 -> CYRILLIC SMALL LETTER ZE
    "??"  # 0xE8 -> CYRILLIC SMALL LETTER I
    "??"  # 0xE9 -> CYRILLIC SMALL LETTER SHORT I
    "??"  # 0xEA -> CYRILLIC SMALL LETTER KA
    "??"  # 0xEB -> CYRILLIC SMALL LETTER EL
    "??"  # 0xEC -> CYRILLIC SMALL LETTER EM
    "??"  # 0xED -> CYRILLIC SMALL LETTER EN
    "??"  # 0xEE -> CYRILLIC SMALL LETTER O
    "??"  # 0xEF -> CYRILLIC SMALL LETTER PE
    "??"  # 0xF0 -> CYRILLIC SMALL LETTER ER
    "??"  # 0xF1 -> CYRILLIC SMALL LETTER ES
    "??"  # 0xF2 -> CYRILLIC SMALL LETTER TE
    "??"  # 0xF3 -> CYRILLIC SMALL LETTER U
    "??"  # 0xF4 -> CYRILLIC SMALL LETTER EF
    "??"  # 0xF5 -> CYRILLIC SMALL LETTER HA
    "??"  # 0xF6 -> CYRILLIC SMALL LETTER TSE
    "??"  # 0xF7 -> CYRILLIC SMALL LETTER CHE
    "??"  # 0xF8 -> CYRILLIC SMALL LETTER SHA
    "??"  # 0xF9 -> CYRILLIC SMALL LETTER SHCHA
    "??"  # 0xFA -> CYRILLIC SMALL LETTER HARD SIGN
    "??"  # 0xFB -> CYRILLIC SMALL LETTER YERU
    "??"  # 0xFC -> CYRILLIC SMALL LETTER SOFT SIGN
    "??"  # 0xFD -> CYRILLIC SMALL LETTER E
    "??"  # 0xFE -> CYRILLIC SMALL LETTER YU
    "??"  # 0xFF -> CYRILLIC SMALL LETTER YA
)

#  Encoding table
encoding_table = codecs.charmap_build(decoding_table)


def lookup(encoding):
    """Lookup the name of the encoding.

    Args:
        encoding (str): name of the encoding

    Returns:
        Codecs.CodecInfo if encoding is the name of the encoding of
            this file, None otherwise.
    """
    if encoding == "meadowmari":
        return getregentry()
    return None


codecs.register(lookup)
