import os
import subprocess

import boto3
from boto3.dynamodb.conditions import Attr
from yt_dlp import YoutubeDL

dataset_bucket_name = os.environ["DATASET_VIDEOS_BUCKET_NAME"]
dataset_dynamodb_name = os.environ["DATASET_VIDEOS_DYNAMODB_NAME"]

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

table = dynamodb.Table(dataset_dynamodb_name)


def download_video(video_id: str, video_url: str, quality_p=1080):
    path = f'./tmp/{video_id}.{quality_p}p.webm'
    # Configuration for youtube-dl
    ydl_opts = {
        'format': f'bestvideo[height<={quality_p}]+bestaudio/best[height<={quality_p}]',
        'outtmpl': f'./tmp/%(id)s.{quality_p}p.%(ext)s',
        # 'postprocessors': [{
        #     'key': 'FFmpegVideoConvertor',
        #     'preferedformat': 'mp4',
        # }],
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

    return path


def upload_file_to_s3(bucket_name: str, key: str, file_path: str):
    s3.upload_file(file_path, bucket_name, key)


def youtube_video_to_s3(video_id: str, video_url: str, quality_p):
    video_path = download_video(video_id, video_url, quality_p=quality_p)
    split_video_into_frames(video_path, video_id, quality_p)
    # upload_file_to_s3(bucket_name=dataset_bucket_name, key=f'{video_id}/video/{quality_p}.webm', file_path=video_path)


def split_video_into_frames(video_path: str, video_id: str, quality_p: int):
    frames_directory = f'./tmp/{video_id}_frames_{quality_p}p'
    os.makedirs(frames_directory, exist_ok=True)
    frames_path = os.path.join(frames_directory, 'frame-%04d.jpg')

    # Run FFmpeg command to extract frames
    subprocess.run(['ffmpeg', '-i', video_path, frames_path])

    # Upload each frame to S3
    for frame_file in os.listdir(frames_directory):
        frame_path = os.path.join(frames_directory, frame_file)
        frame_key = f'{video_id}/frames/{quality_p}/{frame_file}'
        upload_file_to_s3(bucket_name=dataset_bucket_name, key=frame_key, file_path=frame_path)


def handler(event, context):
    # Scan the DynamoDB table for videos where 'upload' is False
    response = table.scan(
        FilterExpression=Attr('upload').ne(True)
    )

    print(response)
    # Iterate over the items returned by the scan
    for item in response['Items']:
        video_id = item['id']
        video_url = f'https://www.youtube.com/watch?v={video_id}'

        youtube_video_to_s3(video_id, video_url, 480)
        # youtube_video_to_s3(video_id, video_url, 1080)

        # Update the 'upload' attribute to True
        # table.update_item(
        #     Key={'id': video_id},
        #     UpdateExpression='SET upload = :val',
        #     ExpressionAttributeValues={
        #         ':val': True
        #     }
        # )

    return {
        'statusCode': 200,
        'body': 'Videos processed successfully'
    }


if __name__ == '__main__':
    handler('', '')
