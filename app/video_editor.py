from flask import current_app
#from .paste_images import paste
import subprocess
import os
import re 
import json
from helper import  get_env_var

class video_editor:
    @staticmethod
    def concat(videos, path, outfile, transition=False):
        if path is None:
            path = "/videos/"
        outpath = video_editor.concat_recursively(videos[0], videos[1:],\
                                                  path, outfile, transition)
        return {'size':os.path.getsize(outpath),
                'duration':video_editor.get_duration(outpath)}\
               if os.path.isfile(outpath) and \
                  os.path.getsize(outpath) > 0 \
               else False 

    @staticmethod
    def cut(video, path, outfile, start, length=None, re_encode=False):
        length_str = ""
        if length is not None:
            length_str = " -t " + str(length)

        if re_encode :
            cmd = "ffmpeg -y -ss " + str(start) + " -i '" +\
                  video + "' -ss 0" + length_str +\
                  " -async 1 -strict -2 "
        else:
            cmd = "ffmpeg -y -ss " + str(start) + length_str +\
                  " -i '" + video +\
                  "' -codec copy "
              
        print cmd
        outpath = path+outfile
        print outpath
        output = subprocess.Popen(cmd+outpath, shell = True,\
                                  stdout = subprocess.PIPE).stdout.read()
        print "Done!", output
        return {'size':os.path.getsize(outpath),
                'duration':video_editor.get_duration(outpath)}\
               if os.path.isfile(outpath) and \
                  os.path.getsize(outpath) > 0 \
               else False


    @staticmethod
    def get_thumbnail(path, video_file):
        video = path + video_file
        outfile = video + "_0.jpg"
        screen_size = video_editor.get_screen_size(video)
        print "screen_size=",screen_size
        if screen_size is None or screen_size[0] < 656 or screen_size[1] < 368:
            cmd = "ffmpeg -y -i " + video + \
                  " -ss 0 -filter_complex '[0:v]pad=656:368:(ow-iw)/2:(oh-ih)/2[t1];"+\
                  "[t1]scale=120:-1[t2]' -map '[t2]' -vframes 1 " + outfile
        else:
            cmd = "ffmpeg -y -i " + video + \
                  " -ss 0 -filter_complex '[0:v]scale=120:-1[t1]' -map '[t1]' -vframes 1 "\
                  + outfile
        print cmd
        output = subprocess.Popen(cmd, shell = True,\
                   stdout = subprocess.PIPE).stdout.read()

        outfile1 = video + "_1.jpg"
        if screen_size is None or screen_size[0] < 656 or screen_size[1] < 368:
            cmd = "ffmpeg -y -i " + video + \
                  " -ss 0 -filter_complex '[0:v]pad=656:368:(ow-iw)/2:(oh-ih)/2[t1];"+\
                  "[t1]scale=360:-1[t2]' -map '[t2]' -vframes 1 " + outfile1
        else:
            cmd = "ffmpeg -y -i " + video + \
                  " -ss 0 -filter_complex '[0:v]scale=360:-1[t1]' -map '[t1]' -vframes 1 "\
                  + outfile1

        print cmd
        output = subprocess.Popen(cmd, shell = True,\
                     stdout = subprocess.PIPE).stdout.read()

        outfile2 = video + "_2.jpg"
        if screen_size is None or screen_size[0] < 656 or screen_size[1] < 368:
            cmd = "ffmpeg -y -i " + video + \
                  " -ss 0 -filter_complex '[0:v]pad=656:368:(ow-iw)/2:(oh-ih)/2[t1]'"+\
                  " -map '[t1]' -vframes 1 " + outfile2
        else:
            cmd = "ffmpeg -y -i " + video + " -ss 0 -vframes 1 " + outfile2

        print cmd
        output = subprocess.Popen(cmd, shell = True,\
                     stdout = subprocess.PIPE).stdout.read()

        return {"default":outfile, "medium":outfile1, "large":outfile2}
    
    @staticmethod
    def concat_recursively(video1, videos, path, outfile, transition=False):
        print video1
        print path
        start_fade = video_editor.get_duration(video1) - 1
        intermediate1 = path+outfile.split('.')[0] + "_1.mp4"
        screen_size = video_editor.get_screen_size(video1)
        cmd = ""
        #if screen_size is None or screen_size[0] != 640:
        if screen_size is None or screen_size[0] < 656 or screen_size[1] < 368:
            #cmd += "'[0:v]pad=640:ih:(ow-iw)/2[t1];"
            cmd += "'[0:v]pad=656:368:(ow-iw)/2:(oh-ih)/2[t1];"
            if transition:
                  cmd += "[t1]fade=t=out:st=" + str(start_fade) + ":d=1[v]'" +\
                         " -map '[v]' -map 0:a -ac 2 " + intermediate1
            else:
                  cmd += "' -map '[t1]' -map 0:a -ac 2 " + intermediate1
            cmd = "ffmpeg -y -i " + video1 + " -filter_complex " + cmd
        elif transition:
            cmd = "ffmpeg -y -i " + video1 + " -filter_complex " +\
                  "'[0:v]fade=t=out:st=" + str(start_fade) + ":d=1[v]'" +\
                  " -map '[v]' -map 0:a -ac 2 " + intermediate1
        if len(cmd) > 0:
            output = subprocess.Popen(cmd, shell = True,\
                                  stdout = subprocess.PIPE).stdout.read()
        else:
            intermediate1 = video1

        intermediate2 = path+outfile.split('.')[0] + "_2.mp4"
        screen_size = video_editor.get_screen_size(videos[0])
        cmd = ""
        #if screen_size is None or screen_size[0] != 640:
        if screen_size is None or screen_size[0] < 656 or screen_size[1] < 368:
            #cmd += "'[0:v]pad=640:ih:(ow-iw)/2[t1];"
            cmd += "'[0:v]pad=656:368:(ow-iw)/2:(oh-ih)/2[t1];"
            if transition:
                cmd += "[t1]fade=t=in:st=0:d=1[v]'" +\
                       " -map '[v]' -map 0:a -ac 2 " + intermediate2
            else:
                cmd += "' -map '[t1]' -map 0:a -ac 2 " + intermediate1
            cmd = "ffmpeg -y -i " + videos[0] + " -filter_complex " + cmd
        elif transition:
            cmd = "ffmpeg -y -i " + videos[0] + " -filter_complex " +\
                  "'[0:v]fade=t=in:st=0:d=1[v]'" +\
                  " -map '[v]' -map 0:a -ac 2 " + intermediate2
        if len(cmd) > 0:
            output = subprocess.Popen(cmd, shell = True,\
                                  stdout = subprocess.PIPE).stdout.read()
        else:
            intermediate2 = videos[0]

        intermediate1_1 = intermediate1.split('.')[0]+'.ts'
        cmd = "ffmpeg -y -i " + intermediate1 +\
              " -c copy -bsf:v h264_mp4toannexb -f mpegts "+intermediate1_1
        output = subprocess.Popen(cmd, shell = True,\
                                  stdout = subprocess.PIPE).stdout.read()
        intermediate2_1 = intermediate2.split('.')[0]+'.ts'
        cmd = "ffmpeg -y -i " + intermediate2 +\
              " -c copy -bsf:v h264_mp4toannexb -f mpegts "+intermediate2_1
        output = subprocess.Popen(cmd, shell = True,\
                                  stdout = subprocess.PIPE).stdout.read()

        outpath = path + outfile
        cmd = 'ffmpeg -y -i "concat:' + intermediate1_1 + '|' + intermediate2_1 +\
              '" -c copy -bsf:a aac_adtstoasc ' + outpath
        output = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE)\
                 .stdout.read()
        if (len(videos) > 1):
            outpath = video_editor.concat_recursively(outpath, videos[1:],\
                                                      path, outfile, transition)
        return outpath

    @staticmethod
    def get_duration(filename):
        print filename
        result = subprocess.Popen(["ffprobe", filename],\
                     stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        matched_line = [x for x in result.stdout.readlines() if "Duration" in x]
        if matched_line:
            match = re.search(r'Duration: (\d\d:\d\d:\d\d.\d\d)', matched_line[0])
            if match:
                time_components =  match.group(1).split(":")
                factor = 60 * 60
                duration = 0
                for component in time_components:
                    if factor:
                        duration += float(component) * factor
                        factor /= 60
                    else:
                        duration += float(component)
                return round(duration,1)
        return 0

    @staticmethod
    def get_screen_size(filename):
        print filename
        result = subprocess.Popen(["ffprobe", filename],\
                     stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        matched_line = [x for x in result.stdout.readlines() if "Video:" in x]
        if matched_line:
            match = re.search(r'(\d\d\d+x\d\d\d+)', matched_line[0])
            print match
            if match:
                size_components =  match.group(1).split("x")
                return (int(size_components[0]), int(size_components[1]))
        return None 

#============================================================================
#============================================================================

    """
    Concats all audio files.
    TODO: Make this function work on multiple codecs
    @param audios
        Listof audio files w/o extension .
    @param path
        The path of the output mp3 file
    @param outfile
        The name of the output mp3 file
    @return
        new concat audio file info
    """    
    @staticmethod
    def concat_audio(audios, path, outfile):
        audioStr = ''
        for file in audios:
            audioStr += file + ".mp3" + "|" # TODO: Support more than mp3s?
        cmd = 'ffmpeg -i "concat:{}" -c copy '.format(audioStr[:-1])
        print cmd
        outpath = path+outfile
        print outpath
        output = subprocess.Popen(cmd+outpath, shell = True,\
                                  stdout = subprocess.PIPE).stdout.read()
        print "Done!", output
        return {'size':os.path.getsize(outpath),
                'duration':video_editor.get_duration(outpath)}\
               if os.path.isfile(outpath) and \
                  os.path.getsize(outpath) > 0 \
               else False

    """
    Extracts the audio from a video file in MP3 format.

    @param video
        The name of the video file.
    @param path
        The path of the output mp3 file
    @param outfile
        The name of the output mp3 file
    @return
        JSON result of the extraced audio file.  
    """  
    @staticmethod
    def extract_audio(video, path, outfile):
        cmd="ffmpeg -i " + video + " -q:a 0 -map a "
        print cmd
        outpath = path+outfile
        print outpath
        output = subprocess.Popen(cmd+outpath, shell = True,\
                                  stdout = subprocess.PIPE).stdout.read()
        print "Done!", output
        return {'size':os.path.getsize(outpath),
                'duration':video_editor.get_duration(outpath)}\
               if os.path.isfile(outpath) and \
                  os.path.getsize(outpath) > 0 \
               else False
    """
    Replaces the audio track of a video with another audio track.

    @param video
        The name of the video file.
    @param audio
        The name of the audio file
    @param path
        The path of the output mp3 file
    @param outfile
        The name of the output mp3 file
    @return
        JSON result of the extraced audio file.  
    """            
    @staticmethod
    def replace_audio(video,audio,path,outfile):
        cmd = "ffmpeg -i " + video + " -i " + audio + \
              " -c:v copy -c:a aac -strict experimental -map 0:v:0 -map 1:a:0 "
        print cmd
        outpath = path+outfile
        print outpath
        output = subprocess.Popen(cmd+outpath, shell = True,\
                                  stdout = subprocess.PIPE).stdout.read()
        print "Done!", output
        return {'size':os.path.getsize(outpath),
                'duration':video_editor.get_duration(outpath)}\
               if os.path.isfile(outpath) and \
                  os.path.getsize(outpath) > 0 \
               else False
    """
    Adds an audio track to an existing video.

    @param video
        The name of the video file.
    @param path
        The path of the output mp3 file
    @param outfile
        The name of the output mp3 file
    @return
        JSON result of the extraced audio file.  
    """  
    @staticmethod
    def add_audio(video,audio,path,outfile):
        # Step 1) Extract audio
        extractedFile = path + "extracted_"+outfile[:-1]+"3" #todo: change file ext hardcode
        cmd = "ffmpeg -i {} {}".format(video,extractedFile) 
        output = subprocess.Popen(cmd, shell = True,\
                                  stdout = subprocess.PIPE).stdout.read()
        print "Done Extracting mp3 file"

        # Step 2) Combined original audio file and new audio file
        finalAudio = path + "audioFinal_" + outfile[:-1]+"3"
        cmd = "ffmpeg -i {} -i {} -filter_complex \"[0:0][1:0] amix=inputs=2:duration=longest\" -c:a libmp3lame {}".format(audio,extractedFile,finalAudio)
        #cmd = "ffmpeg -i {} -i {} -filter_complex amerge -c:a libmp3lame -q:a 4 {}".format(audio,extractedFile,finalAudio)

        output = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE).stdout.read()
        print "Done creating final mp3 file"

        # Step 3) Merge final audio file with the video
        cmd = "ffmpeg -i {} -i {} -c:v copy -c:a aac -strict experimental -map 0:v:0 -map 1:a:0 ".format(video,finalAudio)
        print cmd
        outpath = path+outfile
        print outpath
        output = subprocess.Popen(cmd+outpath, shell = True,\
                                  stdout = subprocess.PIPE).stdout.read()
        print "Done!", output
        return {'size':os.path.getsize(outpath),
                'duration':video_editor.get_duration(outpath)}\
               if os.path.isfile(outpath) and \
                  os.path.getsize(outpath) > 0 \
               else False




    """
    Adds text overlay to a video

    @param video
        The name of the video file.
    @param text
        JSON file containing the text overlay 
    @param path
        The path of the output mp3 file
    @param outfile
        The name of the output mp3 file
    @return
        JSON result of the extraced audio file.  
    """  
    @staticmethod
    def add_text(video,text,path,outfile):
        drawsTextStr = "\"" + parseOverlayFile(text) + "\""
        cmd = "ffmpeg -i {} -vf ".format(video) + drawsTextStr + " "
        print "COMMAND: " + cmd

        outpath = path+outfile
        print outpath
        output = subprocess.Popen(cmd+outpath, shell = True,\
                                  stdout = subprocess.PIPE).stdout.read()
        print "Done!", output
        return {'size':os.path.getsize(outpath),
                'duration':video_editor.get_duration(outpath)}\
               if os.path.isfile(outpath) and \
                  os.path.getsize(outpath) > 0 \
               else False


#input: overlay file
#output: drawtext string
def parseOverlayFile(overlayFile):
  dataFile = open(overlayFile,'r')
  data = json.load(dataFile)
  drawTextStr = ''
  for x in data:
    drawTextStr += "drawtext="
    startTime = -1
    endTime = -1

    for attrib in x:
      if attrib == 'startTime':
        startTime = x[attrib]
      elif attrib == 'endTime':
        endTime = x[attrib]
      else:
        if attrib == "text":
          drawTextStr += attrib + "=" + str(x[attrib]).replace(":", "\\:").replace("'", "\\\\\\\\\\\\'")
        else:  
          drawTextStr += attrib + "="+ str(x[attrib]).replace(":","\\:")
        drawTextStr += ":"

    drawTextStr += "fontfile=\'{}\':".format( get_env_var('VIDEOFILE_DIR') + "/TNR.ttf") #TODO: NEED TO INCLUDE FONT IN SYSTEM

    if startTime != -1 and endTime != -1:
      drawTextStr += 'enable=\'between(t,{},{})\''.format(startTime,endTime)
    else:
      drawTextStr = drawTextStr[:-1]

    drawTextStr += ','
  return drawTextStr[:-1]

    




