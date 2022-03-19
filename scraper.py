import os
import io

import boto3
from dotenv import load_dotenv

load_dotenv()


def scrape_subreddit_to_s3():
    """
    Scrape Alita subreddits content to S3 Bucket.
    """

    s3bucket = os.environ['S3_BUCKET']



