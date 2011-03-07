#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import pickle
from urllib import urlopen, urlencode
from telnetlib import Telnet

robonaut = Telnet('127.0.0.1', 12345)

picklefile = '/usr/share/irccat/.watches.pck'

def get_price(itemid):
  api_args = dict(
    callname = 'GetItemStatus',
    responseencoding = 'NV',
    appid = 'Tormente-ea98-4cb9-bfca-11339ff21b58',
    siteid = 3,
    version = 515,
    itemid = itemid,
  )

  url = 'http://open.api.ebay.com/shopping?%s' % urlencode(api_args)

  f = urlopen(url)
  d = f.readline()
  d = [x.split('=') for x in d.split('&')]
  d = dict(d)

  ccy   = d['Item(0).ConvertedCurrentPrice.CurrencyID']
  price = float(d['Item(0).ConvertedCurrentPrice.Value'])

  ccyfs = dict(
    GBP = '£%0.2f',
    USD = '$%0.2f',
  )

  try:
    ccyf = ccyfs[ccy]
  except KeyError:
    raise Exception('Unexpected currency %s' % ccy)

  if price is None:
    raise Exception('No price returned')

  return ccyf % price


def get_watches():
  f = open(picklefile, 'rb')
  watches = pickle.load(f)
  f.close()
  return watches

def save_watches(watches):
  f = open(picklefile, 'wb')
  pickle.dump(watches, f)
  f.close()


while True:
  try:
    watches = get_watches()

  except Exception, e:
    #import pdb;pdb.set_trace()
    print repr(e)
    time.sleep(1)
    continue

  for itemid, watch in watches.items():
    try:
      price = get_price(itemid)

    except Exception, e:
      #import pdb;pdb.set_trace()
      print repr(e)
      continue

    if 'oldprice' not in watch:
      n = watch['name'] or itemid
      robonaut.write('[EB] Current price of %s: %s\n' % (n, price))
        

    elif price != watch['oldprice']:
      robonaut.write('[EB] Alert! Price of %s now: %s\n' % (watch['name'], price))

    watch['oldprice'] = price

  try:
    save_watches(watches)
  except Exception, e:
    #import pdb;pdb.set_trace()
    robonaut.write('Could not save new prices')
    print repr(e)
    sys.exit(1)

  time.sleep(1)


