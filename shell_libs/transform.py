import base64

C = 0
BASE32 = 1
BASE64 = 2
BASH = 3
CSHARP = 4
DW = 5
DWORD = 6
HEX = 7
JAVA = 8
PERL = 12
PL = 13
POWERSHELL = 14
PS1 = 15
PY = 16
PYTHON = 17
RAW = 18
RB = 19
RUBY = 20
SH = 21
VBAPPLICATION = 22
VBSCRIPT = 23

_formatToName = {
    BASE32: 'BASE32',
    BASE64: 'BASE64',
    BASH: 'BASH',
    C: 'C',
    CSHARP: 'CSHARP',
    HEX: 'HEX',
    JAVA: 'JAVA',
    PERL: 'PERL',
    PL: 'PL',
    POWERSHELL: 'POWERSHELL',
    PS1: 'PS1',
    PY: 'PY',
    PYTHON: 'PYTHON',
    RAW: 'RAW',
    RB: 'RB',
    RUBY: 'RUBY',
    SH: 'SH',
    VBAPPLICATION: 'VBAPPLICATION',
    VBSCRIPT: 'VBSCRIPT',
}
_nameToFormat = {
    'BASE32': BASE32,
    'BASE64': BASE64,
    'BASH': BASH,
    'C': C,
    'CSHARP': CSHARP,
    'HEX': HEX,
    'JAVA': JAVA,
    'PERL': PERL,
    'PL': PL,
    'POWERSHELL': POWERSHELL,
    'PS1': PS1,
    'PY': PY,
    'PYTHON': PYTHON,
    'RAW': RAW,
    'RB': RB,
    'RUBY': RUBY,
    'SH': SH,
    'VBAPPLICATION': VBAPPLICATION,
    'VBSCRIPT': VBSCRIPT,
}
_formatParameters = {
    BASE32: ('', '', '', '', '', '{content}'),
    BASE64: ('', '', '', '', '', '{content}'),
    BASH: ('', '\\x', '$\'', '\'\\', '\\', 'export {var_name}=\\\n{content}'),
    SH: ('', '\\x', '$\'', '\'\\', '\\', 'export {var_name}=\\\n{content}'),
    C: (', ', '0x', '', '', '', '{content}'),
    CSHARP: (',', '0x', '', '', '', 'byte[] {var_name} = new byte[{size}] {{\n{content}\n{line_prefix}}};\n'),
    HEX: ('', '', '', '', '', '{content}'),
    JAVA: (', ', '(byte) 0x', '', '', '', 'byte[] {var_name} = new byte[] {{\n{content}\n{line_prefix}}};\n'),
    PERL: ('', '\\x', '"', '" .', '.', 'my ${var_name} = \n{content};'),
    PL: ('', '\\x', '"', '" .', '.', 'my ${var_name} = \n{content};'),
    POWERSHELL: (',', '0x', '', '', '', '[Byte[]] ${var_name} = {content}'),
    PS1: (',', '0x', '', '', '', '[Byte[]] $buf = {content}'),
    PY: ('', '\\x', '"', '"', '', '{var_name} = (\n{content}\n)'),
    PYTHON: ('', '\\x', '"', '"', '', '{var_name} = (\n{content}\n)'),
    RAW: ('', '', '', '', '', '{content}'),
    RB: ('', '\\x', '"', '" +', '+', '{var_name} = \n{content};'),
    RUBY: ('', '\\x', '"', '" +', '+', '{var_name} = \n{content};'),
    VBAPPLICATION: ('&', '', '', '', '', '{var_name}={content}'),
    VBSCRIPT: ('&', '', '', '', '', '{var_name}={content}'),
}


class Transform(object):
    _format = 0
    _line_size = -1
    _line_prefix = ''

    def __init__(self, format: str = 'c', line_size: int = -1, line_prefix: str = ''):
        self._format = Transform.parse_format(format)
        self._line_size = line_size
        self._line_prefix = line_prefix

    def format(self, data: [bytearray, bytes], bad_chars: [bytearray, bytes] = bytearray()) -> str:
        (separator, marker, sl, el, t, mask) = _formatParameters[self._format]

        return mask.format(
            var_name='buf',
            content=self._doformat(data, bad_chars).strip(' ' + t),
            size=len(data),
            line_prefix=self._line_prefix
        )

    def _doformat(self, data: [bytearray, bytes], bad_chars: [bytearray, bytes] = bytearray()) -> str:
        (separator, marker, sl, el, t, mask) = _formatParameters[self._format]

        if self._format == RAW or self._format == HEX or \
                self._format == VBSCRIPT or \
                self._format == VBAPPLICATION or \
                self._format == PS1 or \
                self._format == POWERSHELL:
            self._line_size = -1

        if self._format == BASE32 or self._format == BASE64:
            if self._format == BASE32:
                data = base64.b32encode(data)
            elif self._format == BASE64:
                data = base64.b64encode(data)

            if isinstance(data, bytes):
                data = data.decode("UTF-8")

            if self._line_size > 1:
                return f'\n'.join(
                    [
                        self._line_prefix + data[i:i + self._line_size] for i in range(0, len(data), self._line_size)
                    ]
                )
            else:
                return data
        else:
            if self._line_size > 1:
                return f'{separator}{el}\n'.join(
                    [
                        (
                                self._line_prefix + sl + separator.join(self._format_byte(x, marker, bad_chars)
                                                                   for x in data[i:i + self._line_size])
                        ) for i in range(0, len(data), self._line_size)
                    ]
                ) + el

            else:
                return self._line_prefix + sl + separator.join(self._format_byte(x, marker, bad_chars) for x in data) + el

    def _format_byte(self, byte: int, marker: str = '', bad_chars: [bytearray, bytes] = bytearray()) -> str:
        mask = '%s%s'
        if byte in bad_chars:
            mask = '{R}%s%s{W}'

        if self._format == VBSCRIPT or self._format == VBAPPLICATION:
            return mask % (marker, "Chr(" + str(int(byte)) + ")")

        return mask % (marker, format(byte, '02x'))

    @staticmethod
    def parse_format(format: [int, str]) -> int:
        if isinstance(format, int):
            if int(format) not in _formatToName:
                raise ValueError("Unknown format: %r" % format)
            rv = format
        elif str(format).upper() == format.upper():
            if format.upper() not in _nameToFormat:
                raise ValueError("Unknown format: %r" % format)
            rv = _nameToFormat[format.upper()]
        else:
            raise TypeError("Format not an integer or a valid string: %r" % format)
        return rv

    @staticmethod
    def format_list() -> list:
        return [k for k, v in _nameToFormat.items()]

    @staticmethod
    def get_name(format):
        return _formatToName[Transform.parse_format(format)]
