import os

import boto3
import pandas as pd
from botocore.exceptions import ClientError
from loguru import logger

REGION_PARIS = 'eu-west-3'
BUCKET_OC_P8 = 'oc-p8'
DATA_LOCAL_PATH = './data/fruits-360_dataset/fruits-360'
EMR_NAME = 'oc-p8_cluster'


def is_s3_object_exist(s3_client, bucket, key):
    try:
        s3_client.head_object(Bucket=bucket, Key=key)
    except ClientError as e:
        return int(e.response['Error']['Code']) != 404
    return True


def main():
    s3_client = boto3.client('s3', region_name=REGION_PARIS)

    # Create S3 bucket
    response = s3_client.list_buckets()
    s3_bucket_name_list = [bucket["Name"] for bucket in response['Buckets']]

    if BUCKET_OC_P8 not in s3_bucket_name_list:
        logger.info(f"Bucket '{BUCKET_OC_P8} creation in '{REGION_PARIS}' region'...")
        location = {'LocationConstraint': REGION_PARIS}
        s3_client.create_bucket(Bucket=BUCKET_OC_P8, CreateBucketConfiguration=location)
    else:
        logger.info(f"Bucket '{BUCKET_OC_P8}' already exists!")

    # Upload EMR config
    logger.info("Upload config...")
    s3_client.upload_file("./data/emr_config.json", BUCKET_OC_P8, "emr_config.json")

    # Upload notebook
    logger.info("Upload notebook...")
    s3_client.upload_file("./P8_01_notebookexploration.ipynb", BUCKET_OC_P8, "jupyter/jovyan/P8_01_notebookexploration.ipynb")

    # Upload bootstrap script
    logger.info("Upload bootstrap script...")
    s3_client.upload_file("./data/emr_bootstrap.sh", BUCKET_OC_P8, "emr_bootstrap.sh")

    # Upload application
    logger.info("Upload application...")
    s3_client.upload_file("./data/app.py", BUCKET_OC_P8, "app.py")

    # Load images list
    images_df = pd.read_csv(DATA_LOCAL_PATH + "/training_images.csv")
    images_df['filename'] = images_df.apply(lambda x: os.path.basename(x.image), axis=1)
    images_df['objectname'] = images_df.apply(lambda x: f"images/{x.label}/{x.filename}", axis=1)
    images_df['set'] = 'training'
    logger.info(f"Read images csv: {images_df.shape}")
    sample_size = 10
    sample_images_df = images_df.groupby('label').apply(lambda x: x.sample(sample_size, random_state=1))

    # Upload some images to s3
    for i, r in sample_images_df.iterrows():
        if not is_s3_object_exist(s3_client, BUCKET_OC_P8, r.objectname):
            logger.info(f"Upload {r.image}")
            s3_client.upload_file(
                r.image, BUCKET_OC_P8, r.objectname,
                ExtraArgs={'Metadata': {'labal': r.label, 'set': r.set}}
            )
        else:
            logger.info(f"Object {r.objectname} already exists!")

    # List EMR cluster
    emr = boto3.client('emr')
    response = emr.list_clusters(
        ClusterStates=[
            'STARTING',
            'BOOTSTRAPPING',
            'RUNNING',
            'WAITING',
            # 'TERMINATING',
            # 'TERMINATED',
            # 'TERMINATED_WITH_ERRORS',
        ]
    )
    emr_cluster_name_list = [c['Name'] for c in response['Clusters']]
    logger.info(f"Available EMR instances: {emr_cluster_name_list}")


if __name__ == '__main__':
    main()
