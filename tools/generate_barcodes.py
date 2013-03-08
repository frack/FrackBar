#!/usr/bin/python
""" Barcode generator for the FrackBar database """
__author__ = "Rudi Daemen <info@kratjebierhosting.nl>"
__version__ = "0.1"

import bci
import code128
import sqlite
import os

HTMLHEAD = """
<html>
  <head>
    <title>Frack Barcode list</title>
  </head>
  <body><p>
    <table>
      <tr>
        <td><b>Barcode</b></td>
        <td><b>Description</b></td>
      </tr>"""
HTMLTAIL = """</table></p></body></html>"""

def GenFromDb(dbdir='~/.frackbar', dbfile='frackbar.sqlite', imdir='barcodes'):
  """ Generates barcodes in .png format. It uses manually defined 'special'
  codes and appends all barcodes present in the database to this list of codes
  it has to parse. Additionally generate a HTML page with the images..."""
  if dbdir.startswith('~'):
    dbdir = os.path.expanduser(dbdir)
  if not dbdir.endswith('/'):
    dbdir += '/'
  if not imdir.endswith('/'):
    imdir += '/'
  dbfile = os.path.join(dbdir, dbfile)
  imdir = os.path.join(dbdir, imdir)

  # Check if the dbfile exists, stops the operation if it doesnt exist.
  if not os.path.isfile(dbfile):
    print u"\r\n*** Database %s not found. Nothing to do...\r\n" % dbfile
    return
  # Only need to check the imdir as makedirs recursivly creates dirs.
  if not os.path.isdir(imdir):
    os.makedirs(imdir)

  # All tests evaluated propperly, let's connect things up and prepare to work!
  dbase = sqlite.Connection(dbfile)
  font = "/usr/share/fonts/truetype/ttf-dejavu/DejaVuSansMono-Bold.ttf"
  imager = bci.BarcodeImage(code128.Code128(), font_file=font, font_size=20,
                            barwidth=2, dpi=192)

  # Define the 'special' barcodes in below dictionary ...
  barcodes = [{'barcode': 'FRACKMEMBER', 'text': 'Cash mode member toggle' },
              {'barcode': 'FCC', 'text': 'No creditcard'}]

  # Now get the barcodes from the database!
  with dbase as cursor:
    barcodes += cursor.execute("""SELECT DISTINCT `barcode`, `name` AS `text`
                               FROM `product`""")
    barcodes += cursor.execute("""SELECT DISTINCT `barcode`, `barcode` AS `text`
                               FROM `creditcard`""")

  # With all the gathered resources, start generating images...
  htmlimg = ""
  print u"Generating %d barcodes ..." % len(barcodes)
  for items in barcodes:
    filename = imdir + items['barcode'] + '.png'
    imager(items['barcode'], alt_text=items['text'], output=filename)
    htmlimg += """<tr>
                    <td height='100px'><img src='%s' border=0></td>
                    <td>%s</td>
               </tr>""" % (items['barcode'] + '.png', items['text'])
  WriteHtml(htmlimg, imdir + 'barcodes.html')
  print u"Done!\r\nBarcodes can be found in %s" % imdir


def WriteHtml(htmlimg, filename):
  """ Write a HTML file with the barcodes """
  with open(filename, 'w') as dest:
    dest.write(HTMLHEAD)
    dest.write(htmlimg)
    dest.write(HTMLTAIL)


if __name__ == '__main__':
  GenFromDb()
