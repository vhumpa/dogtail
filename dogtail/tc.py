# -*- coding: <utf-8> -*-
"""Test Case magic

Author: Ed Rousseau <rousseau@redhat.com>"""
__author__ = "Ed Rousseau <rousseau@redhat.com>"

import string
import sys
import os
import re
import time
import datetime
import os.path
from config import config
from logging import LogWriter, TimeStamp
from errors import DependencyNotFoundError


class TC:
	"""
	The Test Case Superclass
	"""
	writer = LogWriter()
	def __init__(self):
		self.encoding = config.encoding
		# ascii + unicode. 8 bit extended char has been ripped out
		self.supportedtypes = ("ascii", "utf-8", "utf-16", "utf-16-be", "utf-16-le", "unicode-escape", "raw-unicode-escape",
		"big5", "gb18030", "eucJP", "eucKR", "shiftJIS")

	# String comparison function
	def compare(self, label, baseline, undertest, encoding=config.encoding):
		"""
		Compares 2 strings to see if they are the same. The user may specify
		the encoding to which the two strings are to be normalized for the
		comparison.  Default encoding is the default system encoding. Normalization to extended
		8 bit charactersets is not supported.
		"""
		self.label = label.strip()
		self.baseline = baseline
		self.undertest = undertest
		for string in [self.baseline, self.undertest]:
			try: string = unicode(string, 'utf-8')
			except TypeError: pass
		self.encoding = encoding

		# Normalize the encoding type for the comparaison based on self.encoding
		if self.encoding in self.supportedtypes:
			self.baseline = (self.baseline).encode(self.encoding)
			self.undertest = (self.undertest).encode(self.encoding)
			# Compare the strings
			if self.baseline == self.undertest:
				self.result = {self.label: "Passed"}
			else:
				self.result = {self.label: "Failed - " + self.encoding + " strings do not match. " + self.baseline + " expected: Got " + self.undertest}
			# Pass the test result to the LogWriter for writing
			TC.writer.writeResult(self.result)
			return self.result

		else:
			# We should probably raise an exception here
			self.result = {self.label: "ERROR - " + self.encoding + " is not a supported encoding type"}
			TC.writer.writeResult(self.result)
			return self.result
  

# String Test Case subclass
class TCString(TC):
	"""
	String Test Case Class
	"""
	def __init__(self):
		TC.__init__(self)

# Image test case subclass
class TCImage(TC):
	"""
	Image Test Case Class.
	"""
	IMVersion = ''
	
	def __init__(self):
		TC.__init__(self)
		self.supportedmetrics = ("MAE", "MSE", "PSE", "PSNR","RMSE", "none")
		self.scratchDir = config.scratchDir
		self.deldfile = 0

		# Get the ImageMagick version by parsing its '-version' output.
		IMVer = os.popen('compare -version').readline()
		IMVer = re.match('Version: ImageMagick ([0-9\.]+) .*', IMVer)
		if IMVer is not None: 
			IMVer = IMVer.groups()[0]
			TCImage.IMVersion = IMVer
		else:
			raise DependencyNotFoundError, "ImageMagick"

	# Use ImageMagick to compare 2 files
	def compare(self, label, baseline, undertest, dfile='default', metric='none', threshold=0.0):
		"""
		Calls ImageMagick's "compare" program. Default compares are based on
  	size but metric based comparisons are also supported with a threshold
  	determining pass/fail criteria.
		"""
		self.label = label.strip()
		self.baseline = baseline.strip()
		self.undertest = undertest.strip()
		self.difference = 0.0
		self.metric = metric.strip()
		self.threshold = threshold

		# Create a default filename and flag it for deletion
		if dfile == "default":
			x = TimeStamp()
			# Remove all whitespace from the label since IM chokes on it
			splabel = label.split(" ")
			label = "".join(splabel)
			self.dfile = self.scratchDir + x.fileStamp(label)
			self.deldfile = 1
		else: # or use the supplied one with no deletion
			self.dfile = dfile
			self.deldfile = 0

		# Check to see if the metric type is supported
		if self.metric in self.supportedmetrics:
			# This is a bit convoluted and will be until IM completes
			# implementation of command line chaining. This should be put into
			# a try also munge together our IM call chain, if we're not doing
			# numeric metrics
			if self.metric == "none":
				# Build the comparison string. Redirect STDERR to STDOUT;
				# IM writes to STDERR and cmd reads STDOUT
				cmd = ("compare " + self.baseline + " " + self.undertest + " " + self.dfile + " " + "2>&1")
				# os.popen returns a list; if it is empty then we have passed
				answer = os.popen(cmd).readlines()
				if answer == []:
					self.result = {self.label: "Passed - Images are the same size"}
				else:
					fanswer = answer[0].strip()
					self.result = {self.label: "Failed - " + fanswer}
				TC.writer.writeResult(self.result)
				return self.result
			else: # otherwise run the metric code
				# Build the cmd
				cmd = ("compare  -metric " + self.metric + " " + self.baseline + " " + self.undertest + " " + self.dfile + " " + "2>&1")
				answer = os.popen(cmd).readlines()

				# We need to check if the metric comparison failed. Unfortunately we
				# can only tell this by checking the length of the output of the 
				# command. More unfortunately, ImageMagic changed the length of the
				# output at version 6.2.4, so we have to work around that.
				metricFailed = True
				IMVersion = TCImage.IMVersion
				if IMVersion <= '6.2.3' and len(answer) == 1: metricFailed = False
				if IMVersion >= '6.2.4' and len(answer) != 1: metricFailed = False
				if metricFailed:
					fanswer = answer[0]
					self.result = {self.label: "Failed - " + fanswer}
				else: # grab the metric from answer and convert it to a number
					fanswer = answer[0].strip()
					fanswer = fanswer.split(" ")
					fanswer = fanswer[0]
					fanswer = float(fanswer)

					if fanswer == float("inf"): #same under PSNR returns inf dB:
						self.result = {self.label: "Passed - " + "compare results: " + str(fanswer) + " dB"}
					elif fanswer > self.threshold:
						excess = fanswer - self.threshold
						self.result = {self.label: "Failed - " + "compare result exceeds threshold by: " + str(excess) + " dB"}
					else:
						under = self.threshold - fanswer
						self.result = {self.label: "Passed - " + "compare results under threshold by: " + str(under) + " dB"}
				TC.writer.writeResult(self.result)
				return self.result

			# delete the composite image file if self.dfile is default
			if self.deldfile == 1:
				try:
					os.remove(self.dfile)
				except IOError:
					print "Could not delete tempfile " + self.dfile

		else: # unsupported metric given
			self.result = {self.label: "Failed - " + self.metric + " is not in the list of supported metrics"}
			TC.writer.writeResult(self.result)
			return self.result



class TCNumber(TC):
	"""
	Number Comparaison Test Case Class
	"""
	def __init__(self):
		TC.__init__(self)
		self.supportedtypes = ("int", "long", "float", "complex", "oct", "hex")

	# Compare 2 numbers by the type provided in the type arg
	def compare(self, label, baseline, undertest, type):
		"""
		Compares 2 numbers to see if they are the same. The user may specify
		how to normalize mixed type comparisons via the type argument.
		"""
		self.label = label.strip()
		self.baseline = baseline
		self.undertest = undertest
		self.type = type.strip()

		# If we get a valid type, convert to that type and compare
		if self.type in self.supportedtypes:
			# Normalize for comparison
			if self.type == "int":
				self.baseline = int(self.baseline)
				self.undertest = int(self.undertest)
			elif self.type == "long":
				self.baseline = long(self.baseline)
				self.undertest = long(self.undertest)
			elif self.type == "float":
				self.baseline = float(self.baseline)
				self.undertest = float(self.undertest)
			else:
				self.baseline = complex(self.baseline)
				self.undertest = complex(self.undertest)

			#compare 
			if self.baseline == self.undertest:
				self.result = {self.label: "Passed - numbers are the same"}
			else:
				self.result = {self.label: "Failed - " + str(self.baseline) + " expected: Got " + str(self.undertest)}
			TC.writer.writeResult(self.result)
			return self.result
		else:
			self.result = {self.label: "Failed - " + self.type + " is not in list of supported types"}
			TC.writer.writeResult(self.result)
			return self.result


if __name__ == '__main__':
	# import the test modules
	import codecs
	from utils import *

	# Set up vars to use to test TC class
	baseline = "test"
	undertest = "test"
	label = "unit test case 1.0"
	encoding = "utf-8"
	result = {}

	# Create the TC instance
	case1 = TC()

	# Fire off the compaison
	result = case1.compare(label, baseline, undertest, encoding)

	# Print the result - should be label - passed
	print(result)

	# Reset variables for failure path
	undertest = "testy"
	encoding = "utf-8"
	result = {}
	label = "unit test case 1.1"

	# Compare again
	result = case1.compare(label, baseline, undertest, encoding)

	# Print the result - should be label - failure
	print(result)

	# Create a TCString instance
	case2 = TCString()

	# Load our variables for this test
	label = " unit test case 2.0"
	encoding = "utf-8"
	baseline = u"groß"
	undertest = u"gro\xc3\xa1"
	result = {}

	# Fire off a UTF-8 compare
	result = case2.compare(label, baseline, undertest, encoding)

	# Print the result - should be label - passed
	print(result)

	# Fire the test for ASCII converted to UTF-8 testing
	label = " unit test case 2.1"
	encoding = "utf-8"
	baseline = "please work"
	undertest = "please work"
	result = {}

	result = case2.compare(label, baseline, undertest, encoding)

	# Print the result - should be label - passed
	print(result)

	# Reset variables for an out of range encoding type
	label = " unit test case 2.2"
	encoding = "swahilli"
	baseline = "please work"
	undertest = "please work"
	result = {}

	result = case2.compare(label, baseline, undertest, encoding)

	# Print the result - should be label - Error - not supported
	print(result)

	# Reset variables for unmatched utf-8 strings 
	label = " unit test case 2.3"
	encoding = "utf-8"
	baseline = u"groß"
	undertest = "nomatch"
	result = {}

#	result = case2.compare(label, baseline, undertest, encoding)

	# Print the result - should be label - failure
	print(result)

	# Reset variables for inherited TC base compare
	label = " unit test case 2.4"
	baseline = "This is inhereited"
	undertest = "This is inhereited"
	encoding = "utf-8"
	result = {}

	result = case2.compare(label, baseline, undertest, encoding)

	# Print the result - should be label - Passed
	print(result)


	# Include real CJKI (UTF-8) charcters for string compare
	# For this first test case, we are comparing same JA characters
	label = " unit test case 2.5"
	encoding = "utf-8"
	baseline = u"あか"
	undertest = u"あか"
	result = {}

	result = case2.compare(label, baseline, undertest, encoding)

	# Print the result - should be label - Passed
	print(result)


	# Testing different JA characters
	label = " unit test case 2.6"
	encoding = "utf-8"
	baseline = u"あか"
	undertest = u"元気"
	result = {}

	result = case2.compare(label, baseline, undertest, encoding)

	# Print the result - should be label - Failed
	print(result)



	# Test the timestamper class
	# Create a new timestamp instance
	# Print the file format time
	stamp1 = TimeStamp()
	presently = stamp1.fileStamp("filestamp")

	# Print - should be filenameYYYYMMDD with local systems date
	print presently

	# Make a stamp entry
	entry = stamp1.entryStamp()

	# Print the entrystamp - should be YYYY-MM-DD_HH:MM:SS with local system time
	print entry

	# Test to see that image compares work - this a simple compare with defaults
	# Load our variabes
	label = "unit test case 3.0"
	baseline = "../examples/data/GNOME-Street.png"
	undertest = "../examples/data/GNOME-Street1.png"
	result = {}

	# Create a TCImage instance
	case3 = TCImage()

	# Fire off the compare
	result = case3.compare(label, baseline, undertest)

	# Print the result Should be label - Passed - Images are same size
	print result

	# Default compare with different images (the sizes differ)
	label = "unit test case 3.1"
	baseline = "../examples/data/GNOME-Street.png"
	undertest = "../examples/data/g-star.png"
	result = {}

	# Fire off the compare
	result = case3.compare(label, baseline, undertest)

	# Print the result Should be label - Failied compare:Images differ in size
	print result

	# Image compare pass with the metrics option
	label = "unit test case 3.2"
	baseline = "../examples/data/GNOME-Street.png"
	undertest = "../examples/data/GNOME-Street1.png"
	result = {}
	metrics = ("MAE", "MSE", "PSE", "PSNR"," RMSE")

	for i in range(len(metrics)):
		result = case3.compare(label, baseline, undertest, metric=metrics[i])
		print metrics[i]
		print result

	# Image compare fail metrics
	label = "unit test case 3.3"
	baseline = "../examples/data/g-star.png"
	undertest = "../examples/data/g-star1.png"
	result = {}
	metrics = ("MAE", "MSE", "PSE", "PSNR"," RMSE")

	for i in range(len(metrics)):
		result = case3.compare(label, baseline, undertest, metric=metrics[i])
		print metrics[i]
		print result

	# Image comapre threshold metrics - only PNSR should pass
	label = "unit test case 3.4"
	baseline = "../examples/data/g-star.png"
	undertest = "../examples/data/g-star1.png"
	result = {}
	metrics = ("MAE", "MSE", "PSE", "PSNR"," RMSE")
	bound = 5

	for i in range(len(metrics)):
		result = case3.compare(label, baseline, undertest, metric=metrics[i], threshold=bound)
		print metrics[i]
		print result

	# Bogus metric test
	label = "unit test case 3.5"
	baseline = "../examples/data/g-star.png"
	undertest = "../examples/data/g-star1.png"
	result = {}
	metrics = "Guess"

	result = case3.compare(label, baseline, undertest, metric=metrics)

	# Should be failed - metric unsupported
	print result

	# Number comparison tests
	label = "unit test case 4.0"
	baseline = 42
	undertest = 42
	type = "int"
	result = {}

	# Make a TCNumber instance
	case4 = TCNumber()

	# Make a simple int compare
	result = case4.compare(label, baseline, undertest, type)

	# Should be Passed
	print result

	# Now make the int fail
	label = "unit test case 4.1"
	undertest = 999
	result = {}

	result = case4.compare(label, baseline, undertest, type)

	# Should fail
	print result

	# Now long pass
	label = "unit test case 4.2"
	baseline = 1112223334445556667778889990L
	undertest = 1112223334445556667778889990L
	type = "long"
	result = {}

	result = case4.compare(label, baseline, undertest, type)

	# Should pass
	print result

	# Float Pass
	label = "unit test case 4.3"
	baseline = 99.432670
	undertest = 99.432670
	type = "float"
	result = {}

	result = case4.compare(label, baseline, undertest, type)

	# Should pass
	print result

	# Complex pass
	label = "unit test case 4.4"
	baseline = 67+3j
	undertest = 67+3j
	type = "complex"
	result = {}

	result = case4.compare(label, baseline, undertest, type)

	# Should pass
	print result

	# Octal pass
	label = "unit test case 4.5"
	baseline = 0400
	undertest = 0400
	type = "oct"
	result = {}

	result = case4.compare(label, baseline, undertest, type)

	# Should pass
	print result

	# Hex pass
	label = "unit test case 4.6"
	baseline = 0x100
	undertest = 0x100
	type = "hex"
	result = {}

	result = case4.compare(label, baseline, undertest, type)

	# Should pass
	print result

	# Conversion pass - pass in equivalent hex and octal but compare as int
	label = "unit test case 4.7"
	baseline = 0x100
	undertest = 0400
	type = "int"
	result = {}

	result = case4.compare(label, baseline, undertest, type)

	# Should pass
	print result

	# Give a bogus type
	label = "unit test case 4.8"
	type = "face"
	result = {}

	result = case4.compare(label, baseline, undertest, type)

	# Should fail - unsupported type
	print result

