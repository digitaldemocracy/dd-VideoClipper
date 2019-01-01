0) Set up and starting the server
install virtualenv if not already installed
create a virtual environment (remove the existing venv directory included in the repo)
e.g. virtualenv venv

activate the virtual environment
e.g. source venv/bin/activate

install required python modules in the virtual environment
e.g. pip install -r requirements.txt

The video manager module also need to be installed. Please see the dd-VideoManager repo.

register your ip address:
The server does not serve api call made from unknown ip address.
To test from your remote machine, add your machine's ip address in the allowed_ip dictionary in validate_client function in app/helper.py.
To test on your local machine, make sure 127.0.0.1 is added in the allwed_ip dictionary (it is already added in the latest master branch of this repo).

You also need to set these environment variables:
 AWS_ACCESS_KEY_ID yyyyy
 AWS_SECRET_ACCESS_KEY xxxxx
 VIDEOFILE_DIR /xxx
 FILE_URL http://xxx.xxx.org/sites/default/files/videos/
 BUCKET s3bucket_name
 S3URL https://s3-us-west-2.amazonaws.com
 VIDEOMAN_PORT 80
 VIDEOMAN_HOST http://xxx.xxx.org

Start the server:
manage.py deploy

The above command will start your server at port 9000. To change the port, modify manage.py.

1) cut api call - cut a section of a vieo into a new video file
To test:
curl -H "Content-Type: application/json" -X POST -d '{"video":$videoid, "start":$start, "length":$duration, "uid":$user_id, "re_encode":1}' http://xxx.yyy.zzz:9000/api/v1.0/video_editor/cut

WEHRE $videoid is fileId in Video table in DDDB2016Aug database, e.g. a3f30eb0f87feb36b308d1f8a90b735e,
      $start is the cut start position in seconds, e.g. 10,
      $duration is the length of the cut from the start position in seconds, e.g. 60,
      $user_id is a user id, e.g. "test", you can use any string as your user id
      
Example call:
curl -H "Content-Type: application/json" -X POST -d '{"video":"a3f30eb0f87feb36b308d1f8a90b735e", "start":0, "length":3, "uid":"1", "re_encode":1}' http://clip.your-domain-name.org/api/v1.0/video_editor/cut

Example reply:
{
  "duration": 3.0,
  "size": 152029,
  "uri": "http://video.your-domain-name.org/sites/default/files/videos/a0c323357357b43198b57b1dea54039f.mp4"
}
      
2) concat api call - concatenate multiple videos
To test:
curl -H "Content-Type: application/json" -X POST -d '{"uid":$user_id, "videos":$videos, "transition":1}' http://xxx.yyy.zzz:9000/api/v1.0/video_editor/concat

WEHRE $user_id is a user id, e.g. "test", you can use any string as your user id,
      $videos is a json list of fileId in Video table in DDDB2016Aug database, e.g. a3f30eb0f87feb36b308d1f8a90b735e,
      transition is either you want transition bertween videos or not (1:yes, 0:no).
      
Example call:
curl -H "Content-Type: application/json" -X POST -d '{"uid":"test","videos":["a0c323357357b43198b57b1dea54039f","a0c323357357b43198b57b1dea54039f"], "transition":1}' http://clip.your-domain-name.org/api/v1.0/video_editor/concat

Example reply:
{
  "duration": 6.0,
  "size": 321748,
  "uri": "http://video.your-domain-name.org/sites/default/files/videos/5005763a753292e1ea9de1788418127e.mp4"
}

3) upload api call - upload a video to s3
To test:
curl -H "Content-Type: application/json" -X POST -d '{"video_id":$videoid}' http://xxx.yyy.zzz:9000/api/v1.0/video_editor/upload

WEHRE $videoid is a video file name excluding the file extension, e.g. 5005763a753292e1ea9de1788418127e for 5005763a753292e1ea9de1788418127e.mp4

Example call:
curl -H "Content-Type: application/json" -X POST -d '{"video_id":"5005763a753292e1ea9de1788418127e"}' http://clip.your-domain-name.org/api/v1.0/video_editor/upload

Example reply:
{
  "duration": 6.0,
  "filesize": 321748,
  "thumbnail_url": [
    "https://s3-us-west-2.amazonaws.com/your-s3bucket/videos/5005763a753292e1ea9de1788418127e/thumbnails/default.jpg",
    "https://s3-us-west-2.amazonaws.com/your-s3bucket/videos/5005763a753292e1ea9de1788418127e/thumbnails/large.jpg",
    "https://s3-us-west-2.amazonaws.com/your-s3bucket/videos/5005763a753292e1ea9de1788418127e/thumbnails/medium.jpg"
  ],
  "video_url": "https://s3-us-west-2.amazonaws.com/your-s3bucket/videos/5005763a753292e1ea9de1788418127e/5005763a753292e1ea9de1788418127e.mp4"
}

4) delete api call - delete a file from s3
PLASE DO NOT TRY THIS CALL




get_audio example: 
curl -H "Content-Type: application/json" -X POST -d '{"video":"rr", "uid":"1"}' http://127.0.0.1:9000/api/v1.0/video_editor/get_audio

replace_audio example: 
curl -H "Content-Type: application/json" -X POST -d '{"video":"rr", "audio":"nyan", "uid":"1"}' http://127.0.0.1:9000/api/v1.0/video_editor/replace_audio

concat audio example:
curl -H "Content-Type: application/json" -X POST -d '{"audios":["nyan","nyan"], "uid":"1"}' http://127.0.0.1:9000/api/v1.0/video_editor/concat_audio

add_audio
curl -H "Content-Type: application/json" -X POST -d '{"video":"rr", "audio":"nyan", "uid":"1"}' http://127.0.0.1:9000/api/v1.0/video_editor/add_audio


add_text
curl -X POST -F "file=@overlayFile.json" -F "video=rr" -F "uid=1" http://127.0.0.1:9000/api/v1.0/video_editor/add_text



