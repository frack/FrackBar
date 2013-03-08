#!/usr/bin/python2.6
"""FrackBar Database backend module."""
__author__ = "Rudi Daemen <info@kratjebierhosting.nl>"
__version__ = "1.0"

# Standard modules
import os
import sqlite
import datetime
import logging

class FrackDb(object):
  """ Class to handle all Database access for the application """
  def __init__(self, dbfile='frackbar.sqlite'):
    """ Initiate the DB Connection """
    dbdir = os.path.expanduser("~/.frackbar/")
    dbfile = os.path.join(dbdir, dbfile)
    if not os.path.isdir(dbdir):
      os.makedirs(dbdir)
    if not os.path.isfile(dbfile):
      self._CreateTable(dbfile)
    self.connection = sqlite.Connection(dbfile)

  @staticmethod
  def _CreateTable(db_file):
    """ Create the database if it does not exist """
    if not os.path.exists(db_file):
      logging.info("Database not found, creating it...")
      with sqlite.Connection(db_file) as cursor:
        cursor.executescript(file('frackbar.schema').read())
        cursor.executescript(file('frackbar.data').read())

  def GetProduct(self, barcode):
    """ method to get only the required product info from products """
    with self.connection as cursor:
      try:
        return cursor.execute("""select `ID`,`name`,`memberprice`,`visitorprice`
                          from `product`
                          where `barcode` = ? ORDER BY `ID` DESC LIMIT 1""",
                          (barcode,))[0]
      except IndexError:
#        logging.info("No products found matching barcode \'%s\'", barcode)
        return None

  def GetCard(self, barcode):
    """ method to get only the required creditcard info from creditcard """
    with self.connection as cursor:
      try:
        return cursor.execute("""select `ID`,`member`,`credit`
                          from `creditcard`
                          where `barcode` = ? ORDER BY `ID` DESC LIMIT 1""",
                          (barcode,))[0]
      except IndexError:
#        logging.info("No products found matching barcode \'%s\'", barcode)
        return None

  def GetSales(self, card, member):
    """ method to get the sum of all sales associated with creditcard the ID.
    This is based on whether the card is registered for a member or a
    visitor. It does a multi-table select and sums up the result.  """
    with self.connection as cursor:
      if member:
        try:
          return cursor.execute("""
              SELECT SUM(`product`.`memberprice`)
              FROM `product`
              JOIN `sales` ON `sales`.`product` = `product`.`ID`
              WHERE `sales`.`card` = ? """, (card,))[0]
        except IndexError:
          return None
      else:
        try:
          return cursor.execute("""
              SELECT SUM(`product`.`visitorprice`)
              FROM `product`
              JOIN `sales` ON `sales`.`product` = `product`.`ID`
              WHERE `sales`.`card` = ? """, (card,))[0]
        except IndexError:
          return None

  def SetSale(self, product, card=None, member=False):
    """ This method is the actual data writer. It by default asumes the sale
    was done by cash method and a non-member. Returns a string to indicate
    success or failure. """
    # Privacy protection, force set card to None to avoid being able to track
    # a members purchases. This is done as a precaution because the database
    # resides on a public computer and a creditcard can possibly be linked to
    # a real person (even though the cards do NOT use a (nick)name. Comment out
    # below line in case you want to start tracking creditcard sales.
    card = None
    with self.connection as cursor:
      cursor.execute("""
        insert into sales (`datetime`, `product`, `card`, `member`)
        values (?, ?, ?, ?)""",
        (datetime.datetime.now().strftime('%F %T'), product, card, member))

  def UpdateCard(self, cardid, amount):
    """ This method updates the given card with the amount. Please be aware that
    this requires the value to be in the correct form: Negative for decreasing
    the amount, positive for adding the amount! No Try/Except, we want it to
    break when this fails! A failure here means there is something really wrong
    between scanning the creditcard and updating the card! """
    with self.connection as cursor:
      credit = cursor.execute("""
        SELECT `credit`
        FROM `creditcard`
        WHERE `ID` = ?
        ORDER BY `ID` DESC LIMIT 1""", (cardid,))[0]['credit']
    credit = credit + amount
    with self.connection as cursor:
      cursor.execute("""
        UPDATE `creditcard`
        SET `credit` = ?
        WHERE `ID` = ? """, (credit, cardid))

  def ProdSales(self, date=''):
    """ This method gets all sales data for each product """
    date = date + '%'
    with self.connection as cursor:
      return cursor.execute("""
        SELECT
            `product`.`ID` AS ID,
            `product`.`name` AS ProdName,
            `product`.`memberprice` AS MemPrice,
            SUM(`sales`.`member` = '1') AS MemSales,
            `product`.`visitorprice` AS VisPrice,
            SUM(`sales`.`member` = '0') AS VisSales
        FROM `sales`
        JOIN `product` ON `sales`.`product` = `product`.`ID`
        WHERE `sales`.`datetime` LIKE ?
        GROUP BY product.ID""",
        (date, ))

  def GetCards(self):
    """ Simply returns all creditcards stored in the database """
    with self.connection as cursor:
      return cursor.execute('SELECT * FROM `creditcard`')

  def CreateCard(self, barcode, member, credit):
    """ Create a creditcard in the database. Returns false if card exists """
    with self.connection as cursor:
      if cursor.execute("""SELECT * FROM `creditcard` WHERE `barcode` = ?""",
                        (barcode, )):
        return False
    with self.connection as cursor:
      cursor.execute("""
        INSERT INTO `creditcard` (`datetime`, `barcode`, `member`, `credit`)
        VALUES (?, ?, ?, ?) """,
        (datetime.datetime.now().strftime('%F %T'), barcode, member, credit))
    return True

  def UpdateProduct(self, barcode, name, memberprice, visitorprice):
    """ This method 'updates' a product by adding it to the database as a new
    product. This is to avoid breaking the actual transactions with the old
    product pricing. This might cause a messy overview when products are updated
    very often. """
    with self.connection as cursor:
      cursor.execute("""
        INSERT INTO `product` (`barcode`, `name`, `memberprice`, `visitorprice`)
        VALUES (?, ?, ?, ?) """, (barcode, name, memberprice, visitorprice))
