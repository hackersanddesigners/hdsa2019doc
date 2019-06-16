# HDSA 2019 videodoc generator

## Description

This script takes all the videos in a specified folder and uses parts of these
videos to generate a random video of the specified length.

## Installation

Not necessary but preferred.
Create a environment for this project. I use conda:

``` bash
conda create -n hdsa19doc python=3.7.3
conda activate hdsa19doc
```

Then install moviePy

``` bash
pip install moviepy
```

Input videos go in /input. Allowed types: .mov, .m4v, .mp4
Run the script:

``` bash
python generate.py
```

<pre>
optional arguments:
  -h, --help            show this help message and exit
  -d DURATION, --duration DURATION
                        Duration of output file
  -m MAX_SEG_LENGTH, --max_seg_length MAX_SEG_LENGTH
                        Max segment length
</pre>

## Other references:

Other interesting video libraries/languages:

- https://lang.video/
- http://www.vapoursynth.com/
