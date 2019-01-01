import boto3
file_path = '/var/www/html/sites/default/files/videos/dfba7b37be9181ca291990af2db5e96e.mp4'
key = 'examples/dfba7b37be9181ca291990af2db5e96e.mp4'
bucket = 'dd-clip-storage'
s3 = boto3.client('s3')
s3.upload_file(file_path, bucket, key)
