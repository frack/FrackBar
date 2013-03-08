#!/usr/bin/python2.6
"""SQLite connection object to return a list of dicts."""
__author__ = 'Elmer de looff <elmer@underdark.nl>'
__version__ = '0.1'

# Standard modules
import sqlite3


class ResultRow(object):
  """Ordered dictionary-like object for a single result row."""
  def __init__(self, headers, values):
    self.headers = headers
    self.values = values

  def __getitem__(self, index):
    """Returns a value either based on position or fieldname."""
    if type(index) == int:
      # `index` is an integer, return based on position
      return self.values[index]
    else:
      # `index` is a string (hopefully), return based on fieldname
      position = self.headers.index(index)
      return self.values[position]

  def __iter__(self):
    """Returns an iterator for the row's values."""
    return iter(self.values)

  def __repr__(self):
    """Returns a representation that looks like an ordered dictionary."""
    return '{%s}' % ', '.join('%r: %r' % item for item in self.items())

  def items(self):
    """Returns a list of 2-tuples (key, value), in original order."""
    return zip(self.headers, self.values)


class Connection(sqlite3.Connection):
  """SQLite connection object with modified return on execute()."""
  def execute(self, query, parameters=()):
    """Executes an SQLite query and returns a list of ordered dicts."""
    result = super(Connection, self).execute(query, parameters)
    if result.description:
      headers = [row[0] for row in result.description]
      return [ResultRow(headers, row) for row in result.fetchall()]

#    # Basic 'create empty list, iterate and append, return'
#    dict_result = []
#    for row in result.fetchall():
#      dict_result.append(ResultRow(headers, row))
#    return dict_result

#    # Single list comprehension
#    return [ResultRow(headers, row) for row in result.fetchall()]
