from datetime import datetime


event = """
[ 
        {"Records": [
            {
                "EventSource": "aws:sns",
                "EventVersion": "1.0",
                "EventSubscriptionArn": "arn:aws:sns:us-east-1:289485838881:hdmap-services-events-production:e53d9a4c-580c-4ddf-8a55-96a1f1894edb",
                "Sns": {
                    "Type": "Notification",
                    "MessageId": "e02099d7-9be5-58d4-9ae4-c4eb553978d4",
                    "TopicArn": "arn:aws:sns:us-east-1:289485838881:hdmap-services-events-production",
                    "Subject": null,
                    "Message": null,
                    "Timestamp": null,
                    "SignatureVersion": "1",
                    "Signature": "EG5n9yuZP1pFZrgINno3F8n6K9y0epayh9NVC98m6ITvI8lkRudkCitjQnH4FdnhMuKZgGnKkkvy/ShCfHYyb6BK6GDTrZ/nHHlsKgSfwHND6Zw5d7phXvgPRoVz3PEXk0sB/kApWUhLoBs7cuUy1I3zr3C0qG/x1XUNDdc5vliu6sQyE9IiqbPqXd0C3l8dnq8MncvKQnFwB0KXWfH37g0cq7lb6YAKQQH7KPjO6cYb0UcS4Aopm+8RTZXFP8QnTDm4KAyopK1ieuCTIQJy81V3Nni3blaa+XmBM9N87E1xruOMglIzJNpxZ2FhnlVTCgZMJ1imqnfjr3N/ae27yw==",
                    "SigningCertUrl": "https://sns.us-east-1.amazonaws.com/SimpleNotificationService-01d088a6f77103d0fe307c0069e40ed6.pem",
                    "UnsubscribeUrl": "https://sns.us-east-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-east-1:289485838881:hdmap-services-events-production:e53d9a4c-580c-4ddf-8a55-96a1f1894edb",
                    "MessageAttributes": {
                        "content_type": {
                            "Type": "String",
                            "Value": "application/json"
                        }
                    }
                }
            }
        ]}
    ]
        """

#  "Timestamp": "2023-07-27T19:59:24.551Z",




#import kronos.functions.ddb_to_s3_processor
import kronos.functions.event_sns_subscriber
from aws_lambda_powertools.utilities.typing import LambdaContext
from collections import namedtuple
import json
#import kronos.functions.jira_extractor

#print(kronos.functions.ddb_to_s3_processor.test())
#print(kronos.functions.event_sns_subscriber.test())
#print(kronos.functions.jira_extractor.test())

#"message": "<class 'awslambdaric.lambda_context.LambdaContext'>",
lambda_context =  {
    "level": "INFO",
    "location": "/var/task/log_adapter/adapters/powertools_adapter.py::info::38",
    "message": "LambdaContext([aws_request_id=c8b93f03-0a63-4c19-ac99-050a7a08bf0a,log_group_name=/aws/lambda/kronos-event-sns-subscriber-staging,log_stream_name=2023/07/27/[$LATEST]5e21a068a24d4fac871243bdf35185a2,function_name=kronos-event-sns-subscriber-staging,memory_limit_in_mb=256,function_version=$LATEST,invoked_function_arn=arn:aws:lambda:us-east-1:289485838881:function:kronos-event-sns-subscriber-staging,client_context=None,identity=CognitoIdentity([cognito_identity_id=None,cognito_identity_pool_id=None])])",
    "timestamp": "2023-07-27 19:59:25,309+0000",
    "service": "Kronos @ v1.0.0",
    "invoked_function_arn" : "arn",
    "cold_start": True,
    "memory_limit_in_mb": 0,
    "aws_request_id": "c8b93f03-0a63-4c19-ac99-050a7a08bf0a",
    "function_name": "kronos-event-sns-subscriber-staging",
    "function_memory_size": "256",
    "function_arn": "arn:aws:lambda:us-east-1:289485838881:function:kronos-event-sns-subscriber-staging",
    "function_request_id": "c8b93f03-0a63-4c19-ac99-050a7a08bf0a",
    "xray_trace_id": "1-64c2cc9c-77cfb6220a8ce42e5380c9db"
}



lambdaContext = namedtuple("LambdaContext", lambda_context.keys())(*lambda_context.values())

messageStop = """
{
    "event_source": "POSE_GRAPH_VALIDATOR_ARGO",
    "payload": {
        "dataset_region": "us-ca-los-angeles-santa-monica",
        "is_test_data": false,
        "has_colored_point_cloud": null,
        "service_progress_url": "https://argo.maps.motional.com/workflows/argo/pose-graph-validator-msqbr%5C",
        "dataset_session": "2023-07-27_19-54-09-GMT",
        "drivelog": null,
        "service_error_message": "child 'road-metrics-service-5qxdz-119701314' failed",
        "service_final_status": "FAILURE",
        "service_id": "POSE_GRAPH_VALIDATOR"
    },
    "hdmap_slackbot": {
        "extra_text": "",
        "do_skip_notification": null
    },
    "slack_message": {
        "text": null,
        "channel": null
    },
    "force_skip_subscribed_services": null,
    "event_id": "SERVICE_STOP"
}
"""

messageStart = """
{
    "event_source": "POSE_GRAPH_VALIDATOR_ARGO",
    "payload": {
        "service_id": "POSE_GRAPH_VALIDATOR",
        "is_test_data": false,
        "dataset_session": "2023-07-27_19-54-09-GMT",
        "drivelog": null,
        "has_colored_point_cloud": null,
        "service_progress_url": "https://argo.maps.motional.com/workflows/argo/pose-graph-validator-msqbr%5C",
        "dataset_region": "us-ca-los-angeles-santa-monica"
    },
    "hdmap_slackbot": {
        "do_skip_notification": null,
        "extra_text": ""
    },
    "slack_message": {
        "channel": null,
        "text": null
    },
    "event_id": "SERVICE_START"
}
"""
#print(event)
eventDict = json.loads(event)
#print(type(eventDict[0]))
#print(eventDict[0])

eventDict[0]["Records"][0]["Sns"]["Message"] = messageStop 
eventDict[0]["Records"][0]["Sns"]["Timestamp"] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')

# print(datetime.now())
# print(datetime.isoformat(datetime.now()))
# print(datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'))
#2023-07-27T19:59:24.551Z

#print(eventDict)
kronos.functions.event_sns_subscriber.lambda_handler(eventDict[0],lambdaContext)