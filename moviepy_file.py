from moviepy.editor import *
import moviepy.video.fx.all as vfx
from datetime import datetime, timedelta
import requests
import json
import time
import os
import boto3
import pytz
import httplib2
import os
import random
import sys
import time

from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

MAX_RETRIES = 10
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
CLIENT_SECRETS_FILE = "client_secrets.json"
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")

def get_videos():
    number_of_videos = os.environ.get("number_of_videos")
    url="https://api.twitch.tv/kraken/clips/top?limit="+str(number_of_videos)+"&game=League%20of%20Legends&trending=true&period=week"
    referrer = "google.ie"
    client_id = '022i90v7stu8i3u71otlf5xxa6w8si'
    headers = {
        'Client-ID' : client_id,    
        'Accept': 'application/vnd.twitchtv.v5+json'
    }
    response = requests.get(url, headers=headers, timeout=10)
    clips=[]    
    places=[]   
    test = json.loads(response.content)
    print(test)
    today = datetime.now().strftime("%d_%m_%Y")
    save_location = "top_clips_" + today
    for item in test['clips']:
        temp = item['thumbnails']['medium']
        temp2='-'.join(temp.split('-')[:-2])+".mp4"
        clips.append(temp2)
    for clip in clips:
        r=requests.get(clip)
        key=clip.split('/')[-1]
        place=key
        with open(place, 'wb') as f:
            f.write(r.content)
        places.append(place)
    return places

def lambda_handler(paths):
    clips=[]
    #final = VideoFileClip(intro)
    for path in paths:
        clips.append(VideoFileClip(path))
    final = clips[0]
    for clip in clips:
        final = concatenate_videoclips([final, clip], method='compose')
    today = datetime.now().strftime("%M_%H_%d_%m_%Y")
    save_location = "/tmp/top_clips_" + today + ".mp4"
    final_key = 'final_videos/'+ save_location.split('/')[-1]
    final.write_videofile(save_location,fps=60) 
    print('complete')
    print(save_location)
    return save_location



def get_authenticated_service(args):
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
        scope=YOUTUBE_UPLOAD_SCOPE)

    storage = Storage("%s-oauth2.json" % sys.argv[0])
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage, args)

    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
        http=credentials.authorize(httplib2.Http()))

def initialize_upload(youtube, options, test_file):
    tags = None
    if options.keywords:
        tags = options.keywords.split(",")

    body=dict(
        snippet=dict(
            title=options.title,
            description=options.description,
            tags=tags,
            categoryId=options.category
        ),
        status=dict(
            privacyStatus=options.privacyStatus
        )
    )

    # Call the API's videos.insert method to create and upload the video.
    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=MediaFileUpload(test_file, chunksize=-1, resumable=True)
    )

    resumable_upload(insert_request)

def resumable_upload(insert_request):
    response = None
    error = None
    retry = 0
    while response is None:
        print("Uploading file...")
        status, response = insert_request.next_chunk()
        print(response)
            
def upload_video(filepath='test.mp4'):
    #argparser.add_argument("--file", required=True, help="Video file to upload")
    print("HERE")
    argparser.add_argument("--title", help="Video title", default="Test Title 3")
    argparser.add_argument("--description", help="Video description",
        default="Test Description")
    argparser.add_argument("--category", default="22",
        help="Numeric video category. " +
            "See https://developers.google.com/youtube/v3/docs/videoCategories/list")
    argparser.add_argument("--keywords", help="Video keywords, comma separated",
        default="")
    argparser.add_argument("--privacyStatus", choices=VALID_PRIVACY_STATUSES,
        default=VALID_PRIVACY_STATUSES[0], help="Video privacy status.")
    args = argparser.parse_args()
    print('broke at args')
    if not os.path.exists(filepath):
        exit("Please specify a valid file using the --file= parameter.")

    youtube = get_authenticated_service(args)
    initialize_upload(youtube, args,filepath)



places=get_videos()
filename=lambda_handler(places)
print(filename)
upload_video(filename)
print('hello world')