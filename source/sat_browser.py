#!/usr/bin/env python
# coding: utf-8


import os
import sys
from PyQt5.QtCore import (QCoreApplication, QObject, QRunnable, QThread, QThreadPool, pyqtSignal)
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QListWidgetItem
from PyQt5.uic import loadUi
from PyQt5 import QtCore, QtGui, QtWidgets
import time
import datetime
import numpy as np
from satellite import Satellite
from skyfield.api import Topos, load, utc
import pytz


satellites = []

#We define the timescale
ts = load.timescale()

#We define the timezone
tz = 'Europe/Amsterdam'
timezone = pytz.timezone(tz)

#We define our location
lat = '50.0 N'
lon = '5.0 E'

#Let's load some tle files
for tleFile in os.listdir("./tle"):
	satSet = load.tle('tle/' + str(tleFile))
	for noradID in satSet:
		if isinstance(noradID, int):
			satellites.append(Satellite(satSet[noradID], str(tleFile).split('.')[0]))

print("Satellites loaded:  " + str(len(satellites)))

class Main(QMainWindow):

	def __init__(self, parent = None):
		super(Main, self).__init__(parent)
		loadUi('gui.ui', self)
		self.setWindowTitle('Simple Satellite Browser')

		for sat in satellites:
			QListWidgetItem(sat.name, self.listWidget)

		self.listWidget.itemSelectionChanged.connect(self.satSelect)

		self.satupdater = SatUpdater()
		self.satupdater.data.connect(self.update)
		self.satupdater.time.connect(self.ticktock)
		self.satupdater.start()

		self.lat_label.setText(lat)
		self.lon_label.setText(lon)
		self.tz_label.setText(tz)

	def update(self, data):
		self.az_label.setText(str(round(data[0].degrees,3)) + " °")
		self.el_label.setText(str(round(data[1].degrees, 3)) + " °")
		self.range_label.setText(str(int(data[2].km)) + " km")

	def ticktock(self, time):
		self.time_label.setText(time)

	def satSelect(self):
		index = self.listWidget.currentRow()
		self.satupdater.setSat(satellites[index])
		self.getSatInfo()

	def getSatInfo(self):
		satInfo = self.satupdater.getSatInfo()
		self.norad_label.setText(str(satInfo[0]))
		self.name_label.setText(str(satInfo[1]))
		self.sma_label.setText(str(int(satInfo[2])) + " km")
		self.ecc_label.setText(str(round(satInfo[3], 3)) + " rad")
		self.incl_label.setText(str(round(satInfo[4], 3)) + " rad")
		self.ma_label.setText(str(round(satInfo[7], 3)) + " rad")



class SatUpdater(QThread):

	"""
	This QThread has a satellite object as it's main instance and when started continuously
	calculates the position of our satellite
	"""

	active = False
	running = False
	sat = None

	data = pyqtSignal(object)
	time = pyqtSignal(str)

	def __init__(self, parent=None):
		QtCore.QThread.__init__(self, parent)
		self.active = True
		self.running = False

	def setSat(self, sat):
		self.sat = sat
		self.running = True

	def getSatInfo(self):
		return self.sat.getSatInfo();

	def run(self):
		while self.active:
			while self.running:
				t = datetime.datetime.now(timezone)
				self.data.emit(self.sat.getSkyPosition(lat, lon, ts, t))
				self.time.emit(str(t))
				time.sleep(0.1)


if __name__ == '__main__':
	a = QApplication(sys.argv)
	app = Main()
	app.show()
	a.exec_()
	os._exit(0)
