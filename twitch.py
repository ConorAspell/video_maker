from moviepy.editor import *
import moviepy.video.fx.all as vfx
from datetime import datetime
import requests
import json
import time
import os
import boto3


def extract(url="https://api.twitch.tv/kraken/clips/top?limit=5&game=League%20of%20Legends&trending=true&period=week"):
    referrer = "google.ie"
    client_id = '022i90v7stu8i3u71otlf5xxa6w8si'
    
    headers = {
        'Client-ID' : client_id,    
        'Accept': 'application/vnd.twitchtv.v5+json'
    }
    response = requests.get(url, headers=headers, timeout=10)
    clips=[]       
    test = json.loads(response.content)
    today = datetime.now().strftime("%d_%m_%Y")
    save_location = "top_clips_" + today
    for item in test['clips']:
        temp = item['thumbnails']['medium']
        temp2='-'.join(temp.split('-')[:-2])+".mp4"
        clips.append(temp2)
    bucketname='leinsterdash'

    for clip in clips:
        r=requests.get(clip)
        key=clip.split('/')[-1]
        s3=boto3.client('s3')
        place='/tmp/'+key
        #os.mkdir('league_videos/top_clips_'+today)
        final_key = 'league_videos/top_clips_' +today+'/'+key
        with open(final_key, 'wb') as f:
            f.write(r.content)
        #s3.upload_file(place, bucketname,final_key)
    
def transform(intro, paths):
    clips=[]
    final = VideoFileClip(intro)
    for path in paths:
        clips.append(VideoFileClip(path))
    for clip in clips:
        final = concatenate_videoclips([final, clip])
    today = datetime.now().strftime("%d_%m_%Y")
    save_location = "top_clips_" + today + ".mp4"
    final.write_videofile(save_location,fps=60) 
    return save_location
    
def load(save_location):
    pass

#url ="https://www.twitch.tv/directory/game/League%20of%20Legends/clips?range=7d"
extract()
today = datetime.now().strftime("%d_%m_%Y")
save_location = "top_clips_" + today
test=os.listdir('/home/conor/projects/Twitch/league_videos/'+save_location+'/')
for i in range(0, len(test)):
    test[i] = '/home/conor/projects/Twitch/league_videos/'+save_location+'/' +test[i]
transform(test[0], test)