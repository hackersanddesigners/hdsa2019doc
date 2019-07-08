import os, random, pathlib, argparse, time
from moviepy.editor import *
from math import *
import time

start_time = time.time()
cwd =  pathlib.Path.cwd()
pathlib.Path( cwd / 'input' ).mkdir( parents=True, exist_ok=True )
src_path = cwd / 'input'
output_file_duration = 60
duration = 60
allowed = [ ".mov", ".mp4", ".m4v" ]
max_seg_length = 5 # max segment length
open_file = False
text_file = ''
clips = []
fonts = [ 'AlmendraB', 'AlmendraDisplay', 'AlmendraI', 'Amarante', 'KottaOne', 'KronaOne', 'LeagueGothic', 'LeagueSpartanB', 'Montaga', 'NadiaSerifNormal', 'TulpenOne', 'Voltaire', 'YatraOne' ]

def generate():
    print( "Creating movie of %s seconds. Max segment length: %s." % ( duration, max_seg_length ) )
    # load all the clips in the /input directory
    clips = getClips()
    # make random selection add filters and concat them
    concat = mainComp( clips )
    # if there is file with text snippets, overlay a random few of the snippets
    if text_file != '':
        txt = textOverlay()
        final = CompositeVideoClip( [concat] + txt )
    else:
        final = concat

    overlay = getOverlay( clips )
    final = CompositeVideoClip( [ final, overlay ] )

    timestr = time.strftime( "%Y-%m%d-%H%M%S" )
    filename = "output/hdsa%s.mp4" % timestr
    final.write_videofile( filename )
    if open_file:
        from subprocess import call
        call(["open", filename ])
    print ( "\a" )
    print("--- %s seconds ---" % (time.time() - start_time))

def getClips():
    clips = []
    for i, file in enumerate( sorted( src_path.glob( '*' ) ) ):
        filename, ext = os.path.splitext( file.name )
        if( ext in allowed ):
            print( "Input file: %s" % file )
            clip = VideoFileClip( str( file ) )
            clips.append( clip )
    # print (clips)
    # for property, value in vars(clips[0]).items():
    #     print (property, ": ", value)
    return clips

def mainComp( clips ):
    global duration
    edits = []
    while duration > 0:
        clip = random.choice ( clips )
        start = random.uniform( 0, int( clip.duration ) - 1)
        len = random.uniform( 1, min( max_seg_length, duration ) )
        if start + len > clip.duration: # length cant be longer then the time left in the clip
            len = int( clip.duration - start )
        duration -= len
        print( "Segment %s, length: %s, duration left: %s, clip duration: %s" % ( os.path.basename(clip.filename), len, duration, clip.duration ) )
        seg = clip.subclip( start, start + len )
        seg = seg.on_color( size=( 1920, 1080 ), color=( 0, 0, 0 ) )
        # newclip = ( seg.fx( vfx.colorx, 0.5 ) ) # darken
        seg = effectsGenerator( seg )
        edits.append( seg )
    return concatenate_videoclips( edits )

def getOverlay( clips ):
    rndClip = VideoFileClip( clips[ random.randint( 0, len( clips )-1 ) ].filename )
    l = random.randint( 2, 7 )
    s = random.randint( 0, ceil( output_file_duration ) - l )
    # color keying an overlay https://github.com/Zulko/moviepy/issues/389
    # layer2 = ( layer2.fx( vfx.mask_color, color=(133, 148, 155), thr=80, s=20 ) )
    return rndClip.subclip( 0, l ).resize( width=640 ).set_pos( ( 100, "center" )   ).set_start( s )

def textOverlay():
    global duration, output_file_duration, fonts
    edits = []
    try:
        with open( text_file, "r" ) as f:
            lines = f.read().splitlines()
            max = len( lines )
            pick = random.randint( 1, 5 )
            # picked = random.choices( lines, k = pick )
            picked = lines
            for line in picked:
                print( "- %s" % line.strip() )
                s = random.random() * ( output_file_duration - 3 )
                font = random.choice( fonts )
                txt_clip = TextClip( line, fontsize=70, color='white', font= font ).set_start( s ).set_duration( 3 ) # , font="Flightcase"
                txt_clip = txt_clip.set_position( randomPostion( txt_clip.size ) )
                edits.append( txt_clip )
                # txt_clip = txt_clip.set_pos( ( "center", "top" ) ).set_duration( 3 )
                # txt_clip2 = TextClip( "Summerschool 2019", fontsize=70, color='white', font="Chalkduster" )
                # txt_clip2 = txt_clip2.set_duration( 4 ).set_start( 3, True ).set_position( lambda t:( -150 + 500 * ( t - 1 ), "bottom" ) ) #.set_pos(("center","bottom"))
    except IOError:
         print ( "Error: Text input file does not appear to exist. Continuing." )
    return edits

def randomPostion( size ):
    return ( random.randint( 0, (1920 - size[ 0 ]) ), random.randint( 0, 1080 - size[ 1 ] ) )


def effectsGenerator( clip ):
    luckyNumber = random.randint( 0, 6 )
    # luckyNumber = 4
    effects = {
        0: effect_flicker,
        1: effect_saturate,
        2: effect_speed,
        3: effect_invert,
        4: effect_saturate2,
        # 4: effect_blink,
    }
    if( luckyNumber in effects ):
        print( "Apply effect %s" % effects[ luckyNumber ] )
        clip = effects[ luckyNumber ]( clip )
    return clip

def effect_flicker( clip ):
    return clip.fl_image( fuck_channels )

def effect_saturate( clip ):
    return clip.fx( vfx.colorx, factor=4 )

def effect_saturate2( clip ):
    return clip.fx( vfx.colorx, factor=2 )

def effect_speed( clip ):
    return clip.fx( vfx.time_symmetrize )

def effect_invert( clip ):
    return clip.fx( vfx.invert_colors   )

def effect_blink( clip ):
    #return clip.fx( vfx.blink, d_on = 0.1, d_off=0.1)
    # clip = clip.fl_time(lambda t: 1+sin(t))
    clip = clip.fl( blink_fx )
    return clip

import copy
import numpy as np

def blink_fx( get_frame, t ):
    """
    This function returns a 'region' of the current frame.
    The position of this region depends on the time.
    """
    print( "time %f" % t )
    frame = get_frame(t)
    newclip = copy.copy(frame)
    # import pdb; pdb.set_trace()
    # print( newclip )
    #black = np.tile(np.array([0,0,0]),(1080,1920))#np.full((1920, 1080), (0,0,0))
    # print( black )
    # print ( type(frame) )
    # d_on = 0.1
    # d_off = 0.1
    # D = d_on + d_off
    # if( (t % D) < d_on):
        # print( "")
        # newclip = black
    black = np.array([1920, 1080, 3])
    black.fill(0)

    d_on = 0.1
    d_off = 0.1
    D = d_on + d_off
    if( (t % D) < d_on):
        newclip = black
    return newclip

def invert_green_blue( image ):
    return image[:,:,[0,2,1]]

def fuck_channels( image ):
    r = random.randint( 0, 2 )
    if r == 0:
        return image[:,:,[2,0,1]]
    elif r == 1:
        return image[:,:,[1,2,0]]
    else:
        return image[:,:,[0,2,1]]


def main(argv):
    global duration, max_seg_length, output_file_duration, open_file, text_file
    parser = argparse.ArgumentParser(description='Generate H&D Book')
    parser.add_argument('-d','--duration', help='Duration of output file', default = 60 )
    parser.add_argument('-m','--max_seg_length', help='Max segment length', default = 15 )
    parser.add_argument('-o','--open', help='Open the output file on finish.', action='store_true' )
    parser.add_argument('-t','--textfile', help='Path to textfile. Overlay the video with lines from input text file.' )
    args = parser.parse_args()
    if args.duration:
        duration = float(args.duration)
        output_file_duration = duration
        print( "Duration: %s" % output_file_duration )
    if args.max_seg_length:
        max_seg_length = float(args.max_seg_length)
    if args.open:
        open_file = True
    if args.textfile:
        text_file = args.textfile
    generate()

if __name__ == "__main__":
   main( sys.argv[ 1: ] )
