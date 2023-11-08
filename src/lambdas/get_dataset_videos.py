import os

import boto3
from boto3.dynamodb.conditions import Attr
from youtube_dl import YoutubeDL

dataset_bucket_name = os.environ["DATASET_VIDEOS_BUCKET_NAME"]
dataset_dynamodb_name = os.environ["DATASET_VIDEOS_DYNAMODB_NAME"]

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

table = dynamodb.Table('dataset_dynamodb_name')


def download_video(video_url: str, quality_p=1080):
    # Configuration for youtube-dl
    ydl_opts = {
        'format': f'bestvideo[height<={quality_p}]+bestaudio/best[height<={quality_p}]',
        'outtmpl': f'/tmp/%(id)s.{quality_p}p.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

    return ydl_opts['outtmpl']


def put_mp4_video(bucket_name: str, key: str, video_path: str):
    s3.put_object(
        Bucket=bucket_name,
        Key=key,
        Body=video_path,
        ContentType="video/mp4"
    )


def youtube_video_to_s3(video_id: str, video_url: str, quality_p):
    video_path = download_video(video_url, quality_p=quality_p)
    put_mp4_video(bucket_name=dataset_bucket_name, key=f'{quality_p}/{video_id}', video_path=video_path)


def lambda_handler(event, context):
    # Scan the DynamoDB table for videos where 'upload' is False
    response = table.scan(
        FilterExpression=Attr('upload').eq(False)
    )

    # Iterate over the items returned by the scan
    for item in response['Items']:
        video_id = item['id']
        video_url = f'https://www.youtube.com/watch?v={video_id}'

        youtube_video_to_s3(video_id, video_url, 1080)
        youtube_video_to_s3(video_id, video_url, 480)

        # Update the 'upload' attribute to True
        table.update_item(
            Key={'id': video_id},
            UpdateExpression='SET upload = :val',
            ExpressionAttributeValues={
                ':val': True
            }
        )

    return {
        'statusCode': 200,
        'body': 'Videos processed successfully'
    }
