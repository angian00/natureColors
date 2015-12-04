#!/usr/bin/env python

from subprocess import call
from PIL import Image
from operator import add


def extract_stills(video_file, frame_dir):
	output_file_path = still_dir + '/out.png'

	#ffmpeg -i input.flv -ss 00:00:14.435 -vframes 1 out.png
	#cmd = 'ffmpeg'
	cmd = 'echo'
	cmd_args = '-i ' + video_file + ' -ss 00:00:14.435 -vframes 1 ' + output_file_path

	call([cmd, cmd_args])


def compute_color(frame_dir):
	image_file_path = frame_dir + '/frame00_test.png'

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


def to_hexcode(rgb_vals):
	return '#%02x%02x%02x' % (rgb_vals[0], rgb_vals[1], rgb_vals[2])


def run():
	print '-- video processing started'
	input_file_path = 'videos/planet_earth/planet_earth_02.avi'
	#extract_stills(input_file_path, 'frames')

	print "avg color: ", to_hexcode(compute_color('frames'))

	print '-- video processing finished'


if __name__ == '__main__':
    run()
