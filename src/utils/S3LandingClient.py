import json
import os
import uuid
from datetime import datetime
from enum import Enum

import boto3


class S3Folder(Enum):
    PROJECTS = 'projects'
    TIME_ENTRIES = 'time-entries'
    USERS = 'users'
    GROUPS = 'groups'
    CALENDAR_EVENTS = 'events'
    PTO = 'pto'
    TEAMS = 'teams'
    BOARDS = 'boards'
    ACCOUNTS = 'accounts'
    RESOURCES_TAGS = 'resources-tags'
    TAGS = 'tags'


class EntityTypes(Enum):
    CLOCKIFY = 'clockify'
    GOOGLE_CALENDAR = 'google-calendar'
    MONDAY = 'monday'
    QUICKBOOKS = 'quickbooks'
    AWS = 'aws'
    SLACK = 'slack'


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return int(o.timestamp() * 1000000)

        return json.JSONEncoder.default(self, o)


class S3LandingClient:
    def __init__(self, entity_type: EntityTypes = EntityTypes.CLOCKIFY):
        self.s3 = boto3.client('s3')
        self.bucket_name = os.environ["LANDING_BUCKET_NAME"]
        self.entity_type = entity_type

        current_date = datetime.now()
        self.date_folder = current_date.strftime("%Y/%m/%d")

    def build_key_path(self, folder: S3Folder, custom_date=None, suffix=None):
        if custom_date:
            return f'{self.entity_type.value}/{folder.value}/{custom_date}/{suffix + "/" if suffix else ""}' \
                   f'{uuid.uuid4()}.json'
        else:
            return f'{self.entity_type.value}/{folder.value}/{self.date_folder}/{suffix + "/" if suffix else ""}' \
                   f'{uuid.uuid4()}.json'

    def put_jsonl_object(self, folder: S3Folder, json_array, suffix=None):
        if (json_array is None) or (len(json_array) == 0):
            return

        jsonl_string = ""
        key = self.build_key_path(folder, suffix=suffix)
        for json_obj in json_array:
            # Convert the JSON object to a string and append it to the JSONL string
            jsonl_string += json.dumps(json_obj, cls=DateTimeEncoder) + "\n"

        self.s3.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=jsonl_string,
            ContentType="application/json"
        )

    def put_object_formatted(self, folder: S3Folder, jsonl_str, custom_date):
        key = self.build_key_path(folder, custom_date)
        self.s3.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=jsonl_str,
            ContentType="application/json"
        )


if __name__ == '__main__':
    s3 = S3LandingClient(EntityTypes.CLOCKIFY)
    s3.put_jsonl_object(S3Folder.USERS, json.dumps({'test': 'test'}))
