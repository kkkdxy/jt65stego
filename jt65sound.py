import numpy as np
import pygame
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

def outputpygame(tones):
    
  size = (20, 20)

  bits = 16

  pygame.mixer.pre_init(44100, -bits, 1, 1024)
  pygame.init()
  _display_surf = pygame.display.set_mode(size, pygame.HWSURFACE | pygame.DOUBLEBUF)


  duration = .75    # in seconds

  for index in range(0,125):
    #freqency for the left speaker
    frequency_l = tones[index]
    #frequency for the right speaker
    frequency_r = 0

    #this sounds totally different coming out of a laptop versus coming out of headphones

    sample_rate = 44100
    n_samples = int(round(duration*sample_rate))
 #   n_samples = 4096
	#setup our numpy array to handle 16 bit ints, which is what we set our mixer to expect with "bits" up above
    buf = np.zeros(n_samples, dtype = np.int16)
    max_sample = 2**(bits - 1) - 1

    for s in range(n_samples):
	  t = float(s)/sample_rate    # time in seconds

	  #grab the x-coordinate of the sine wave at a given time, while constraining the sample to what our mixer is set to with "bits"
	  buf[s] = int(round(max_sample*math.sin(2*math.pi*frequency_l*t)))        # left
#	  buf[s][1] = int(round(max_sample*0.5*math.sin(2*math.pi*frequency_r*t)))    # right

	  sound = pygame.sndarray.make_sound(buf)
#play once, then loop forever
    sound.play(0, 329)


  pygame.quit()
 

def outputwavfile(filename, tones):
 

  data_size = 4096
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