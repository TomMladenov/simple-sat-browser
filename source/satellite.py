from skyfield.api import Topos, load, utc
from datetime import datetime
from datetime import timedelta
import pytz


class Satellite():

	id = 0		#NORAD ID
	name = 0	#name of the satellite
	type = 0	#name of TLE file where the satellite was generated from
	semi_major_axis = 0
	GM = 398600.4418

	#still todo: check if satellite.model parameters are time injection dependent
	#if NOT then just list them as variables here and init them in the init function
	#then we can query the variables without invoking a function


	def __init__(self, satellite, type):
		self.satellite = satellite
		self.id = self.satellite.model.satnum
		self.name = self.satellite.name
		self.type = type
		mean_motion = self.satellite.model.no / 60.0 						#radians per second
		self.semi_major_axis = (self.GM )**(1/3)/(mean_motion)**(2/3)


	def getSatInfo(self):
		return self.id, self.name, self.semi_major_axis, self.satellite.model.ecco, self.satellite.model.inclo, self.satellite.model.nodeo, self.satellite.model.argpo, self.satellite.model.mo;
		"""
		@return
		orbit semi major axis
		orbit eccentricity
		orbit inclination
		orbit right ascension
		orbit argument perigee
		orbit mean anomaly
		"""

	def getSkyPosition(self, lat, lon, ts, time):
		t = ts.utc(time)
		groundstation = Topos(lat, lon)
		difference = self.satellite - groundstation
		topocentric = difference.at(t)
		el, az, range = topocentric.altaz()
		return az, el, range;
		"""
		@return
		azimuth of satellite (Angle object)
		elevation of satellite (Angle object)
		range to the satellite (Distance object)
		"""


	def getGroundPosition(self, ts, time):
		t = ts.utc(time)
		geocentric = self.satellite.at(t)
		subpoint = geocentric.subpoint()
		latitude = subpoint.latitude
		longitude = subpoint.longitude
		elevation = subpoint.elevation
		return latitude, longitude, elevation;

		"""
		latitude of ground track (Angle object)
		longitude of ground track (Angle object)
		elevation of satellite above earth (Distance object)
		"""
