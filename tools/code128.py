#!/usr/bin/python2.5
"""Code128 Barcode creation library

This code is based on the work of an unknown author, and comes from
  http://barcode128.blogspot.com

That code is based on EanBarCode.py submitted by Remi Inconnu on
  http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/426069

Classes:
  Code128: Emitter class for generating Code128 barcodes as 'binary' strings.
"""
__author__ = 'Elmer de Looff <elmer@underdark.nl>'
__version__ = '0.3'
__all__ = 'Code128',

# List of characters in Code 128 Subcode A; Basic alphabet and control codes.
SUBCODE_A = [' ', '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',',
             '-', '.', '/', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
             ':', ';', '<', '=', '>', '?', '@', 'A', 'B', 'C', 'D', 'E', 'F',
             'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
             'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '[', '\\', ']', '^', '_',
             '\x00', '\x01', '\x02', '\x03', '\x04', '\x05', '\x06', '\x07',
             '\x08', '\t', '\n', '\x0b', '\x0c', '\r', '\x0e', '\x0f', '\x10',
             '\x11', '\x12', '\x13', '\x14', '\x15', '\x16', '\x17', '\x18',
             '\x19', '\x1a', '\x1b', '\x1c', '\x1d', '\x1e', '\x1f', 'FNC3',
             'FNC2', 'SHIFT', 'Code C', 'Code B', 'FNC4', 'FNC1', 'START A',
             'START B', 'START C', 'STOP']

# List of characters in Code 128 Subcode B; Most commonly used for printing.
SUBCODE_B = [' ', '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',',
             '-', '.', '/', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
             ':', ';', '<', '=', '>', '?', '@', 'A', 'B', 'C', 'D', 'E', 'F',
             'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
             'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '[', '\\', ']', '^', '_', '`',
             'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
             'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
             '{', '|', '}', '~', '\x7f', 'FNC3', 'FNC2', 'SHIFT', 'Code C',
             'FNC4', 'Code A', 'FNC1', 'START A', 'START B', 'START C', 'STOP']

# List of characters in Code 128 Subcode C; Double density for digits.
SUBCODE_C = ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10',
             '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21',
             '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32',
             '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43',
             '44', '45', '46', '47', '48', '49', '50', '51', '52', '53', '54',
             '55', '56', '57', '58', '59', '60', '61', '62', '63', '64', '65',
             '66', '67', '68', '69', '70', '71', '72', '73', '74', '75', '76',
             '77', '78', '79', '80', '81', '82', '83', '84', '85', '86', '87',
             '88', '89', '90', '91', '92', '93', '94', '95', '96', '97', '98',
             '99', 'Code B', 'Code A', 'FNC1', 'START A', 'START B', 'START C',
             'STOP']

# List of element-values for the subcode entries.
ENCODED_VALUES = [
    '11011001100', '11001101100', '11001100110', '10010011000', '10010001100',
    '10001001100', '10011001000', '10011000100', '10001100100', '11001001000',
    '11001000100', '11000100100', '10110011100', '10011011100', '10011001110',
    '10111001100', '10011101100', '10011100110', '11001110010', '11001011100',
    '11001001110', '11011100100', '11001110100', '11101101110', '11101001100',
    '11100101100', '11100100110', '11101100100', '11100110100', '11100110010',
    '11011011000', '11011000110', '11000110110', '10100011000', '10001011000',
    '10001000110', '10110001000', '10001101000', '10001100010', '11010001000',
    '11000101000', '11000100010', '10110111000', '10110001110', '10001101110',
    '10111011000', '10111000110', '10001110110', '11101110110', '11010001110',
    '11000101110', '11011101000', '11011100010', '11011101110', '11101011000',
    '11101000110', '11100010110', '11101101000', '11101100010', '11100011010',
    '11101111010', '11001000010', '11110001010', '10100110000', '10100001100',
    '10010110000', '10010000110', '10000101100', '10000100110', '10110010000',
    '10110000100', '10011010000', '10011000010', '10000110100', '10000110010',
    '11000010010', '11001010000', '11110111010', '11000010100', '10001111010',
    '10100111100', '10010111100', '10010011110', '10111100100', '10011110100',
    '10011110010', '11110100100', '11110010100', '11110010010', '11011011110',
    '11011110110', '11110110110', '10101111000', '10100011110', '10001011110',
    '10111101000', '10111100010', '11110101000', '11110100010', '10111011110',
    '10111101110', '11101011110', '11110101110', '11010000100', '11010010000',
    '11010011100', '11000111010']

TERMINATION_BAR = '11'

class Code128(object):
  """Barcode generator for Code128 barcodes.

  To use this class, create an instance and call it with a string argument to
  receive an encoded string with which a barcode can be easily constructed.

  Members:
    @ A: dict
      Maps the characters of subcode A to their position and encoded value.
    @ B: dict
      Maps the characters of subcode B to their position and encoded value.
    @ C: dict
      Maps the characters of subcode C to their position and encoded value.

  Methods
    @ _ChangeSubcode
      Changes or sets the Code128 subcode to be used.
    @ _ProcessChar
      Decides on which subcode to use for processing the next character(s).
    @ _WriteElement
      Adds an element to the barcode and updates element count and checksum.
    @ _WriteEnd
      Writes checksum and closing barcode elements.
    % Calling (__call__)
      Returns the Code128 encoded string of the input.
  """
  A = dict(zip(SUBCODE_A, enumerate(ENCODED_VALUES)))
  B = dict(zip(SUBCODE_B, enumerate(ENCODED_VALUES)))
  C = dict(zip(SUBCODE_C, enumerate(ENCODED_VALUES)))

  def __init__(self, debug=False):
    """Initializes a new Code128 generator.

    Arguments:
      % debug: bool ~~ False
        Flags whether verbose debug output should be printed to the commandline.
    """
    self.barcode = []
    self.checksum = 0
    self.debug = debug
    self.subcode = {}

  def __call__(self, text):
    """Returns the Code128 encoded string of the input.

    The output will be a string consisting of ones and zeroes. A one signifies
    a bar, a zero signifies a space. The returned string is a complete and valid
    Code128 barcode (including start, stop, checksum, and termination bar).

    Arguments:
      @ text: str / iterable of str
        Input text to be converted to Code128. In case you need access to
        code128 control codes, provide an iterable with these codes specified.

    Returns:
      str: The input text as a Code128 string of ones and zeroes.
    """
    self.barcode = []
    self.subcode = {}
    self.checksum = 0
    skip_one = False
    for index in xrange(len(text)):
      if skip_one:
        # Skipping one loop since the previous encoded two digits in subcode C.
        skip_one = False
        continue
      else:
        skip_one = self._ProcessChar(index, text)

    self._WriteEnd()
    if self.debug:
      print 'Wrote %d glyphs for %d chars of input (efficiency: %.f%%)\n' % (
          len(self.barcode), len(text), 100.0 * len(text) / len(self.barcode))
    return ''.join(self.barcode)

  def _ChangeSubcode(self, subcode):
    """Changes or sets the Code128 subcode to be used.

    Arguments:
      @ subcode: str
        'A', 'B', or 'C', referring to the Code128 subcodes.
    """
    subcode_dict = getattr(self, subcode)
    if self.subcode == subcode_dict:
      return
    elif self.subcode:
      if self.debug:
        print '* Changing to subcode %s' % subcode
      self._WriteElement('Code %c' % subcode)
      self.subcode = subcode_dict
    else:
      if self.debug:
        print '* Starting in subcode %s' % subcode
      self.subcode = subcode_dict
      self._WriteElement('START %c' % subcode)

  def _ProcessChar(self, index, text):
    """Decides on which subcode to use for processing the next character(s).

    Arguments:
      @ index: int
        The character number to process.
      @ text: iterable
        The character / operator stream to process from. This is needed since
        Subcode C optimizations require lookahead.

      Returns:
        bool: whether or not the next index should be skipped by the caller.
    """
    if (len(text[index:]) >= 4 and ''.join(text[index:index + 4]).isdigit() or
        len(text[index:]) >= 2 and ''.join(text[index:index + 2]).isdigit() and
        (not self.subcode or self.subcode == self.C)):
      # Subcode C is optimized for double digit numbers and is triggered in
      # the following situations:
      # * The next four chars are numbers, changing to subcode C makes sense.
      # * The next two chars are numbers, and we are already in subcode C.
      # * The next two chars are numbers, and we still have to choose subcode.
      self._ChangeSubcode('C')
      self._WriteElement(''.join(text[index:index + 2]))
      return True

    char = text[index]
    if char not in self.subcode:
      # The character isn't in the current subcode, find one that contains it.
      # We prefer subcode B as it contains more commonly printed characters.
      if char in self.B:
        self._ChangeSubcode('B')
      elif char in self.A:
        self._ChangeSubcode('A')
      else:
        raise ValueError('Charachter %r could not be encoded.' % char)

    # By now, we have the correct subcode for the character and we can write it.
    self._WriteElement(char)

  def _WriteElement(self, element):
    """Adds an element to the barcode and updates element count and checksum.

    Arguments:
      @ element: str
        The element to add to the barcode.
    """
    if self.debug:
      print 'Writing element %r' % element
    index, value = self.subcode[element]
    self.checksum = (self.checksum + index * max(len(self.barcode), 1)) % 103
    self.barcode.append(value)

  def _WriteEnd(self):
    """Writes checksum and closing barcode elements."""
    if self.debug:
      print 'Writing checksum: #%d' % self.checksum
    self.barcode.append(ENCODED_VALUES[self.checksum])
    self.barcode.append(self.subcode['STOP'][1])  # [1] is the barcode element.
    self.barcode.append(TERMINATION_BAR)


class SymbolControlCoder(Code128):
  """Created control codes for Symbol barcode scanners.

  Works identical to Code128, only prefixing [FNC3] to all barcodes.
  This forces the Symbol to interpret the codes as configuration control codes.
  """
  def __call__(self, text):
    return super(SymbolControlCoder, self).__call__(['FNC3'] + list(text))
