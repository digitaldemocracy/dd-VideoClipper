import os
from flask import current_app, jsonify, redirect, request, url_for
from . import api
from ..helper import create_outfile, get_env_var, validate_client
from .request import get_file
from ..video_editor import video_editor
from ..s3utility import s3utility

@api.route('/video_editor/concat', methods=['POST'])
def concat_videos():
    json_obj = request.get_json()
    if json_obj is None or not validate_client(request.remote_addr):
        return jsonify({}),500
    videos = json_obj.get('videos')
    print videos
    videofiles = []
    for video in videos:
        videofiles.append(get_file(video))
    outfile = create_outfile(json_obj.get('uid'), videos)
    print json_obj
    print "video files", videofiles
    transition = True if json_obj.get('transition') else False
    result = video_editor.concat(videofiles, get_env_var('VIDEOFILE_DIR'),\
                                 outfile, transition)
    if result:
        result['uri'] = get_env_var('FILE_URL')+outfile
        #return jsonify({'uri':get_env_var('FILE_URL')+outfile}),201
        return jsonify(result),201
    else:
        return jsonify({}),500

@api.route('/video_editor/cut', methods=['POST'])
def cut_video():
    print request.json
    print request
    json_obj = request.get_json()
    if json_obj is None or not validate_client(request.remote_addr):
        return jsonify({}),500
    video = json_obj.get('video')
    videofile = get_file(video) 
    outfile = create_outfile(json_obj.get('uid'), [video])
    re_encode = True if json_obj.get('re_encode') else False
    result = video_editor.cut(videofile, get_env_var('VIDEOFILE_DIR'),\
                        outfile, json_obj.get('start'),\
                        json_obj.get('length'), re_encode)
    if result:
        result['uri'] = get_env_var('FILE_URL')+outfile
        print result
        return jsonify(result),201
    else:
        return jsonify({}),500

@api.route('/video_editor/upload', methods=['POST'])
def upload_video():
    print request.json
    print request
    json_obj = request.get_json()
    if json_obj is None or not validate_client(request.remote_addr):
        return jsonify({}),500
    video_id = json_obj.get('video_id') 
    s3url = get_env_var('S3URL')
    bucket = get_env_var('BUCKET')
    file_path = get_env_var('VIDEOFILE_DIR')
    videofile = get_file(video_id)
    thumbnails = video_editor.get_thumbnail(file_path, json_obj.get('video_id')+".mp4")
    urls = s3utility.upload_video(bucket, videofile, thumbnails)
    if urls is not None:
        return jsonify(urls),201
    else:
        return jsonify({}),500

@api.route('/video_editor/delete', methods=['POST'])
def delete_video():
    print request.json
    print request
    json_obj = request.get_json()
    if json_obj is None or not validate_client(request.remote_addr):
        return jsonify({}),500
    video_id = json_obj.get('video_id') 
    s3url = get_env_var('S3URL')
    bucket = get_env_var('BUCKET')
    file_path = get_env_var('VIDEOFILE_DIR')
    file_with_path = file_path + video_id + '.mp4'
    if os.path.isfile(file_with_path):
        os.remove(file_with_path)
    s3utility.delete_video(s3url, bucket, file_path, video_id)
    return jsonify({'message':'success!'}),201



#=======================================================================
#=======================================================================

# For testing purposes.  I don't see a need to expose this in the API...
@api.route('/video_editor/get_audio', methods=['POST'])
def get_audio():
    print request.json
    print request
    json_obj = request.get_json()
    if json_obj is None or not validate_client(request.remote_addr):
        return jsonify({}),500
    video = json_obj.get('video')
    videofile = get_file(video) 
    outfile = create_outfile(json_obj.get('uid'), [video], ext='.mp3')
    result = video_editor.extract_audio(videofile, get_env_var('VIDEOFILE_DIR'),\
                        outfile)
    if result:
        result['uri'] = get_env_var('FILE_URL')+outfile
        print result
        return jsonify(result),201
    else:
        return jsonify({}),500

#ROFLStomps the video's audio, and replaces it with an audio track
@api.route('/video_editor/replace_audio', methods=['POST'])
def replace_audio():
    print request.json
    print request
    json_obj = request.get_json()
    if json_obj is None or not validate_client(request.remote_addr):
        return jsonify({}),500
    video = json_obj.get('video')
    audio = json_obj.get('audio')
    videofile = get_file(video) 
    #TODO: update cache system to handle mp3 files
    #audiofile = get_env_var('VIDEOFILE_DIR') + audio + ".mp3" #get_file(audio) 
    audiofile = get_file(audio,ext=".mp3")
    print "AUDIO FILE: " + audiofile
    outfile = create_outfile(json_obj.get('uid'), [video])

    result = video_editor.replace_audio(videofile, audiofile, get_env_var('VIDEOFILE_DIR'),\
                        outfile)
    if result:
        result['uri'] = get_env_var('FILE_URL')+outfile
        print result
        return jsonify(result),201
    else:
        return jsonify({}),500

# Concatinates audio files
# Note: all audio files need to be the same codec :/ 
# only works on mp3's for now because of hardcoding the file extention due to the lack
# of audio file caching. 
@api.route('/video_editor/concat_audio', methods=['POST'])
def concat_audio():
    print request.json
    print request
    json_obj = request.get_json()
    if json_obj is None or not validate_client(request.remote_addr):
        return jsonify({}),500
    audios = json_obj.get('audios')
    outfile = create_outfile(json_obj.get('uid'), audios, ext='.mp3')

    #TODO: cache mp3s?
    for i in range(len(audios)):
        audios[i] = get_env_var('VIDEOFILE_DIR')  + audios[i]

    result = video_editor.concat_audio(audios, get_env_var('VIDEOFILE_DIR'),outfile)
    if result:
        result['uri'] = get_env_var('FILE_URL')+outfile
        print result
        return jsonify(result),201
    else:
        return jsonify({}),500        


#Adds an additional audio track to the video  ON TOP 
@api.route('/video_editor/add_audio', methods=['POST'])
def add_audio():
    print request.json
    print request
    json_obj = request.get_json()
    if json_obj is None or not validate_client(request.remote_addr):
        return jsonify({}),500
    video = json_obj.get('video')
    audio = json_obj.get('audio')
    videofile = get_file(video) 
    #TODO: Add audio file caching
    audiofile = get_env_var('VIDEOFILE_DIR') + audio + ".mp3" #get_file(audio) 
    outfile = create_outfile(json_obj.get('uid'), [video])

    result = video_editor.add_audio(videofile, audiofile, get_env_var('VIDEOFILE_DIR'),\
                        outfile)
    if result:
        result['uri'] = get_env_var('FILE_URL')+outfile
        print result
        return jsonify(result),201
    else:
        return jsonify({}),500


#Adds text overlay to a video using ffmpeg's draw feature
@api.route('/video_editor/add_text', methods=['POST'])
def add_text():   
    if 'file' not in request.files:
        print "NO FILE"
        return jsonify({}),500

    file = request.files['file']
    filename = (file.filename) #todo: sanitize filename!!!!!
    file.save(os.path.join(get_env_var('VIDEOFILE_DIR'), filename))

    if 'video' not in request.form:
        print "NO FILE 2"
        return jsonify({}),500

    video = request.form['video']
    videofile = get_file(video) 

    outfile = create_outfile(request.form['uid'], [video])

    result = video_editor.add_text(videofile, get_env_var('VIDEOFILE_DIR') + filename, get_env_var('VIDEOFILE_DIR'),\
                        outfile)
    if result:
        result['uri'] = get_env_var('FILE_URL')+outfile
        print result
        return jsonify(result),201
    else:
        return jsonify({}),500



