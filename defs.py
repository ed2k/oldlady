#! /usr/bin/env python

# Old Lady
# Copyright (C) 2007 Paul Kuliniewicz <paul@kuliniewicz.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02111-1301, USA.

VERSION = "0.2.0"
PACKAGE = "oldlady"
DATA_DIR = "/local/scratch/oldlady-0.1.0"
PKG_DATA_DIR = "/local/scratch/oldlady-0.1.0"
SWI_PROLOG = "/x3/pl-5.6.49/src/pl"
FL_DATA = "/x3/floater-imp/curdeck.tmp"

import os

ROOT_PATH = os.getcwd()
if ROOT_PATH[-len('oldlady'):] == 'oldlady':
    ROOT_PATH = os.path.abspath(os.path.join(os.getcwd(), '..'))
# 
DEAL_PATH = os.path.join(ROOT_PATH, "../deal319")
DDS_PATH = os.path.join(ROOT_PATH, "../ddsprogs")
testing = True
hands = [
['KQJ763', '95', 'AT92', '3'],
['T', 'J8642', 'K8', 'JT752'],
['A942', 'AQT7', 'J', 'AK96'],
['85', 'K3', 'Q76543', 'Q84'],
]
hands = ['J643.AT8.J4.KQJ3', 'AK8.J632.A5.A874', '5.K975.K8762.952', 'QT972.Q4.QT93.T6']
hands = ['AK.AQJT98.QJ95.2', 'T932.32.K2.T9843', 'Q65.754.AT.AKJ75', 'J874.K6.87643.Q6']
# test shortage
hands = ['A83.96.865.T87J6', 'T7.QJT3.JT3.9543', 'KJ9.7A84.Q94.AKQ', '64Q52.K52.K7A2.2']
# test balanced, semibalanced
hands = ['KT76.J6.AQ9T8.73', '5J4.KQT5.5.K8962', 'A3Q8.8A7.K43.AJ4', '29.9432.J762.QT5']
# test interference bidding
hands = ['K6T974.QJ6.T.952', 'QJ823.T54.894.J6', '.A92.KQ6725.Q743', 'A5.7K83.A3J.AKT8']
hands = ['AT7.JAQ3.T7.9742', 'J9532.4.KJ59.683', '8.K9652.Q846.JT5', 'KQ64.T87.3A2.AKQ']

hands = [x.split('.') for x in hands]