#!/usr/bin/env python

import sys
import logging
import os
from os.path import *
import glob
from subprocess import call

from PIL import Image
from operator import add


#### processing parameters
n_frames = 10 #number of frames extracted per video file
start_skip_interval = 2*60 #safeguard against start credits, in seconds
end_skip_interval = 5*60 #safeguard against end credits, in seconds
####

videos_dir = 'videos'
frames_dir = 'frames'

cmd_help = 'help'
cmd_clean = 'clean'
cmd_scan = 'scan'
cmd_extract = 'extract'
cmd_color = 'colors'


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s', datefmt='%I:%M:%S')
logger = logging.getLogger('process_video')

def run():
	if len(sys.argv) < 2:
		cmd = 'help'
	else:
		cmd = sys.argv[1]

	#change to the script's dir
	os.chdir(dirname(realpath(__file__)))

	if cmd == cmd_help:
		help()
	
	elif cmd == cmd_clean:
		clean()
	
	elif cmd == cmd_scan:
		scan()
	
	elif cmd == cmd_extract:
		if len(sys.argv) < 3:
			print '!! Missing argument'
			help()
		else:
			video_file = sys.argv[2]
			extract(video_file)
	
	elif cmd == cmd_color:
		if len(sys.argv) < 3:
			print '!! Missing argument'
			help()
		else:
			video_file = sys.argv[2]
			compute_colors(get_video_name(video_file))
	
	else:
		print '!! Unknown command: ' + cmd
		help()


def help():
	print
	print 'Usage instructions: '
	print '\t' + sys.argv[0] + ' <cmd> [cmd_args]'
	print 'Available commands: '
	print '\t' + cmd_help + '\t Produces this help message'
	print '\t' + cmd_scan + '\t Scan [' + videos_dir + '] dir and process any videos found, as per ' + cmd_extract + ' command'
	print '\t' + cmd_extract + ' <video_file>\t Extract frames from <video_file>'
	print '\t' + cmd_color + ' <video_file>\t Compute color from frames extracted from <video_file>'
	print '\t' + cmd_clean + '\t Remove all byproducts'
	print


def clean():
	print('TODO: clean')

def scan():
	logger.info('Scanning video dir [' + videos_dir +']')
	for f in os.listdir(videos_dir):
		full_file_path = join(videos_dir, f)
		if isfile(full_file_path):
			logger.debug('Found file: ' + full_file_path)
			extract_frames(full_file_path)




def extract_frames(video_file_path):
	#video_file_path = 'videos/planet_earth/planet_earth_02.avi'

	video_name = get_video_name(video_file_path)
	logger.info('Extracting frames from video [' + video_name +']')

	output_file_path = get_frame_file_pattern(video_name, forFFMpeg=True)

	#TODO: get video duration (and metadata?)
	duration = 40*60*60
	interval = duration / n_frames

	#TODO: apply skip intervals

	#ffmpeg -i input.flv -ss 00:00:14.435 -vframes 1 out.png
	#cmd = 'echo ffmpeg'
	#shell_line = 'echo ffmpeg -i ' + video_file_path + ' -ss 00:00:14.435 -vframes 1 ' + output_file_path
	shell_line = 'echo ffmpeg -i ' + video_file_path + ' -vf fps=1/' + interval + ' ' + output_file_path
	
	call(shell_line, shell=True)


def compute_colors(video_file_path):
	video_name = get_video_name(video_file_path)
	logger.info('Computing frame colors for video [' + video_name +']')

	#iterate over frame dir
	frame_list = glob.glob(get_frame_file_pattern(video_name))
	frame_list.sort()

	for fr in frame_list:
		logger.debug('Processing frame: ' + basename(fr))
		hex_color = to_hexcode(compute_color(fr))
		logger.debug("avg color: " + hex_color)

	#TODO: save color data as text file

	#TODO: save colorband image



def compute_color(image_file_path):
	#load image from file
	im = Image.open(image_file_path)
	#convert to RGB data format (in case it's indexed palette or something)
	im = im.convert('RGB')

	#process pixel data
	pixels = im.load()
	w, h = im.size

	cum_rgb_values = [0, 0, 0]
	for x in range(w):
	    for y in range(h):
			cpixel = pixels[x, y]
			#element by element sum
			cum_rgb_values = map(add, cum_rgb_values, cpixel)


	return [ x/(w*h) for x in cum_rgb_values ]



def get_video_name(video_file_path):
	#remove dir path
	just_filename = basename(video_file_path)
	#remove extension
	return just_filename.split('.')[0]


def get_frame_file_pattern(video_name, forFFMpeg=False):
	frame_pattern = join(frames_dir, video_name, 'frame_')
	if forFFMpeg:
		frame_pattern = frame_pattern + '%03d.png'
	else:
		frame_pattern = frame_pattern + '*.png'
	
	return frame_pattern


def to_hexcode(rgb_vals):
	return '#%02x%02x%02x' % (rgb_vals[0], rgb_vals[1], rgb_vals[2])



if __name__ == '__main__':
    run()
