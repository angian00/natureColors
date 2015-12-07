#!/usr/bin/env python

import sys
import logging
import os
from os.path import *
import glob
import subprocess
import re

from PIL import Image
from operator import add


#### processing parameters
n_frames = 10 #number of frames extracted per video file
start_skip_interval = 30 #safeguard against start credits, in seconds
end_skip_interval = 5 #safeguard against end credits, in seconds

#geometry of the colorband image, in pixels
colorband_width = 800
colorband_height = 40
n_colorbands = n_frames
####

videos_dir = 'videos'
frames_dir = 'frames'
colors_dir = 'colors'

cmd_help = 'help'
cmd_clean = 'clean'
cmd_scan = 'scan'
cmd_extract = 'extract'
cmd_color = 'colors'
cmd_save_image = 'image'


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
			extract_frames(video_file)
	
	elif cmd == cmd_color:
		if len(sys.argv) < 3:
			print '!! Missing argument'
			help()
		else:
			video_file = sys.argv[2]
			compute_colors(get_video_name(video_file))
	
	elif cmd == cmd_save_image:
		if len(sys.argv) < 3:
			print '!! Missing argument'
			help()
		else:
			video_file = sys.argv[2]
			save_color_image(get_video_name(video_file))

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
	print '\t' + cmd_save_image + ' <video_file>\t Compute color band image for <video_file>'
	print '\t' + cmd_clean + '\t Remove all byproducts'
	print


def clean():
	print('TODO: clean')


def scan():
	logger.info('Scanning video dir [' + videos_dir +']')
	for f in os.listdir(videos_dir):
		full_file_path = join(videos_dir, f)
		if isfile(full_file_path) and not full_file_path.endswith('.txt'):
			logger.debug('Found file: ' + full_file_path)
			extract_frames(full_file_path)

def extract_frames(video_file_path):
	#video_file_path = 'videos/planet_earth/planet_earth_02.avi'

	video_name = get_video_name(video_file_path)
	logger.info('Extracting frames from video [' + video_name +']')

	output_file_path = get_frame_file_pattern(video_name, forFFMpeg=True)

	#TODO: get metadata?

	raw_duration = get_video_duration(video_file_path)
	interval = (raw_duration - start_skip_interval - end_skip_interval) / n_frames
	logger.debug('n_frames: {}, raw duration: {} secs, interval: {} secs'.format(n_frames, raw_duration, interval))

	frame_dir = join(frames_dir, video_name)
	if not os.path.exists(frame_dir):
		logger.debug('Creating dir ' + frame_dir)
		os.makedirs(frame_dir)

	shell_line = 'ffmpeg -itsoffset -{} -i {} -frames {} -vf fps=1/{} {}'.format(start_skip_interval, video_file_path, n_frames+1, interval, output_file_path)
	call_with_output(shell_line)



def compute_colors(video_name):
	logger.info('Computing frame colors for video [' + video_name +']')

	#iterate over frame dir
	frame_list = glob.glob(get_frame_file_pattern(video_name))
	frame_list.sort()

	hexcode_file_path = join(colors_dir, 'hexcolors_' + video_name + '.txt')
	with open(hexcode_file_path, 'w') as f:
		for fr in frame_list:
			logger.debug('Processing frame: ' + basename(fr))
			hex_color = to_hexcode(compute_color(fr))
			logger.debug("avg color: " + hex_color)
			f.write(hex_color)
			f.write('\n')

	logger.debug('Written hex color file: ' + hexcode_file_path)


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


def save_color_image(video_name):
	output_file_path =join(colors_dir, video_name + '.png')
	img = Image.new( 'RGB', (colorband_width, colorband_height*n_colorbands), "black")
	pixels = img.load()

	hexcode_file_path = join(colors_dir, 'hexcolors_' + video_name + '.txt')
	with open(hexcode_file_path, 'r') as hf:
		i_band = 0
		for hexcode in hf:
			band_color = to_rgb(hexcode)
			logger.debug('Read color: {}'.format(band_color))
			for x in range(colorband_width):
				for y in range(colorband_height):
					pixels[x, y + i_band*colorband_height] = band_color

			i_band = i_band + 1

	img.save(output_file_path)
	logger.debug('Saved colorband image: ' + output_file_path)



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


def get_video_duration(video_file_path):
	shell_line = 'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 ' + video_file_path
	#call(shell_line, shell=True)
	shell_output, shell_error = subprocess.Popen(shell_line.split(' '), stdout = subprocess.PIPE, stderr= subprocess.PIPE).communicate()
	return float(shell_output)


def call_with_output(cmd_line):
	i_frame_pattern = re.compile('.*frame=\s*(\d+)')
	ts_pattern = re.compile('.*time=(\S+)')

	child = subprocess.Popen(cmd_line, shell=True, stderr=subprocess.PIPE)
	curr_line = ''
	curr_frame = -1
	while True:
		out_char = child.stderr.read(1)
		if out_char == '' and child.poll() != None:
			break
		if out_char != '':
			#sys.stdout.write(out)
			#sys.stdout.flush()
			curr_line = curr_line + out_char
			if out_char == '\r':
				if curr_line.startswith('frame='):
					#parse line with format [frame=    <i> fps=....]
					i_frame = int(i_frame_pattern.match(curr_line).group(1))
					ts = ts_pattern.match(curr_line).group(1)
					if i_frame != curr_frame:
						logger.debug('Extracting frame: {}, ts={}'.format(i_frame, ts))
						curr_frame = i_frame

				curr_line = ''


def to_hexcode(rgb_vals):
	return '#%02x%02x%02x' % (rgb_vals[0], rgb_vals[1], rgb_vals[2])

def to_rgb(hexcode):
	return (int(hexcode[1:3], 16), int(hexcode[3:5], 16), int(hexcode[5:7], 16))



if __name__ == '__main__':
	run()
