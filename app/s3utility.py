import boto3
import os
import sys
import traceback
from boto3.session import Session
from botocore.exceptions import ClientError
from flask import current_app
from .video_editor import video_editor
from .helper import create_outfile, get_env_var, validate_client

class s3utility:
    @staticmethod
    def upload_video(bucket, pathfile, thumbnails, key=None, secret=None):
        aws_key = key if key else get_env_var('AWS_ACCESS_KEY_ID')
        aws_secret = secret if secret else get_env_var('AWS_SECRET_ACCESS_KEY')
        tokens = pathfile.split("/")
        video_file = tokens[-1]
        video_id = video_file.split(".")[0]
        video_folder = "videos/" + video_id
        video_url=s3utility.upload_file(bucket, video_folder, pathfile,
                                        video_file, key=aws_key, secret=aws_secret)
        thumbnail_folder = video_folder+"/thumbnails"
        thumbnail_urls = []
        for key in thumbnails.keys():
            thumbnail = key+'.'+thumbnails[key].split(".")[-1]
            thumbnail_urls.append(
                s3utility.upload_file(bucket, thumbnail_folder, thumbnails[key],
                                      thumbnail, key=aws_key, secret=aws_secret))

        filesize = os.path.getsize(pathfile)
        duration = video_editor.get_duration(pathfile)

        return {'video_url':video_url,
                'thumbnail_url':thumbnail_urls,
                'filesize':filesize, 'duration':duration}

    @staticmethod
    def delete_video(bucket, path, video_id, key=None, secret=None):
        aws_key = key if key else get_env_var('AWS_ACCESS_KEY_ID')
        aws_secret = secret if secret else get_env_var('AWS_SECRET_ACCESS_KEY')
        video_folder = "videos/" + video_id
        video_key = video_folder + "/" + video_id + ".mp4"
        thumbnail_key = video_folder + "/thumbnails/default.jpg"
        s3 = boto3.client('s3', aws_access_key_id=aws_key, aws_secret_access_key=aws_secret)
        print bucket, video_key
        s3.delete_object(Bucket=bucket, Key=video_key)
        s3.delete_object(Bucket=bucket, Key=thumbnail_key)

    # Uploads the contents of a directory at [dirName] into the s3 bucket [bucket]
    # with the prefix [prefix]
    @staticmethod
    def upload_dir(bucket, dirName, prefix, key=None, secret=None):
        try:
            aws_key = key if key else get_env_var('AWS_ACCESS_KEY_ID')
            aws_secret = secret if secret else get_env_var('AWS_SECRET_ACCESS_KEY')
            s3 = boto3.client('s3', aws_access_key_id=aws_key, aws_secret_access_key=aws_secret)
            for root,dirs,files in os.walk(dirName):
                for f in files:
                    s3.upload_file(root + '/' + f, bucket, prefix + f,\
                        ExtraArgs={'ACL': 'public-read'})
            return 0
        except ClientError:
            return 1

    # Uploads a file into the s3 bucket [bucket] with specified folder and file name
    @staticmethod
    def upload_file(bucket, folder, pathfile, new_file_name=None, key=None, secret=None):
        try:
            aws_key = key if key else get_env_var('AWS_ACCESS_KEY_ID')
            aws_secret = secret if secret else get_env_var('AWS_SECRET_ACCESS_KEY')
            file_name = pathfile.split('/')[-1]
            file_type = s3utility.get_content_type(file_name)
            file_key = folder + "/" + new_file_name if new_file_name else file_name
            s3 = boto3.client('s3', aws_access_key_id=aws_key, aws_secret_access_key=aws_secret)
            s3.upload_file(pathfile, bucket, file_key,\
                ExtraArgs={'ACL': 'public-read', 'ContentType': file_type})

            s3url = get_env_var("S3URL") if get_env_var("S3URL") \
                else "https://s3-us-west-2.amazonaws.com"

            return s3url+'/'+bucket+'/'+file_key
        except:
            traceback.print_exc(file=sys.stdout)
            return None

    @staticmethod
    def get_content_type(file_name):
        ext = file_name.split(".")[-1].lower()
        if ext == "jpg" or ext == "jpeg":
            return "image/jpeg"
        if ext == "png":
            return "image/png"
        if ext == "gif":
            return "image/gif"
        if ext == "txt":
            return "text/plain"
        if ext == "rtf":
            return "text/rtf"
        if ext == "zip":
            return "application/zip"
        if ext == "doc":
            return "application/msword"
        if ext == "pdf":
            return "application/pdf"
        if ext == "mp3":
            return "audio/mpeg"
        if ext == "mp4":
            return "video/mp4"
        if ext == "html":
            return "text/html"
        if ext == "htm":
            return "text/html"
        if ext == "shtml":
            return "text/html"
        return None


