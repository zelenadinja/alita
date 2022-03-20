import io
import os

import boto3
import numpy as np
import praw
import requests  # type: ignore
from boto3_type_annotations.s3 import Client
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()


def scrape_img_to_s3(job_type: str, limit: int) -> bool:

    """
    Scrape random image from cyberpunk subreddit into s3 Bucket.

    Parameters
    ----------

    job_type: str
        Since web app have scheduled images and images scraped by user requests
        job type is either scheduled or requested.

    limit: int
        Number of posts to scrape

    Returns bool
        True if image was uploaded to Bucket else False
    """

    valid_extensions = ['.jpeg', '.jpg', '.png', '.gif']

    s3bucket: str = os.environ['S3_BUCKET']
    client_id: str = os.environ['CLIENT_ID']
    client_secret: str = os.environ['CLIENT_SECRET']
    username: str = os.environ['USERNAME']
    password: str = os.environ['PASSWORD']

    s3client: Client = boto3.client('s3')

    user = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent="cyberpunk_scraper",
        username=username,
        password=password,
    )

    cyberpunk_sub = user.subreddit("Cyberpunk")

    ulrs = []
    extensions = []

    for post in cyberpunk_sub.top(limit=limit):

        _, extension = os.path.splitext(post.url)

        if extension in valid_extensions:
            ulrs.append(post.url)
            extensions.append(extension)

    num_urls = len(ulrs)
    random_idx: int = np.random.randint(
        low=0,
        high=num_urls,
        size=1,
        dtype=int)[0]
    image_url = ulrs[random_idx]
    image_ext = extensions[random_idx]
    image_name = image_url.split(image_ext)[0].split("/")[-1]

    try:
        response = requests.get(image_url)
    except ValueError:
        raise ValueError("Something went wrong!")

    image_stream = io.BytesIO(response.content)

    try:
        s3client.upload_fileobj(
            Fileobj=image_stream,
            Bucket=s3bucket,
            Key=f"uploaded_images/{job_type}/{image_name}",
            ExtraArgs={"ContentType": f"image/{image_ext.split('.')[1]}"}
        )
    except ClientError:
        return False
    return True
