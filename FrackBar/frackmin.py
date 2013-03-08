#!/usr/bin/python2.6
"""FrackBar GUI backend for administration purposes."""
__author__ = "Rudi Daemen <info@kratjebierhosting.nl>"
__version__ = "1.2"

import datetime
import os
import gtk
import frackdb
import threading
import logging

class FrackMin(object):
  """ Opens the AdminGui window """
  def __init__(self):
    self.timer = threading.Timer(None, 0)
    try:
      datetime.datetime(datetime.date.today().year, 2, 29)
      self.lastdaymonth = { 1: 31, 2: 29, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31,
           8: 31, 9: 30, 10: 31, 11: 30, 12: 31 }
    except ValueError:
      self.lastdaymonth = { 1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31,
           8: 31, 9: 30, 10: 31, 11: 30, 12: 31 }
    self.dbase = frackdb.FrackDb()
    self.builder = gtk.Builder()
    self._StartGui()

  def _StartGui(self):
    self.builder.add_from_file(os.path.join(
        os.path.dirname(__file__), 'frackmin.glade'))
    self.builder.connect_signals(self)
    dialog = self.builder.get_object('AdminGui')
    dialog.connect('delete-event', dialog.hide_on_delete)
    dialog.show()

  @staticmethod
  def _Main():
    try:
      gtk.gdk.threads_init()
      gtk.main()
    except Exception:
      logging.exception("Frackmin crashed!")
      raise

  @staticmethod
  def _Exit(*_args):
    raise SystemExit

  # InfoDialog to interact with the end-user in a more obvious way
  def InfoDialog(self, message, timeout=3, error=False):
    """ Handles the InfoDialog. Pass the message and the time it should remain
    visible """
    logging.debug("InfoDialog called: message=%r, error=%s", message, error)
    if error:
      pango = "<span foreground=\"red\" size=\"large\">%s</span>" % message
    else:
      pango = "<span size=\"large\">%s</span>" % message
    self.builder.get_object('InfoDialog').set_markup(pango)
    self.builder.get_object('DialogClose').set_label("Closing in %i seconds..."
                                                     % timeout)
    self.builder.get_object('InfoDialog').connect('delete-event',
        self.builder.get_object('InfoDialog').hide_on_delete)
    self.builder.get_object('InfoDialog').show()
    self.timer = threading.Timer(timeout, self.DialogClose_clicked_cb)
    self.timer.start()

  def DialogClose_clicked_cb(self, data=None):
    """ The very impatient persons can close the dialog by hand. This will also
    cancel the running close-dialog timer """
    self.timer.cancel()
    self.builder.get_object('InfoDialog').hide()

  # All button handling for the Admin GUI.
  def AdminClose_clicked_cb(self, data=None):
    """ Closes the AdminGui, resets and opens KassaGui """
    self.builder.get_object('AdminGui').destroy()

  def AdminDay_clicked_cb(self, data=None):
    """ Makes the AdminGui show all sales made today """
    self.AdminSalesPrint(datetime.datetime.now().strftime('%Y-%m-%d'))

  def AdminMonth_clicked_cb(self, data=None):
    """ Makes the AdminGui show all sales made this month """
    self.AdminSalesPrint(datetime.datetime.now().strftime('%Y-%m'))

  def AdminYear_clicked_cb(self, data=None):
    """ Makes the AdminGui show all sales made this year """
    self.AdminSalesPrint(datetime.datetime.now().strftime('%Y'))

  def AdminLDay_clicked_cb(self, data=None):
    """ Makes the AdminGui show all sales made yesterday """
    date = datetime.datetime.now() - datetime.timedelta(days=1)
    self.AdminSalesPrint(date.strftime('%Y-%m-%d'))

  def AdminLMonth_clicked_cb(self, data=None):
    """ Makes the AdminGui show all sales made last month """
    month = datetime.date.today().month
    date = (datetime.datetime.now() -
        datetime.timedelta(days=self.lastdaymonth[month]))
    self.AdminSalesPrint(date.strftime('%Y-%m'))

  def AdminLYear_clicked_cb(self, data=None):
    """ Makes the AdminGui show all sales made last year """
    self.AdminSalesPrint('%s' % (datetime.date.today().year - 1))

  def AdminTotal_clicked_cb(self, data=None):
    """ Print all sales regardless of date """
    self.AdminSalesPrint()

  def AdminCc_clicked_cb(self, data=None):
    """ Print all creditcards information and their credit """
    self.builder.get_object('AdminCol1').get_buffer().set_text(u"\nCard ID\n")
    self.builder.get_object('AdminCol2').get_buffer().set_text(
        u"\nCreation date\n")
    self.builder.get_object('AdminCol3').get_buffer().set_text(u"\nBarcode\n")
    self.builder.get_object('AdminCol4').get_buffer().set_text(
        u"\nMember/Visitor\n")
    self.builder.get_object('AdminCol5').get_buffer().set_text(
        u"\nRemaining credit\n")
    self.builder.get_object('AdminCol6').get_buffer().set_text('')
    self.builder.get_object('AdminCol7').get_buffer().set_text('')
    self.builder.get_object('AdminCol8').get_buffer().set_text('')
    self.builder.get_object('AdminCol9').get_buffer().set_text('')
    self.builder.get_object('AdminCol0').get_buffer().set_text('')
    # Clear the other columns because it is not using all of them
    for items in self.dbase.GetCards():
      member = 'Visitor'
      if items['member']:
        member = 'Member'
      self.builder.get_object('AdminCol1').get_buffer().insert_at_cursor(
          u"%i\n" % items['ID'])
      self.builder.get_object('AdminCol2').get_buffer().insert_at_cursor(
          u"%s\n" % items['datetime'])
      self.builder.get_object('AdminCol3').get_buffer().insert_at_cursor(
          u"%s\n" % items['barcode'])
      self.builder.get_object('AdminCol4').get_buffer().insert_at_cursor(
          u"%s\n" % member)
      self.builder.get_object('AdminCol5').get_buffer().insert_at_cursor(
          u"\u20AC%.2f\n" % items['credit'])

  def AdminSalesPrint(self, date=''):
    """ This prints the header of the sales overview """
    self.builder.get_object('AdminCol1').get_buffer().set_text(
        u"\nID\n")
    self.builder.get_object('AdminCol2').get_buffer().set_text(
        u"\nName\n")
    self.builder.get_object('AdminCol3').get_buffer().set_text(
        u"Guest\nprice\n")
    self.builder.get_object('AdminCol4').get_buffer().set_text(
        u"Guest\nsales\n")
    self.builder.get_object('AdminCol5').get_buffer().set_text(
        u"Guest\nturnover\n")
    self.builder.get_object('AdminCol6').get_buffer().set_text(
        u"Member\nprice\n")
    self.builder.get_object('AdminCol7').get_buffer().set_text(
        u"Member\nsales\n")
    self.builder.get_object('AdminCol8').get_buffer().set_text(
        u"Member\nturnover\n")
    self.builder.get_object('AdminCol9').get_buffer().set_text(
        u"Total\nsales\n")
    self.builder.get_object('AdminCol0').get_buffer().set_text(
        u"Total\nturnover\n")
    totalturn = 0
    for items in self.dbase.ProdSales(date):
      visturn = float(items['VisPrice']) * float(items['VisSales'])
      memturn = float(items['MemPrice']) * float(items['MemSales'])
      totalturn = totalturn + memturn + visturn
      self.builder.get_object('AdminCol1').get_buffer().insert_at_cursor(
          u"%i\n" % items['ID'])
      self.builder.get_object('AdminCol2').get_buffer().insert_at_cursor(
          u"%s\n" % items['ProdName'])
      self.builder.get_object('AdminCol3').get_buffer().insert_at_cursor(
          u"\u20AC%.2f\n" % items['VisPrice'])
      self.builder.get_object('AdminCol4').get_buffer().insert_at_cursor(
          u"%i\n" % items['VisSales'])
      self.builder.get_object('AdminCol5').get_buffer().insert_at_cursor(
          u"\u20AC%.2f\n" % visturn)
      self.builder.get_object('AdminCol6').get_buffer().insert_at_cursor(
          u"\u20AC%.2f\n" % items['MemPrice'])
      self.builder.get_object('AdminCol7').get_buffer().insert_at_cursor(
          u"%i\n" % items['MemSales'])
      self.builder.get_object('AdminCol8').get_buffer().insert_at_cursor(
          u"\u20AC%.2f\n" % memturn)
      self.builder.get_object('AdminCol9').get_buffer().insert_at_cursor(
          u"%i\n" % (items['VisSales'] + items['MemSales']))
      self.builder.get_object('AdminCol0').get_buffer().insert_at_cursor(
          u"\u20AC%.2f\n" % (memturn + visturn))
    self.builder.get_object('AdminCol9').get_buffer().insert_at_cursor(
        u"\nTotal:\n\u20AC%.2f" % totalturn)
    if not date == '':
      self.builder.get_object('AdminCol2').get_buffer().insert_at_cursor(
          u"\nSales matching\ndates:\n%s*" % date)

  def AdminProd_clicked_cb(self, data=None):
    """ The UpdateProduct button is pressed """
    self.UpdateDialog('product')

  def AdminCard_clicked_cb(self, data=None):
    """ The Create-Card button is pressed """
    self.UpdateDialog('card')

  def UpdateDialog(self, update):
    """ Handles the UpdateProduct Dialog """
    dialog = self.builder.get_object('UpdateDialog')
    dialog.connect('delete-event', dialog.hide_on_delete)
    dialog.show()
    logging.debug("UpdateDialog called: mode=%r", update)
    self.UpdateCancel_clicked_cb()
    if update == 'product':
      self.builder.get_object('UpdateInfo').set_text(u"Please provide the "
        u"following details\r\nto create/update a product:")
      self.builder.get_object('UpdateLbl1').set_text('Product Barcode:')
      self.builder.get_object('UpdateLbl2').set_text('Product Name:')
      self.builder.get_object('UpdateLbl3').set_text('Member Price:')
      self.builder.get_object('UpdateLbl4').set_text('Visitor Price:')
      self.builder.get_object('UpdateLbl4').show()
      self.builder.get_object('UpdateIn4').show()
    else:
      self.builder.get_object('UpdateInfo').set_text(u"Please provide the "
        u"following details\r\nto create a creditcard:")
      self.builder.get_object('UpdateLbl1').set_text('Barcode:')
      self.builder.get_object('UpdateLbl2').set_text('Member:')
      self.builder.get_object('UpdateLbl3').set_text('Credit:')
      self.builder.get_object('UpdateLbl4').hide()
      self.builder.get_object('UpdateIn4').hide()
      self.builder.get_object('UpdateLbl4').set_text('card')
      self.builder.get_object('UpdateIn1').set_text('FCC-')
      self.builder.get_object('UpdateIn2').set_text('yes')
    dialog.show()

  def UpdateCancel_clicked_cb(self, data=None):
    """ Handles the Reset button """
    self.builder.get_object('UpdateIn1').set_text('')
    self.builder.get_object('UpdateIn2').set_text('')
    self.builder.get_object('UpdateIn3').set_text('0.00')
    self.builder.get_object('UpdateIn4').set_text('0.00')

  def UpdateClose_clicked_cb(self, data=None):
    """ Handles the Close button """
    self.UpdateCancel_clicked_cb()
    self.builder.get_object('UpdateDialog').hide()

  def UpdateSubmit_clicked_cb(self, data=None):
    """ Handles the submit button, does several checks on input before sending
    it to the database. On error it does NOT reset the input fields. """
    barcode = self.builder.get_object('UpdateIn1').get_text().decode('utf-8')
    input2 = self.builder.get_object('UpdateIn2').get_text().decode('utf-8')
    value1 = self.builder.get_object('UpdateIn3').get_text().decode('utf-8')
    value2 = self.builder.get_object('UpdateIn4').get_text().decode('utf-8')
    mode = self.builder.get_object('UpdateLbl4').get_text()

    #Input tests, value2 always has valid input when it is hidden:
    if '' in (barcode, input2, value1, value2):
      # all fields are required!
      self.InfoDialog(u"All input fields are required!\nPlease try again...",
                      error=True)
      return
    if barcode in ('FRACKMEMBER', 'FCC', 'FCC-'):
      # These are the special codes, not allowed for products.
      self.InfoDialog(u"Barcode \"%s\" is not allowed.\nPlease choose a "
                      u"different barcode." % barcode, error=True)
      return
    try:
      # Money values must be float.
      value1 = float(value1)
      value2 = float(value2)
    except ValueError:
      self.InfoDialog(u"Please use numbers only for cash values!\nUse the dot "
                      u"(.) as decimal delimiter.", error=True)
      return

    # Just a few more checks to make sure if the data is correct for cardmode.
    # For product mode we don't care any further about the first two input
    # fields as they contain a barcode and a name the user can choose.
    if barcode.startswith("FCC-"):
      #the frack creditcard prefix is found!
      if not mode == 'card':
        #but oh noes, it is not in cardmode!!!
        self.InfoDialog(u"Barcode \"%s\" is not allowed for a product.\nPlease "
                        u"choose a different barcode." % barcode, error=True)
        return
      else:
        # Woot! Cardmode is active now!!
        if not input2.lower() in ('yes','no'):
          # Need to make sure it is a 'usable' string...
          self.InfoDialog(u"Invalid input in Member field.\nPlease type \"yes\""
                          u" or \"no\".", error=True)
          return
        if input2.lower() == 'yes':
          member = True
        else:
          member = False
        if self.dbase.CreateCard(barcode, member, value1):
          # Returns true if the card was not a duplicate and has been added!
          self.InfoDialog(u"Creditcard \"%s\" has been created.\nIt has \u20AC"
                          u"%.2f credit." % (barcode, value1), error=False)
          self.UpdateCancel_clicked_cb()
          logging.debug("UpdateDialog/card: barcode=%r, credit=%s, member=%s",
                        barcode, input2, value1)
        else:
          self.InfoDialog(u"Creditcard \"%s\" is allready in use.\nPlease use a"
                          u" different barcode!" % barcode, error=True)
    else:
      self.dbase.UpdateProduct(barcode, input2, value1, value2)
      logging.debug("UpdateDialog/prod: Product=%r, barcode=%r, memberprice=%s,"
                    " visitorprice=%s.", input2, value1, value2)
      self.UpdateCancel_clicked_cb()


if __name__ == '__main__':
  LOGFILE = os.path.expanduser("~/.frackbar/frackmin.log")
  LOGFORMAT = "%(asctime)-15s %(message)s"
  logging.basicConfig(filename=logfile, filemode='a', format=logformat,
                      level=logging.INFO)
  logging.info("Frackmin started!")
  FrackMin()
