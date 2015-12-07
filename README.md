# natureColors
Simple video processing inspired by http://thecolorsofmotion.com/films.

Sample content: BBC "Planet Earth" documentaries. They should provide interesting color variations, with different seasons aand environments.

Tools: Python + (some Python libs) + libffmpeg.

Flowchart:
- (batch) Video file --> sampled stills --> avg color --> saved JSON data 
- (online)  HTML + CSS + JSON data --> Web visualization


## Environment setup
- install ffmpeg

- install Python
- install pip and virtualenv
- setup a Python virtualenv for your project
- install PIL (Python Image Library) in your virtualenv, excluding the pypi version:
`pip install --no-index -f http://dist.plone.org/thirdparty/ -U PIL`

- save (or symlink to) your video files in videos/ subdir
- launch `./process_video.py` and follow the instructions


