import os

import boto3
from boto3_type_annotations.s3 import Client
from dotenv import load_dotenv
from flask import Flask, render_template

load_dotenv()

app = Flask(__name__)


def get_most_recent_upload(type: str) -> str:
    """Get last scheduled image filename
    Parameters
    ---------

    type: str
        scheduled or requested, since its prefix for images on S3 Bucket.
    """

    s3bucket = os.environ['S3_BUCKET']
    s3client: Client = boto3.client('s3')

    get_last_modified = lambda obj: int(obj['LastModified'].strftime('%s'))  # noqa: E731,E501
    objs: dict = s3client.list_objects_v2(
        Bucket=s3bucket,
        Prefix=f'uploaded_images/{type}/'
    )['Contents']
    last_added: str = [
        obj['Key'] for obj in sorted(objs, key=get_last_modified)
    ][-1]
    s3_url_link = os.path.join(
        "https://alita-webapp.s3.eu-west-3.amazonaws.com",
        last_added
    )

    return s3_url_link


@app.route('/')
def scheduled():

    image = get_most_recent_upload(type='scheduled')
    print(image)
    return render_template("scheduled.html", scheduled_image=image)


@app.route('/requested', methods=["POST", "GET"])
def requested():

    lambda_arn = os.environ['LAMBDA_REQUESTED_ARN']
    lambdaclient: Client = boto3.client('lambda')
    lambdaclient.invoke(
        FunctionName=lambda_arn,
        InvocationType='RequestResponse'
    )
    image = get_most_recent_upload(type='requested')
    return render_template('requested.html', requested_image=image)


if __name__ == '__main__':

    load_dotenv()

    PORT = int(os.environ["PORT"])
    app.run(host="0.0.0.0", port=PORT)
