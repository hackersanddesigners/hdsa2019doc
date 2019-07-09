import os, random, pathlib, argparse, time
from moviepy.editor import *
from math import *
import time

start_time = time.time()
cwd =  pathlib.Path.cwd()
pathlib.Path( cwd / 'input' ).mkdir( parents=True, exist_ok=True )
src_path = cwd / 'input'
output_file_duration = 60 # specified length of the video
duration_left = 60 # time left in video
allowed = [ ".mov", ".mp4", ".m4v" ] # allowed file extensions in input folder
max_seg_length = 5 # max segment length
open_file = False # if true (settable via commandline) the output file will open in the os default application
text_file = '' # input text file path
# make sure these fonts are loaded. See readme for instructions.
fonts = [ 'AlmendraB', 'AlmendraDisplay', 'AlmendraI', 'Amarante', 'KottaOne', 'KronaOne', 'LeagueGothic', 'LeagueSpartanB', 'Montaga', 'NadiaSerifNormal', 'TulpenOne', 'Voltaire', 'YatraOne' ]

def generate():
    print( "Creating movie of %s seconds. Max segment length: %s." % ( output_file_duration, max_seg_length ) )
    # load all the clips in the /input directory
    files = getVideoFiles()

    # make random selection add filters and concat them
    concat = mainComp( files )
    # if there is file with text snippets, overlay a random few of the snippets
    if text_file != '':
        txt = textOverlay()
        final = CompositeVideoClip( [concat] + txt )
    else:
        final = concat

    # Pick one random clip and overlay it PIP style somewhere sometime in the video
    overlay = getOverlay( files )
    final = CompositeVideoClip( [ final, overlay ] )

    # write the video to file
    timestr = time.strftime( "%Y-%m%d-%H%M%S" )
    filename = "output/hdsa%s.mp4" % timestr
    final.write_videofile( filename )
    if open_file:
        from subprocess import call
        call(["open", filename ])
    print ( "\a" )
    print("--- %s seconds ---" % (time.time() - start_time))

# Load all clips and store them in an array
def getVideoFiles():
    files = []
    for i, file in enumerate( sorted( src_path.glob( '*' ) ) ):
        filename, ext = os.path.splitext( file.name )
        if( ext in allowed ):
            print( "Input file: %s" % file )
            files.append( file )
            # clip = VideoFileClip( str( file ) )
            # clips.append( clip )
    # print (clips)
    # for property, value in vars(clips[0]).items():
    #     print (property, ": ", value)
    return files

# The real work. Pick a bunch of random clips, stick them together until we reach
# the desired duration. Apply effects to some of them.
def mainComp( files ):
    global duration_left
    edits = []
    while duration_left > 0:
        clip = VideoFileClip( str( random.choice ( files ) ) )
        start = random.uniform( 0, int( clip.duration ) - 1)
        len = random.uniform( 1, min( max_seg_length, duration_left ) )
        if start + len > clip.duration: # length cant be longer then the time left in the clip
            len = int( clip.duration - start )
        duration_left -= len
        print( "Segment %s, length: %s, duration left: %s, clip duration: %s" % ( os.path.basename(clip.filename), len, duration_left, clip.duration ) )
        seg = clip.subclip( start, start + len )
        seg = seg.on_color( size=( 1920, 1080 ), color=( 0, 0, 0 ) )
        seg = effectsGenerator( seg )
        edits.append( seg )
    return concatenate_videoclips( edits )

def getOverlay( files ):
    file = files[ random.randint( 0, len( files )-1 ) ]
    rndClip = VideoFileClip( str( file ) )
    l = random.randint( 2, 7 )
    s = random.randint( 0, ceil( output_file_duration ) - l )
    # color keying an overlay https://github.com/Zulko/moviepy/issues/389
    # layer2 = ( layer2.fx( vfx.mask_color, color=(133, 148, 155), thr=80, s=20 ) )
    return rndClip.subclip( 0, l ).resize( width=640 ).set_pos( ( 100, "center" )   ).set_start( s )

def textOverlay():
    global duration_left, output_file_duration
    edits = []
    try:
        with open( text_file, "r" ) as f:
            lines = f.read().splitlines()
            max = len( lines )
            pick = random.randint( 1, 5 )
            picked = random.choices( lines, k = pick )
            # picked = lines
            for line in picked:
                print( "- %s" % line.strip() )
                l = random.uniform( 3, 10 ) # duration to show the text
                s = random.random() * ( output_file_duration - l ) # start time
                font = random.choice( fonts ) # pick a font
                txt_clip = TextClip( line, fontsize=70, color='white', font= font ).set_start( s ).set_duration( l ) # , font="Flightcase"
                txt_clip = txt_clip.set_position( randomPostion( txt_clip.size ) )
                edits.append( txt_clip )
    except IOError:
         print ( "Error: Text input file does not appear to exist. Continuing." )
    return edits

def randomPostion( size ):
    return ( random.randint( 0, (1920 - size[ 0 ]) ), random.randint( 0, 1080 - size[ 1 ] ) )

def effectsGenerator( clip ):
    luckyNumber = random.randint( 0, 6 ) # pick a random number
    # luckyNumber = 2
    effects = {
        0: effect_flicker,
        1: effect_saturate,
        2: effect_speed,
        3: effect_invert,
        4: effect_saturate2,
        # 4: effect_blink,
    }
    if( luckyNumber in effects ): # if the lucky number has an effect, apply it.
        print( "Apply effect %s" % effects[ luckyNumber ] )
        clip = effects[ luckyNumber ]( clip )
    return clip

def effect_flicker( clip ):
    # clip = ( clip.fx( vfx.colorx, 0.5 ) ) # darken
    return clip.fl_image( fuck_channels )

def effect_saturate( clip ):
    return clip.fx( vfx.colorx, factor=4 )

def effect_saturate2( clip ):
    return clip.fx( vfx.colorx, factor=2 )

def effect_speed( clip ):
    return clip.fx( vfx.time_symmetrize ).fx( vfx.speedx, factor = 2 )

def effect_invert( clip ):
    return clip.fx( vfx.invert_colors   )

def invert_green_blue( image ):
    return image[:,:,[0,2,1]]

def fuck_channels( image ):
    r = random.randint( 0, 2 ) # change channel order for each frame
    if r == 0:
        return image[:,:,[2,0,1]]
    elif r == 1:
        return image[:,:,[1,2,0]]
    else:
        return image[:,:,[0,2,1]]

def main(argv):
    global duration_left, max_seg_length, output_file_duration, open_file, text_file
    parser = argparse.ArgumentParser(description='Generate H&D Book')
    parser.add_argument('-d','--duration', help='Duration of output file', default = 60 )
    parser.add_argument('-m','--max_seg_length', help='Max segment length', default = 15 )
    parser.add_argument('-o','--open', help='Open the output file on finish.', action='store_true' )
    parser.add_argument('-t','--textfile', help='Path to textfile. Overlay the video with lines from input text file.' )
    args = parser.parse_args()
    if args.duration:
        duration_left = float(args.duration)
        output_file_duration = duration_left
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
