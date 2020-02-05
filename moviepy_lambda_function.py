from moviepy.editor import *
import moviepy.video.fx.all as vfx
from datetime import datetime, timedelta
import requests
import json
import time
import os
import boto3
import pytz



def lambda_handler(event, context):
    utc=pytz.UTC
    s3=boto3.client('s3')
    resp = s3.list_objects_v2(Bucket='leinsterdash')
    paths = []
    
    test= timedelta(hours=3)
    three_hours_ago = utc.localize(datetime.now()-test)
    
    for obj in resp['Contents']:
        if  obj['LastModified'] > three_hours_ago and obj['Key'].split('.')[-1] == 'mp4':
            paths.append(obj['Key'])
    bucketname='leinsterdash'
    intro = []
    
    clips=[]
    #final = VideoFileClip(intro)
    for path in paths:
        s3.download_file(Bucket=bucketname,Key=path, Filename='/tmp/' +path.split('/')[-1])
        clips.append(VideoFileClip('/tmp/' + path.split('/')[-1]))
    final = clips[0]
    for clip in clips:
        final = concatenate_videoclips([final, clip], method='compose')
    today = datetime.now().strftime("%M_%H_%d_%m_%Y")
    save_location = "/tmp/top_clips_" + today + ".mp4"
    final_key = 'final_videos/'+ save_location.split('/')[-1]
    final.write_videofile(save_location,fps=60) 
    
    s3.upload_file(save_location, bucketname,final_key)

lambda_handler(0,0)