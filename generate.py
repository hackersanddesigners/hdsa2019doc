import os, random, pathlib, argparse, time
from moviepy.editor import *

cwd =  pathlib.Path.cwd()
pathlib.Path( cwd / 'input' ).mkdir( parents=True, exist_ok=True )
src_path = cwd / 'input'
duration = 60
allowed = [ ".mov", ".mp4", ".m4v" ]
clips = []
edits = []

max_seg_length = 5 # max segment length

def invert_green_blue(image):
    return image[:,:,[0,2,1]]

def generate():
    global duration
    print( "Creating movie of %s seconds. Max segment length: %s." % ( duration, max_seg_length ) )
    for i, file in enumerate( sorted( src_path.glob( '*' ) ) ):
        filename, ext = os.path.splitext( file.name )
        print( "Input file: %s" % file )
        if( ext in allowed ):
            clip = VideoFileClip( str( file ) )
            clips.append( clip )

    while duration > 0:
        clip = random.choice ( clips )
        start = random.randint( 0, int(clip.duration) - 1)
        len = random.randint( 1, min( max_seg_length, duration ) )
        if start + len > clip.duration: # length cant be longer then the time left in the clip
            len = int( clip.duration - start )
        duration -= len
        print( "segment length: %s, duration left: %s, clip duration: %s" % ( len, duration, clip.duration ) )
        seg = clip.subclip( start, start + len ).on_color( size=( 1920, 1080 ), color=( 0, 0, 0 ) )
        # newclip = ( seg.fx( vfx.colorx, 0.5))
        if random.randint( 0, 2 ) == 2: # random filter chance :)
            seg = seg.fl_image( invert_green_blue )
        # if random.randint( 0, 2 ) == 2: # random filter chance :)
        # seg = ( seg.fx( vfx.freeze_region, t=0, region=(960-300,540-100,960+300,540+100) ))
        edits.append( seg )

    timestr = time.strftime( "%Y-%m%d-%H%M%S" )
    final_clip = concatenate_videoclips( edits )
    final_clip.write_videofile( "output/hdsa%s.mp4" % timestr )

def main(argv):
    global duration, max_seg_length
    parser = argparse.ArgumentParser(description='Generate H&D Book')
    parser.add_argument('-d','--duration', help='Duration of output file', default = 60 )
    parser.add_argument('-m','--max_seg_length', help='Max segment length', default = 15 )
    args = parser.parse_args()
    if args.duration:
        duration = int(args.duration)
    if args.max_seg_length:
        max_seg_length = int(args.max_seg_length)
    generate()

if __name__ == "__main__":
   main( sys.argv[ 1: ] )
