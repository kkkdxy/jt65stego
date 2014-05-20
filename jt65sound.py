import numpy as np
import math
import wave
import sys
import struct

##some functions to calculate the tone values in hz for jt65 messages
## key function to call is tonewithsync it does all the work
## play these at  0.372 s each and you're done :)


def tone(number, m=1, offset=0):
##return a tone in HZ for the input number specified
#"Each channel symbol generates a tone at frequency 1270.5 + 2.6917 (N+2) m Hz, where N is
#the integral symbol value, 0 <=N <= 63, and m assumes the values 1, 2, and 4 for JT65 sub-
#modes A, B, and C."

	return offset + 1270.5 + (2.6917 * (number + 2 ) * m)

def tonepacket(message, m=1, offset=0):
#takes in a message array and returns an array of tones representing the jt65 audio tones in the message

	output = np.array(range(63),dtype=np.float)
	for x in range(0,63):
		output[x] = tone(message[x], m, offset)
	return output

def toneswithsync(message, m=1, offset=0):
## take in a jt65 packet and return a full set of tone values, ready to go with sync vector already calcualted in
# this is HZ ready to covert to audio and put out on the wire
#m is 1 2 or 4 for submodes a b and c
#offset is frequency offset
	output = np.array(range(125),dtype=np.float)
	synctone = 1270.5 + offset
	messagetones = tonepacket(message, m, offset)
	messageindex = 0
#the mystic 'pseudo-random sequence"
	syncvector = [1,0,0,1,1,0,0,0,1,1,1,1,1,1,0,1,0,1,0,0,0,1,0,1,1,0,0,1,0,0,0,1,1,1,0,0,1,1,1,1,0,1,1,0,1,1,1,1,0,0,0,1,1,0,1,0,1,0,1,1,0,0,1,1,0,1,0,1,0,1,0,0,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,1,1,0,1,0,0,1,0,1,1,0,1,0,1,0,1,0,0,1,1,0,0,1,0,0,1,0,0,0,0,1,1,1,1,1,1,1,1]
	for x in range(0,125):
		if syncvector[x] == 1:
			output[x] = synctone
		else:
			output[x] = messagetones[messageindex]
			messageindex += 1
	
	return output

 

def outputwavfile(filename, tones):
 

  data_size = 4096 #samples per jt65 symbol
  frate = 11025.0  # framerate as a float
  amp = 64000.0     # multiplier for amplitude


  wav_file = wave.open(filename, "w")

  nchannels = 1
  sampwidth = 2
  framerate = int(frate)
  nframes = data_size * 126
  comptype = "NONE"
  compname = "not compressed"

  wav_file.setparams((nchannels, sampwidth, framerate, nframes, comptype, compname))
  
  for index in range(0,125):
    sine_list_x = []
    for x in range(data_size):
      sine_list_x.append(math.sin(2*math.pi*tones[index]*(x/frate)))
    for s in sine_list_x:
    # write the audio frames to file
      wav_file.writeframes(struct.pack('h', int(s*amp/2)))

  wav_file.close()
  return filename