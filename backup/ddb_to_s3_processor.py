import os
import json
import boto3
import csv
import io


def test():
    return 'OK!'

def lambda_handler(event, context):
    # Get the DynamoDB stream records from the event

    print(event)

    records = event['Records']

    s3_client = boto3.client('s3') 

    s3_bucket = os.environ['KRONOS_S3_BUCKET']
     
    # Create an in-memory CSV file
    

    # Create a CSV writer
    

    # Iterate over the records and extract the JSON data
    for record in records:

        csv_buffer = io.StringIO()
        csv_writer = csv.writer(csv_buffer)
    
        eventName = record.get('eventName')

        # Get the new or updated item from the stream record
        #item = record.get('dynamodb').get('NewImage') or record.get('dynamodb').get('OldImage')
        item = record.get('dynamodb').get('NewImage')

        itemType = record.get('dynamodb').get('NewImage').get("ItemType").get("S")
        serviceId = record.get('dynamodb').get('NewImage').get("ServiceId").get("S")
        serviceRunId = record.get('dynamodb').get('NewImage').get("ServiceRunId").get("S")
        trackingActivityId = record.get('dynamodb').get('NewImage').get("TrackingActivityId").get("S")


        # Convert the DynamoDB JSON item to a Python dictionary
        item_dict = {k: v.get(list(v.keys())[0]) for k, v in item.items()}

        # Write the dictionary values as a CSV row
        csv_writer.writerow(item_dict.values())

        # Get the CSV data as a string
        csv_data = csv_buffer.getvalue()

        # Upload the CSV data to S3
        

        s3_key = itemType.lower() + '/trackingactivityid=' + trackingActivityId +  '/servicerunid=' + serviceRunId + "/service-run.csv"
        s3_client.put_object(Body=csv_data, Bucket=s3_bucket, Key=s3_key)

        s3_key2 = itemType.lower() + 'indexserviceid' + '/serviceid=' + serviceId + "/service-run-id.csv"
        csv_data2 = serviceRunId
        s3_client.put_object(Body=csv_data2, Bucket=s3_bucket, Key=s3_key2)

    return {
        'statusCode': 200,
        'body': 'CSV data converted and uploaded to S3'
    }