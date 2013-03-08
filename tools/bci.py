#!/usr/bin/python2.5
"""BarcodeImage class to generate images from barcode integer streams."""
__author__ = 'Elmer de Looff <elmer@underdark.nl>'
__version__ = '0.3'
__all__ = 'BarcodeImage',

# Standard modules
import cStringIO
import Image
import ImageDraw
import ImageFont


class BarcodeImage(object):
  """Creates images for one-dimensional barcodes."""
  def __init__(self, coder, **options):
    """Initializes a new BarcodeImage generator.

    Arguments:
      @ coder: barcode generator
        A callable object that takes an iterable and returns a string of ones
        and zeroes that describes the barcode.
      % barwidth: int ~~ 1
        The width of the smallest bar in pixels.
      % dpi: int ~~ 96
        Print resolution of the generated images.
      % font_file: str ~~ None
        Font file to use for the barcode text. This should be a full pathname
        to a True- or Open Type font. If omitted, the default (courier) is used.
      % font_size: int ~~ 9
        The font size to use with the given font_file. This is a size in points.
      % format: str ~~ 'png'
        The output image format.
      % height: int ~~ 30 * barwidth
        The height of the generated images.
      % print_text: bool ~~ True
        Configures whether text should be printed on the baseline of the image.
    """
    self.coder = coder
    self.options = options
    self.options.setdefault('barwidth', 1)
    self.options.setdefault('height', 30 * self.options['barwidth'])
    self.options.setdefault('dpi', 96)
    self.options.setdefault('format', 'png')
    self.options.setdefault('print_text', True)
    if 'font_file' in self.options:
      self.font = ImageFont.truetype(self.options['font_file'],
                                     self.options['font_size'])
    else:
      self.font = ImageFont.load_default()

  def __call__(self, code, alt_text=None, output=None, raw=False):
    """Creates a barcode image of the given input text.

    Arguments:
      @ code: iterable
        The input for the barcode generator. Use a string for regular input.
        A list of strings can be used to insert control symbols etc.
      % alt_text: str ~~ None
        Alternate text to put under the barcode instead of the code itself.
        This will not work if print_text is set to False for this instance.
      % output: str / file-like obj ~~ StringIO
        The return value and image creation depends on the type of this arg:
        - None (or undefined): The return value will be a StringIO with the
          byte content of the image written to it.
        - str: A file with the given name will be created and the image will be
          saved in that file, and the return will be that file() instance.
          If a file with the given name already exists, IT WILL BE OVERWRITTEN.
        - file: The contents of the image will be written to this object.
      % raw: boolean ~~ False
        No file will be generated and return value will be the PIL image *only*

    Returns:
      2-tuple: file-like obj of image, str of image format extension.
      PIL Image(): if raw=True is given for the call.
    """
    barcode = self.coder(code)

    # Create a new image of appropriate size for the barcode.
    width = len(barcode) * self.options['barwidth']
    height = self.options['height']
    image = Image.new(mode='1', size=(width, height), color=255)

    # Draw the bar code lines.
    draw = ImageDraw.Draw(image)
    for pos_x, bit in enumerate(barcode):
      if bit == '1':
        pos_x *= self.options['barwidth']
        # Quick & dirty fix for the barwidth=1 issue.
        if self.options['barwidth'] > 1:
          # If the barwidth is more then 1 it needs to draw a rectangle.
          draw.rectangle((pos_x, 0, pos_x + self.options['barwidth'],
                          height + 1), outline=0, fill=0)
        else:
          # If the barwidth is 1, it just needs to draw a line.
          draw.line((pos_x, 0, pos_x, height), width=self.options['barwidth'])

    if self.options['print_text']:
      image = self._AddText(image, alt_text or code)

    image.info['dpi'] = self.options['dpi'], self.options['dpi']
    if raw:
      return image
    elif not output:
      output = cStringIO.StringIO()
    elif isinstance(output, basestring):
      output = file(output, 'wb+')

    image.save(output, format=self.options['format'],
               dpi=image.info['dpi'])
    return output, self.options['format']


  def _AddText(self, image, text):
    """Adds a text to the given image instance."""
    # Check textsize and draw it in the bottom center of the barcode.
    # Also update height so that barcode is not printed over the text.
    draw = ImageDraw.Draw(image)
    width, height = image.size
    text_width, text_height = draw.textsize(text, font=self.font)
    if text_width > width:
      new_width = text_width + 10
      new_image = Image.new(
          mode='1', size=(new_width, height), color=255)
      new_image.paste(image, ((new_width - width) / 2, 0))
      width = new_width
      image = new_image
      draw = ImageDraw.Draw(image)

    # Show at most 20px of barcode on either side of the text:
    visible_margin = min(20, (width - text_width - 4) / 2)
    draw.rectangle(((visible_margin, height - text_height),
                    (width - visible_margin, height)),
                   fill=255)
    draw.text(((width - text_width) / 2, height - text_height),
              text, font=self.font)
    return image

  @staticmethod
  def _ScaleImage(image, scale):
    if scale == 1:
      return image
    width, height = image.size
    return image.resize((width * scale, height * scale))
