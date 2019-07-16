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
branding_file = '' # branding video overlay file
title_file = '' # title overlay file
logo_file = '' # corner logo overlay file
# make sure these fonts are loaded. See readme for instructions.
# fonts = [ 'AlmendraB', 'AlmendraDisplay', 'AlmendraI', 'Amarante', 'KottaOne', 'KronaOne', 'LeagueGothic', 'LeagueSpartanB', 'Montaga', 'NadiaSerifNormal', 'TulpenOne', 'Voltaire', 'YatraOne' ]
fonts = [ 'KronaOne' ]
output_size = ( 1920, 1080 )

# TODO:
# x multiple Overlays
# x outline around overlay
# x Pick one video from a folder with branding
# - speed up / optimize?
# - use screengrabbed video? What happens to the size?

def generate():
    print( "Creating movie of %s seconds. Max segment length: %s." % ( output_file_duration, max_seg_length ) )

    # getMaskFile( title_file )
    # return
    # load all the clips in the /input directory
    files = getVideoFiles( src_path )


    # make random selection add filters and concat them
    final = mainComp( files )

    # if there is file with text snippets, overlay a random few of the snippets
    if text_file != '':
        txt = textOverlay()
        final = CompositeVideoClip( [ final ] + txt )

    #branding
    final = branding( final )

    # Pick one random clip and overlay it PIP style somewhere sometime in the video
    final = getOverlays( files, final )
    # final = CompositeVideoClip( [ final, overlay ] )

    # add logo
    final = logo( final )

    # add effects to the whole shebang
    final = effectsGenerator( final, 2 )

    #title
    final = title( final )

    # write the video to file
    timestr = time.strftime( "%Y-%m%d-%H%M%S" )
    filename = "output/hdsa%s.mp4" % timestr
    final.write_videofile( filename, threads = 16 )
    # final.save_frame( "frame.png", t = 0.5 ) # saves the frame a t=2s
    if open_file:
        from subprocess import call
        call(["open", filename ])
    print ( "\a" )
    print("--- %s seconds ---" % (time.time() - start_time))

# Load all clips and store them in an array
def getVideoFiles( path ):
    files = []
    for i, file in enumerate( sorted( path.glob( '*' ) ) ):
        filename, ext = os.path.splitext( file.name )
        if( ext in allowed ):
            print( "Input file: %s" % file )
            files.append( file )
    return files

# The main edit sequence. Pick a bunch of random clips, pick a random segment of those clips,
# stick them together until we reach the desired duration. Apply effects to some of them.
def mainComp( files ):
    global duration_left
    edits = []
    while duration_left > 0:
        seg = randomEdit( files, duration_left )
        seg = effectsGenerator( seg )
        duration_left -= seg.duration
        print( "duration left: %s" % duration_left )
        edits.append( seg )
    return concatenate_videoclips( edits )

def branding( final_comp ):
    if branding_file == '':
        return final_comp
    print( "Branding loading from file \"%s\"" % branding_file  )
    files = [ branding_file ] # randomEdit needs an array
    seg = randomEdit( files, max_duration = 100 ) # high number, so max_seg_length gets used
    seg = seg.set_start( random.uniform( 0, output_file_duration - seg.duration ) )
    print( "Branding start: %f" % seg.start )
    final_comp = CompositeVideoClip( [ final_comp, seg ], size = output_size )
    return final_comp

def title( final_comp ):
    if title_file == '':
        return final_comp
    print( "Title loading from file \"%s\"" % title_file  )
    seg = VideoFileClip( title_file )
    mask_file = getMaskFile( title_file )
    if mask_file != None:
        print( "Using mask file: \"%s\"" % mask_file )
        maskclip = VideoFileClip( mask_file )
        maskclip = maskclip.to_mask()
        seg = seg.set_mask( maskclip )
    if( seg.duration > output_file_duration ):
        seg.set_duration( output_file_duration )
    end = seg.set_start( output_file_duration - seg.duration )
    begin = seg.copy()
    begin = begin.set_start( 0 )
    return CompositeVideoClip( [ final_comp, begin, end ], size = output_size )

def getMaskFile( file ):
    # check for mask. Expect title file with mask_ prefix with the same extension
    dir = os.path.dirname( file )
    base = os.path.basename( file )
    mask_file = pathlib.Path( dir + ( "/mask_" + base ) )
    if mask_file.is_file():
        return str( mask_file )
    else:
        return None

def logo( final_comp ):
    if logo_file == '':
        return final_comp
    logo = VideoFileClip( logo_file )
    logo = logo.fx( vfx.loop ).set_duration( output_file_duration ).set_position( ( 10, 10 ) )
    return CompositeVideoClip( [ final, logo ], size = output_size )


def randomEdit( files, max_duration ):
    # global duration_left
    clip = VideoFileClip( str( random.choice ( files ) ) )
    start = random.uniform( 0, int( clip.duration ) - 1)
    len = random.uniform( 1, min( max_seg_length, max_duration ) )
    if start + len > clip.duration: # length cant be longer then the time left in the clip
        len = int( clip.duration - start )
    print( "Segment \"%s\", start: %ss, length: %ss, clip duration: %ss" % ( os.path.basename(clip.filename), start, len, clip.duration ) )
    seg = clip.subclip( start, start + len )
    seg = seg.on_color( size=output_size, color=randomColor() )
    return seg

def getOverlays( files, mainClip ):
    numOverlays = random.randint( 1, 5 )
    picked = random.choices( files, k = numOverlays )
    for path in picked:
        rndClip = VideoFileClip( str( path ) )
        l = random.randint( 2, 7 )
        s = random.randint( 0, ceil( output_file_duration ) - l )
        # color keying an overlay https://github.com/Zulko/moviepy/issues/389
        # layer2 = ( layer2.fx( vfx.mask_color, color=(133, 148, 155), thr=80, s=20 ) )
        resized = rndClip.subclip( 0, l ).resize( width=640 )
        p = randomPosition( resized.size )
        resized = resized.set_pos( p ).set_start( s )
        clip_with_borders = resized.margin(top=20, bottom=20, left=20, right=20, color=randomColor() )
        mainClip = CompositeVideoClip( [ mainClip, clip_with_borders ] )
    return mainClip

def textOverlay():
    global duration_left, output_file_duration
    edits = []
    try:
        with open( text_file, "r" ) as f:
            lines = f.read().splitlines()
            max = len( lines )
            #pick = random.randint( 1, 5 )
            #picked = random.choices( lines, k = pick )
            for line in lines:
            # for line in picked:
                l = random.uniform( 3, 10 ) # duration to show the text
                s = random.random() * ( output_file_duration - l ) # start time
                font = random.choice( fonts ) # pick a font
                fontsize = 70 * random.randint(1,3)
                print( "- %s @%fs for %fs in font \"%s\" size %i" % ( line.strip(), s, l, font, fontsize ) )
                txt_clip = TextClip( line, fontsize=fontsize, font= font, color=randomTextColor() ).set_start( s ).set_duration( l ) # , font="Flightcase" #, color=randomColor()
                txt_clip = txt_clip.set_position( randomPosition( txt_clip.size ) )
                edits.append( txt_clip )
    except IOError:
         print ( "Error: Text input file does not appear to exist. Continuing." )
    return edits

def randomPosition( size ):
    rngx = output_size[ 0 ] - size[ 0 ]
    rngy = output_size[ 1 ] - size[ 1 ]
    return ( randomCoord( 0, rngx ), randomCoord( 0, rngy ) )

def randomCoord( v1, v2 ): #python wants the smallest number first in randint
    if( v1 > v2 ):
        return random.randint( v2, v1 )
    else:
        return random.randint( v1, v2 )

def randomColor():
    return ( random.randint( 0, 255 ), random.randint( 0, 255 ), random.randint( 0, 255 ) )

textColors = []
def randomTextColor():
    global textColors
    if len( textColors ) == 0:
        textColors = TextClip.list( 'color' )
    r = random.choice( textColors )
    return r

def effectsGenerator( clip, chance = 6 ):
    luckyNumber = random.randint( 0, chance ) # pick a random number
    # luckyNumber = 2
    effects = {
        0: effect_flicker,
        1: effect_saturate,
        2: effect_saturate2,
        3: effect_invert,
        4: effect_speed,
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
    return clip.fx( vfx.colorx, factor=3 )

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

def dumpObj( oj ):
    for property, value in vars(obj).items():
        print (property, ": ", value)

def main(argv):
    global duration_left, max_seg_length, output_file_duration, open_file, text_file, branding_file, title_file, logo_file
    parser = argparse.ArgumentParser(description='Generate H&D Documentation video')
    parser.add_argument('-d','--duration', help='Duration of output file', default = 60, type = float )
    parser.add_argument('-m','--max_seg_length', help='Max segment length', default = 15, type = float )
    parser.add_argument('-o','--open', help='Open the output file on finish.', action='store_true' )
    parser.add_argument('-t','--textfile', help='Path to textfile. Overlay the video with lines from input text file.' )
    parser.add_argument('-b','--branding', help='Path to video. A part of this video will be overlaid on the main composition.' )
    parser.add_argument('--title', help='Path to video/gif. Title overlay. If a file with the same name prefixed with mask_ is available it will be loaded as a mask' )
    parser.add_argument('--logo', help='Path to video/gif. Corner logo overlay.' )
    args = parser.parse_args()
    if args.duration:
        duration_left = args.duration
        output_file_duration = duration_left
        print( "Duration: %s" % output_file_duration )
    if args.max_seg_length:
        max_seg_length = float(args.max_seg_length)
    if args.open:
        open_file = True
    if args.textfile:
        text_file = args.textfile
    if args.branding:
        branding_file = args.branding
    if args.title:
        title_file = args.title
    if args.logo:
        title_file = args.logo
    generate()

if __name__ == "__main__":
   main( sys.argv[ 1: ] )
