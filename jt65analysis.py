# basic "stats analysis" of jt65 symbol sets/packets
# Copyright 2014 - Paul Drapeau and Brent Dukes

#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import sys
import glob
import copy
import argparse
import random
import math
import csv
import jt65stego
import jt65wrapy
import numpy as np
import matplotlib.pyplot as plt

distancedict = {}

def eq(a, b) :
#for map in checkpacket
  return (a == b)

def col(a, i):
    return [float(row[i]) for row in a]

def selecterrors(errors, a):
  rows = [] 
  for row in a :
    if int(row[0]) == errors :
      rows.append(row)
  return rows

def gridtolatlon(grid) :
#takes in a maidenhead grid and returns lat, lon
#https://en.wikipedia.org/wiki/Maidenhead_Locator_System

  lon = (ord(grid[0]) - ord('A')) * 20 - 180
  lat = (ord(grid[1]) - ord('A')) * 10 - 90
  lon += (ord(grid[2]) - ord('0')) * 2
  lat += (ord(grid[3]) - ord('0'))
  
# move to center of square
  lon += 1
  lat += 0.5
  
  return [lat, lon]
  
  
def distance_on_unit_sphere(lat1, long1, lat2, long2, unit=3960):
#http://www.johndcook.com/python_longitude_latitude.html
#The following code returns the distance between to locations based on each point's longitude and latitude. 
#The distance returned is relative to Earth's radius. To get the distance in miles, multiply by 3960. 
#To get the distance in kilometers, multiply by 6373.
# We default to miles...

    # Convert latitude and longitude to 
    # spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0
	
    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians
	
    # theta = longitude
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians
	
    # Compute spherical distance from spherical coordinates.
	
    # For two locations in spherical coordinates 
    # (1, theta, phi) and (1, theta, phi)
    # cosine( arc length ) = 
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length
    
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
           math.cos(phi1)*math.cos(phi2))
    arc = math.acos( cos )

    return arc * unit
  

def getgrid(string) :
#takes in a string. If the last 4 character make up valid grid it returns them
# if they aren't a valid grid returns False
  validletters=["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R"]
  
  splits = string.split()
  length = len(splits)
  
  last = splits[length-1]
  if len(last) != 4 :  # if it isn't 4 chars long it isn't a grid
    return False 
  elif last[0] not in validletters or last[1] not in validletters :
    return False  #doesn't start with two valid capital letters
  else :
    try :
      number = int(last[2:4])
      return last #it looks like a grid more or less at this point
    except :
      return False #can't convert to int
      
    

def checkpacket(packet, verbose=False) :
#packet is a two dimensional array of symbols and confidence
#returns diffs list of [diff position, packet symbol, clean encode symbol, confidence]
#if verbose prints <number of diffs>,<average confidence of diffs> to stdout
  symbols = packet[0]
  confidence = packet[1]
  
  symboltrydecode = copy.deepcopy(symbols)
  testdecode = jt65wrapy.unprepmsg(symboltrydecode)
  realmessage = jt65wrapy.prepmsg(testdecode)
  symbolmap = map(eq, realmessage, symbols)
  
  diffs = []
  for i in range(0,63) :
    if not symbolmap[i] :
      diffs.append([ i, symbols[i], realmessage[i], confidence[i] ])    
  if verbose :
    print diffs
    print realmessage
    print symbols

  return diffs
  
  
def output(diffs, packet, distances=False, distancegrid="", homelatlon=[]) :
# formated output for a packet and some diffs
# #diffs, totalconfidence, averageconfidence, mediaconfidence, stddevconfidence, averagedistance, s2db, freq, a1, a2, decode
    if distances and not getgrid(distancegrid) :
      print "you asked for distances and gave a bad or no grid... ERROR"
      return False
    elif distances and not homelatlon :
      homelatlon = gridtolatlon(distancegrid)

#SNR logic from jt65a.f90

    snr = 10.0* math.log10(float(packet[3])) - 32
    if snr > -1 :
      snr = -1
    elif snr < -30 :
      snr = -30
      
    conftotal = 0
    diffdist = 0
    grid = getgrid(packet[2])
    distance = 0
    
    if distances and grid:
      if grid in distancedict :
	distance = distancedict[grid]
      else:
        gridlatlon = gridtolatlon(grid)
        distance = distance_on_unit_sphere(gridlatlon[0], gridlatlon[1], homelatlon[0], homelatlon[1])
        distancedict[grid] = distance
        
    if diffs :
      for dif in diffs:
	conftotal += dif[3]
        diffdist += abs(dif[1]-dif[2])
      print str(len(diffs)) +  ", " + str(conftotal) + ", " + str( float(conftotal) / float(len(diffs))) + ", " + str(np.median(col(diffs,3)))  + ", " + str(np.std(col(diffs,3)))+  ", " + str(diffdist/len(diffs))   +  ", " + packet[3]  +  ", " + packet[4] +  ", " + packet[5] +  ", " + packet[6] + ", " + str(distance) + ", " + str(snr)  + ", " + packet[2] 
    else :
      print "0, 0, 0, 0, 0, 0, " + packet[3]  +  ", " + packet[4] +  ", " + packet[5] +  ", " + packet[6] + ", " + str(distance) + ", " + str(snr)  + ", " + packet[2]   

      
def processtextfile(filename, threshold=10) :
# process a textfile of output above and generate distance / snr / error stats
  rows = []
  f = open(filename, "rU")
  data = csv.reader((line.replace('\0','') for line in f), delimiter=",")
  for row in data :
    rows.append(row)
  errorcol = col(rows,0)
  snrcol = col(rows,11)

  print "Number of packets in file:			" + str(len(rows))
  print "\n"
  print "Median Number of Errors:			" + str(np.median(errorcol)) 
  print "Average Number of Errors:			" + str(np.average(errorcol))
  print "Standard Deviation of Errors:			" + str(np.std(errorcol))
  print "Error Bins:					\n" + str(np.bincount(errorcol, None, 63))
  print "\n"
  print "Median SNR:					" + str(np.median(snrcol)) 
  print "Average SNR:					" + str(np.average(snrcol))
  print "Standard Deviation SNR:				" + str(np.std(snrcol))
  
  errorplot = plt.figure()
  errorplot.suptitle('Error Histogram', fontsize=14, fontweight='bold')
  axerror = errorplot.add_subplot(111)
  numbins = max(errorcol)
  axerror.hist(errorcol,numbins,color='red',alpha=0.8)
  errorplot.show()
  
  inrangepackets = []
  for i in range(0, threshold + 1):
    setpackets = selecterrors(i, rows)
    inrangepackets +=  setpackets
    
  print "\n"
  print "Number of packets in set with " + str(threshold) +" or less errors: " + str(len(inrangepackets))
  
  distances = []
  for entry in col(inrangepackets,10) :
      if entry != 0 :
       distances.append(entry)
  print "	" + str(len(distances)) + " have distance data"
  if len(distances) != 0 :
    print "	Max Distance of Set:			" + str(np.amax(distances))
    print "	Median Distance of Set:			" + str(np.median(distances)) 
    print "	Average Distance of Set:		" + str(np.average(distances))
    print "	90% Distance of Set:			" + str(np.percentile(distances,90))

    distplot = plt.figure()
    distplot.suptitle('Distances for errors <= ' + str(threshold), fontsize=14, fontweight='bold')
    axdist = distplot.add_subplot(111)
    numbins = 10
    axdist.hist(distances,numbins,color='green',alpha=0.8)
    distplot.show()
   
  heatplot = plt.figure(facecolor='black')
  heatplot.suptitle('Errors / std(confidence) ', fontsize=14, fontweight='bold')
  axheat = heatplot.add_subplot(111)
  axheat.hexbin(errorcol,col(rows,4), bins='log', gridsize=200, cmap=plt.cm.bone)
  heatplot.show()
  
  heatplot2 = plt.figure()
  heatplot2.suptitle('Errors / avg(confidence) ', fontsize=14, fontweight='bold')
  axheat2 = heatplot2.add_subplot(111)
  axheat2.hexbin(errorcol,col(rows,2), bins='log', gridsize=200, cmap=plt.cm.bone)
  heatplot2.show()
  
  heatplot3 = plt.figure()
  heatplot3.suptitle('Errors / snr ', fontsize=14, fontweight='bold')
  axheat3 = heatplot3.add_subplot(111)
  axheat3.hexbin(errorcol,snrcol, bins='log', gridsize=200, cmap=plt.cm.bone)
  heatplot3.show()
  
def wavfileinput(filename, verbose=False, dodistance=False, homegrid="", homelatlon=[]):
# does the analysis for a wav file
# returns the packet array if you want it
    sys.stderr.write("processing: " + filename + "\n")
    packets = jt65wrapy.decodewav(filename)
    if verbose :  
      print packets
    
    for packet in packets :  
     diffs=checkpacket(packet, verbose)
     output(diffs,packet, dodistance, homegrid, homelatlon)
    
    return packets
 
def findpacketsbyerror(packets, verbose=False, errormax=6) :
#return all the packets and diffs with <= errormax errors
    
    returnpackets = []
    returndiffs = []
    for packet in packets :
      diffs = []
      diffs = checkpacket(packet, verbose)
      if len(diffs) <= errormax :
	returnpackets.append(packet)
	returndiffs += diffs
	
    return returnpackets, returndiffs       

def getgoodconfidence(packets, verbose=False) :
#takes in a list of packets
#returns a list of all the confidence values for correct symbols
  confidences = []
  for packet in packets :
    symbols = packet[0]
    confidence = packet[1]
  
    symboltrydecode = copy.deepcopy(symbols)
    testdecode = jt65wrapy.unprepmsg(symboltrydecode)
    realmessage = jt65wrapy.prepmsg(testdecode)
    symbolmap = map(eq, realmessage, symbols)
 
    for i in range(0,63) :
      if symbolmap[i] :
        confidences.append( confidence[i] )    

  return confidences
  
def spreadgoodconfidence(packet, confidences) :
#spread confidences in packet replacing exsiting (simulate on air reception)
  for i in range(0, 63) :
    packet[1][i] = random.choice(confidences)
  return packet

def simulateerrors(packet, diffs, numerrors, verbose=False) :
#simulate numerrors errors in the packet from the population of diffs
     usedpos = []
     for i in range(0, numerrors) :
       
       pos = random.randint(0,62)
       while pos in usedpos :
	 pos = random.randint(0,62)
       diff = random.choice(diffs)
       if verbose:
        print repr(diff) + " " + str(pos)
       packet[0][pos] = diff[1]
       packet[1][pos] = diff[3]
       
     return packet

def readsimwav(filename) :
#reads in a text file that simulates the output of ./jt65 to build an array of packets
	messages = []
	symbols = []
	confidence = []
	jt65msg = ""

	with open(filename, "r") as f:
		f.seek(0)	# Reset to start reading from beginning of file
		linecount = sum(1 for _ in f)	# Get linecount

		f.seek(0)	# Reset to start reading from beginning of file
                error = False 
		while linecount >= 3 and not error:		
			symbols = map(int, f.readline().strip().replace("  ", " ").replace("   ", " ").replace("\n", "").strip().split(" "))
			confidence = map(int, f.readline().strip().replace("   ", " ").replace("  ", " ").replace("\n", "").strip().split(" "))
			msgandstats = f.readline().strip().replace("\n", "").split(",")
			try :
			  jt65msg, s2db, freq, a1, a2 = msgandstats
			except :
			  error = True
			  jt65msg = "ERROR DECODE"
			  s2db = "1"
			  freq = "0"
			  a1 = "0"
			  a2 = "0"
			messages.append([symbols, confidence, jt65msg.strip(), s2db.strip(), freq.strip(), a1.strip(), a2.strip()])
			linecount = linecount - 3
	return messages





if __name__ == "__main__":
  
  parser = argparse.ArgumentParser(description='Packet Analysis tools for JT65 messages.', epilog="Transmitting hidden messages over amateur radio is prohibited by U.S. law.")
  
  groupSource = parser.add_argument_group("Source")
  groupCommands = parser.add_argument_group("Commands")
  groupOptions = parser.add_argument_group("Options")
  groupOptions.add_argument('--distance', metavar='<gridloc>', help='calc distance from grid')
  groupSource.add_argument('--file', metavar='<filename>', help='Read from and parse wav file')
  groupSource.add_argument('--dir', metavar='<dirname>', help='Read from and parse all wav files in a given path')
  groupSource.add_argument('--text', metavar='<textfile>', help='Read from and parse a text file for distance and snr stats')
  groupCommands.add_argument('--verbose', action='store_true', help='verbosity')
  
  args = parser.parse_args()
  
  verbose = False
  #add some validation
  if args.verbose :
    verbose = True
  homegrid = ""
  dodistance= False
  if args.distance :
    dodistance = True 
    homegrid = args.distance

#decode a wav file    
  if args.file : 
    wavfileinput(args.file, verbose, dodistance, homegrid) 
  
  if args.dir :
    wavlist = glob.glob(args.dir + "/*.wav")
    if dodistance :
      homelatlon = gridtolatlon(homegrid)
    if not wavlist :
      print "No .wav files found in : " + args.dir
      sys.exit(99)
    for wav in wavlist :
      wavfileinput(wav, verbose, dodistance, homegrid, homelatlon)
      
  
#decode a text file

  if args.text :
    processtextfile(args.text)
    raw_input("Press Enter to continue...")