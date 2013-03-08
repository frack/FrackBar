#!/usr/bin/python2.6
"""FrackBar GUI frontend on the FrackDb (Sales)."""
__author__ = "Rudi Daemen <info@kratjebierhosting.nl>"
__version__ = "1.2"

# Standard modules
import time
import os
import gtk
import frackdb
import frackmin
import threading
import logging

#Constants
CCPREFIX = 'FCC'
ANONMEMCARD = 'FRACKMEMBER'
NOTIFYTIME = 3

class KassaGui(object):
  """ Gui Handler class, this handles all GTK Gui I/O and buildup """
  def __init__(self):
    self.timer = None
    self.is_member = False
    self.prod_list = []
    self.cred_card = ''
    self.amount = 0
    self.cred_left = 0
    self.cred_id = ''
    self.dbase = frackdb.FrackDb()
    self.builder = gtk.Builder()
    self._StartGui()

  def _StartGui(self):
    verstring = "FrackBar Consumption Tracker GUI v%s" % __version__
    self.builder.add_from_file(os.path.join(
        os.path.dirname(__file__), 'frackbar.glade'))
    self.builder.connect_signals(self)
    self.builder.get_object('KassaGui').show()
    self.builder.get_object('KassaGui').set_title(verstring)
    self.builder.get_object('GuiMode').set_label("Payment in Cash")
    self.builder.get_object('GuiTotal').set_text(u"\u20AC%.2f" % self.amount)
    self.builder.get_object('GuiInvProd').get_buffer().set_text("Product:\n")
    self.builder.get_object('GuiInvPrice').get_buffer().set_text("Price:\n")
    self._Main()

  @staticmethod
  def _Main():
    try:
      gtk.gdk.threads_init()
      gtk.main()
    except Exception:
      logging.exception("Application crashed!")
      raise

  @staticmethod
  def _Exit(*_args):
    logging.info("Closing application.")
    raise SystemExit

  # InfoDialog to interact with the end-user in a more obvious way
  def InfoDialog(self, message, timeout=NOTIFYTIME, error=False):
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
    if self.timer:
      self.timer.cancel()
      self.timer = None
    self.timer = threading.Timer(timeout, self.DialogClose_clicked_cb)
    self.timer.start()
    time.sleep(.05)

  def DialogClose_clicked_cb(self, data=None):
    """ The very impatient persons can close the dialog by hand. This will also
    cancel the running close-dialog timer """
    try:
      self.timer.cancel()
      self.timer = None
    except AttributeError:
      logging.warning("CloseDialog timer was already stopped")
    self.builder.get_object('InfoDialog').hide()

  # Background method that updates the Invoice field based on Input changes
  def UpdateInvoice(self):
    """ This class updates the InVoice field. It redraws the field every time
    a change is made (e.g. new product, change from member to visitor, etc. """
    self.builder.get_object('GuiInvProd').get_buffer().set_text("Product:\n")
    self.builder.get_object('GuiInvPrice').get_buffer().set_text("Price:\n")
    self.amount = 0
    for items in self.prod_list:
      self.builder.get_object('GuiInvProd').get_buffer().insert_at_cursor(
          u"%s\n" % items[1])
      if self.is_member:
        self.builder.get_object('GuiInvPrice').get_buffer().insert_at_cursor(
          u"\u20AC%.2f\n" % items[2])
        self.amount = self.amount + items[2]
      else:
        self.builder.get_object('GuiInvPrice').get_buffer().insert_at_cursor(
          u"\u20AC%.2f\n" % items[3])
        self.amount = self.amount + items[3]
    if self.is_member:
      self.builder.get_object('GuiInvProd').get_buffer().insert_at_cursor(
          u"\nYou are a member.")
    self.builder.get_object('GuiTotal').set_text(u"\u20AC%.2f" % self.amount)
    self.builder.get_object('GuiInput').set_text("")

  def CashMode(self):
    """ Resets the interface to 'cash' mode """
    self.cred_left = 0
    self.is_member = False
    self.cred_id = ''
    self.cred_card = ''
    self.builder.get_object('GuiMode').set_label("Payment in Cash")

  def CardMode(self, barcode):
    """ Handles the creditcards """
    self.cred_card = barcode
    cardinfo = self.dbase.GetCard(self.cred_card)
    if cardinfo:
      self.cred_left = cardinfo['credit']
      self.is_member = cardinfo['member']
      self.cred_id = cardinfo['ID']
      self.InfoDialog(u"Your card \"%s\" has \u20AC%.2f credit left." % (
          self.cred_card, self.cred_left))
      self.builder.get_object('GuiMode').set_label(u"Creditcard: %s\t"
                   u"Credit: \u20AC%.2f" % (self.cred_card, self.cred_left))
    else:
      self.InfoDialog(u"Card \"%s\" is not a valid creditcard.\nPayment mode is"
                      u" set to cash." % barcode, error=True)
      self.CashMode()

  # Below all button/input field handling for the main GUI.
  def GuiInput_activate_cb(self, data=None):
    """ This handles the input text box. When a CR is received, the input is
    passed in the same was as in the old CLI version: The barcode is checked
    against the database and if it is a valid product it will be added to the
    list of products """
    barcode = data.get_text().decode('utf-8')
    logging.debug("Input received: %r", barcode)
    if barcode == '':
      self.InfoDialog(u"Please scan a barcode...", error=True)
      return
    if barcode.startswith(CCPREFIX):
      if barcode == CCPREFIX:
        self.CashMode()
        self.InfoDialog(u"Switching to cash mode as requested")
      else:
        self.CardMode(barcode)
    elif barcode == ANONMEMCARD:
      if self.cred_card:
        self.CashMode()
        self.InfoDialog(u"Switching back to cash mode as requested")
      if self.is_member:
        self.is_member = False
      else:
        self.is_member = True
    else:
      product = self.dbase.GetProduct(barcode)
      if product == None:
        self.InfoDialog("\"%s\" is not a valid barcode." % barcode, error=True)
      else:
        self.prod_list.append(product)
    self.UpdateInvoice()
    data.set_text("")


  def GuiReset_clicked_cb(self, data=None):
    """ Reset the application to startup values """
    self.CashMode()
    self.prod_list = []
    self.amount = 0
    self.builder.get_object('GuiInput').set_text("")
    self.builder.get_object('GuiInvProd').get_buffer().set_text("Product:\n")
    self.builder.get_object('GuiInvPrice').get_buffer().set_text("Price:\n")
    self.builder.get_object('GuiTotal').set_text(u"\u20AC%.2f" % self.amount)
    self.builder.get_object('GuiInput').set_sensitive(True)
    self.builder.get_object('GuiReset').set_sensitive(True)
    self.builder.get_object('GuiAccept').set_sensitive(True)
    self.builder.get_object('GuiInput').grab_focus()


  def GuiAccept_clicked_cb(self, data=None):
    """ This handles the accept button. If it is pressed, all products in the
    prod_list variable will then be added to the database. """
    if len(self.prod_list) == 0:
      self.InfoDialog("No items in invoice, nothing to do.\n\rResetting...")
      self.GuiReset_clicked_cb()
      return
    if self.cred_card:
      newcredit = self.cred_left - self.amount
      if newcredit < 0:
        self.InfoDialog(u"Not enough credit on the card.\r\nPlease use a "
                        u"different card.", error=True)
        return
      else:
        self.dbase.UpdateCard(self.cred_id, -self.amount)
        # Use -self.amount because you want to deduct this value from the
        # actual credit instead of add it. This function is used for both
        # topping up credit as well as deducting it!
    for items in self.prod_list:
      self.dbase.SetSale(items[0], self.cred_id, self.is_member)
    if self.cred_card:
      self.InfoDialog(u"Transaction completed.\r\nYour card %s has been charged"
                      u" \u20AC%.2f. \r\nYour card has \u20AC%.2f left." %
                      (self.cred_card, self.amount, newcredit),timeout=6)
    else:
      self.InfoDialog(u"Transaction completed.\r\nPlease deposit \u20AC%.2f in"
                       u" the cash box." % self.amount, timeout=6)
    self.builder.get_object('GuiMode').set_label(u"Thank you, come again!"
        u"\n\u00A9 Apu Nahasapeemapetilon")
    self.builder.get_object('GuiInvProd').get_buffer().insert_at_cursor(
        u"\nSuccess!\n\nApplication will\nreset in 3s.")
    self.builder.get_object('GuiAccept').set_sensitive(False)
    self.builder.get_object('GuiInput').set_sensitive(False)
    self.builder.get_object('GuiReset').set_sensitive(False)
    reset = threading.Timer(3, self.GuiReset_clicked_cb)
    reset.start()


  # Handling the items in the File and Help menu
  def StartAdmin_activate_cb(self, data=None):
    """ Start the FrackMin application and reset the KassaGui """
    frackmin.FrackMin()
    self.GuiReset_clicked_cb()

  def CreditTopup_activate_cb(self, data=None):
    """ This handles the credit TopUp dialog """
    dialog = self.builder.get_object('TopUpGui')
    dialog.connect('delete-event', dialog.hide_on_delete)
    dialog.show()
    self.builder.get_object('TopUpInfo').get_buffer().set_text(u"Please scan "
        "your creditcard...")
    self.builder.get_object('TopUpAmount').set_text(u"\u20AC0.00")
    self.GuiReset_clicked_cb() # Make sure all vars are reset!

  def About_activate_cb(self, data=None):
    """ Opens the About window """
    dialog = self.builder.get_object('GuiAbout')
    dialog.set_version("v%s" % __version__)
    dialog.connect('delete-event', dialog.hide_on_delete)
    dialog.show()
    dialog.run()
    dialog.hide()

  # All Input/Output methods for the Creditcard TopUp dialog.
  def TopUpInput_activate_cb(self, data=None):
    """ Reads the barcode that is scanned after the CR from the scanner """
    self.cred_card = self.builder.get_object('TopUpInput').get_text().decode(
        'utf-8')
    cardinfo = self.dbase.GetCard(self.cred_card)
    if cardinfo:
      self.cred_id = cardinfo['ID']
      self.cred_left = cardinfo['credit']
      self.builder.get_object('TopUpInfo').get_buffer().set_text(u"Card: %s\n"
          u"Credit: %.2f\n\nPlease click how much money you have deposited in "
          u"the cash box.\nClick Submit when you are done!"
          % (self.cred_card, self.cred_left))
    else:
      self.builder.get_object('TopUpInfo').get_buffer().set_text(
          u"Invalid or no card scanned! Please try again...\n")
      self.cred_card = ''
    self.builder.get_object('TopUpInput').set_text('')

  def TopUpAdd5_clicked_cb(self, data=None):
    """ The button to add 5 euro """
    if self.cred_card == '':
      self.builder.get_object('TopUpInfo').get_buffer().set_text(
          u"Please scan a card first!")
      return
    self.amount += 5
    self.builder.get_object('TopUpAmount').set_text(u"\u20AC%.2f" % self.amount)

  def TopUpAdd10_clicked_cb(self, data=None):
    """ The button to add 10 euro """
    if self.cred_card == '':
      self.builder.get_object('TopUpInfo').get_buffer().set_text(
          u"Please scan a card first!")
      return
    self.amount += 10
    self.builder.get_object('TopUpAmount').set_text(u"\u20AC%.2f" % self.amount)

  def TopUpAdd20_clicked_cb(self, data=None):
    """ The button to add 20 euro """
    if self.cred_card == '':
      self.builder.get_object('TopUpInfo').get_buffer().set_text(
          u"Please scan a card first!")
      return
    self.amount += 20
    self.builder.get_object('TopUpAmount').set_text(u"\u20AC%.2f" % self.amount)

  def TopUpAdd50_clicked_cb(self, data=None):
    """ The button to add 50 euro """
    if self.cred_card == '':
      self.builder.get_object('TopUpInfo').get_buffer().set_text(
          u"Please scan a card first!")
      return
    self.amount += 50
    self.builder.get_object('TopUpAmount').set_text(u"\u20AC%.2f" % self.amount)

  def TopUpOK_clicked_cb(self, data=None):
    """ The button commit the credit changes """
    if self.cred_card == '':
      self.builder.get_object('TopUpInfo').get_buffer().set_text(
          u"Please scan a card first!")
      return
    logging.debug("Card %r added %s credit.", self.cred_card, self.amount)
    self.builder.get_object('TopUpInfo').get_buffer().insert_at_cursor(
        u"\nAdding \u20AC%.2f to card %s...\n" % (self.amount, self.cred_card))
    self.dbase.UpdateCard(self.cred_id, self.amount)
    self.InfoDialog(u"Please make sure you have deposited \u20AC%.2f in the "
                    u"cash box!\r\nYour cards (%s) credit is now \u20AC%.2f." %
                    (self.amount, self.cred_card, self.cred_left + self.amount),
                    timeout=6)
    self.GuiReset_clicked_cb()
    self.builder.get_object('TopUpGui').hide()

  def TopUpCancel_clicked_cb(self, data=None):
    """ The button to cancel topping up credit """
    self.GuiReset_clicked_cb()
    self.builder.get_object('TopUpGui').hide()


def FrackBar():
  """ Launch the Bar Application! """
  while True:
    KassaGui()


if __name__ == '__main__':
  LOGFILE = os.path.expanduser("~/.frackbar/frackbar.log")
  LOGFORMAT = "%(asctime)-15s %(message)s"
  logging.basicConfig(filename=LOGFILE, filemode='a', format=LOGFORMAT, 
                      level=logging.INFO)
  logging.info("Application started!")
  FrackBar()
