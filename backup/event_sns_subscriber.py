from typing import Any, Dict
from aws_lambda_powertools.utilities.typing import LambdaContext
from ..utils import log_utils
from ..utils.log_utils import logger
from ..service.service_run_service import ServiceRunService
from ..domains import (
    base_domain_exceptions,
    location_url_factory_domain_exceptions,
    service_run_domain_exceptions
)
from aws_lambda_powertools.utilities.data_classes import SNSEvent

# Objects declared outside of the Lambda's handler method are part of Lambda's
# *execution environment*. This execution environment is sometimes reused for subsequent
# function invocations. Note that you can not assume that this always happens.
# Typical use case: database connection. The same connection can be re-used in some
# subsequent function invocations. It is recommended though to add logic to check if a
# connection already exists before creating a new one.
# The execution environment also provides 512 MB of *disk space* in the /tmp directory.
# Again, this can be re-used in some subsequent function invocations.
# See: https://docs.aws.amazon.com/lambda/latest/dg/runtimes-context.html#runtimes-lifecycle-shutdown

# The Lambda is configured with 3 retries. So do not raise an exception for
# non-retryable errors. Do print error logs in that case.
# For retryable errors do raise an Exception instead.

log_utils.configure()
inject_lambda_context = logger.get_adapter().logger.inject_lambda_context
#logger.info("KRONOS: LOADING EVENT-SNS-SUBSCRIBER")


def test():
    logger.info("in test()")
    return 'OK!'

@inject_lambda_context
def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> None:
    """
    Handler for the Lambda function (async). This function is the entry point.

    Args:
        event: an AWS event, eg. SNS Message with an inner ServiceStartEvent or ServiceStopEvent.
        context: the context passed to the Lambda.

    The `event` can be any incoming Lambda event, but we expect it to be an incoming
     SNSEvent with an inner ServiceStartEvent or ServiceStopEvent event similar to:
        {
            "Records": [
                {
                    "EventSource": "aws:sns",
                    "EventVersion": "1.0",
                    "EventSubscriptionArn": "arn:aws:sns:us-east-1:289485838881:hdmap-services-events-production:d8a5415a-6c61-4d3d-b5f4-061c63a1f16c",
                    "Sns": {
                        "Type": "Notification",
                        "MessageId": "510530f0-0808-5fd3-b55e-6bdd16457097",
                        "TopicArn": "arn:aws:sns:us-east-1:289485838881:hdmap-services-events-production",
                        "Subject": null,
                        "Message": "{\"event_source\": \"MAP_GPKG_EXPORTER_JENKINS\", \"payload\": {\"dataset_session\": \"2022-02-17_00-32-21-GMT\", \"drivelog\": \"2022.02.16.18.48.56-g1p-veh-2042\", \"dataset_region\": \"sg-one-north\", \"is_test_data\": false, \"service_id\": \"MAP_GPKG_EXPORTER\", \"service_progress_url\": \"http://www.google.com\"}, \"hdmap_slackbot\": {\"do_skip_notification\": true, \"extra_text\": null}, \"slack_message\": {\"text\": null, \"channel\": null}, \"event_id\": \"SERVICE_START\"}",
                        "Timestamp": "2022-06-22T13:41:33.726Z",
                        "SignatureVersion": "1",
                        "Signature": "O09RawLuz+vvxdxxkyKX4Ll0abfYryp15oE1IYtkSRITN7hVJJs8+wn7k2Aje85GJnQ8nWmW54eMvpjexKUtepHTL8tGuBl48ibV+G710H6SMvA5pAW4v17bsV3K7qNpIw0JUuqcKVuUeDoTrklvpmqN53+0o+NQn/7ajTP6qx9SPI5zqldVWFB3bT+JMewu5IRX+agcrZaqYPJQKOWIbL9nYefU+0kqXkY6noZSesj6MJ2oQI7Xc0oWYIspzgH0TnysTMl6GuKqvguiT/NpktDczoBHg70vyCRJlMfdaqdVmOzivakaqTk5TCXCDqCQ45y0ODb9qD6pcqjGj/7xUw==",
                        "SigningCertUrl": "https://sns.us-east-1.amazonaws.com/SimpleNotificationService-7ff5318490ec183fbaddaa2a969abfda.pem",
                        "UnsubscribeUrl": "https://sns.us-east-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-east-1:289485838881:hdmap-services-events-production:d8a5415a-6c61-4d3d-b5f4-061c63a1f16c",
                        "MessageAttributes": {
                            "content_type": {
                                "Type": "String",
                                "Value": "application/json"
                            }
                        }
                    }
                }
            ]
        }

    The `context` is a `LambdaContext` instance with properties similar to:
        {
            'aws_request_id': '75e62f43-062b-4b16-b877-e4662ea0ed32',
            'log_group_name': '/aws/lambda/lambda-s3',
            'log_stream_name': '2020/11/19/[$LATEST]071cab333b4c4a5b94ab0ae0a10c4b7c',
            'function_name': 'lambda-s3',
            'memory_limit_in_mb': '128',
            'function_version': '$LATEST',
            'invoked_function_arn': 'arn:aws:lambda:ap-southeast-1:477353422995:function:lambda-s3',
            'client_context': None,
            'identity': "<__main__.CognitoIdentity object at 0x7f8cbb404280>",
            '_epoch_deadline_time_in_ms': 1605769759863,
        }
    More info here: https://docs.aws.amazon.com/lambda/latest/dg/python-context.html
    """
    #logger.info("KRONOS: SERVICES EVENTS SUBSCRIBER: START")

    try:
   
        #print("Event")
        #print(event)
        sns_event = SNSEvent(event)
        service = ServiceRunService()
        service.process_sns_event(sns_event)
        
    except service_run_domain_exceptions.IncomingEventUnknown as exc:
        logger.exception("Unknown incoming event", extra=dict(event=event))
        return
    except service_run_domain_exceptions.DynamodbServiceRunCreateError as exc:
        logger.exception("Failed to create ServiceRun")
    except base_domain_exceptions.DynamodbRegionsSingletonUpdateError as exc:
        logger.exception(
            "Failed to update RegionsSingleton",
            extra=dict(region=exc.region),
        )
    except base_domain_exceptions.DynamodbAuthError as exc:
        logger.exception("DynamoDB authentication error")
    except service_run_domain_exceptions.DynamodbDatasetDoesNotExist as exc:
        logger.exception("Dataset does not exist in DB")
    except service_run_domain_exceptions.SnsAuthError as exc:
        logger.exception("SNS authentication error")
    except location_url_factory_domain_exceptions.LocationUrlNotFound as exc:
        logger.exception(f"Location url not found for: {exc.region} {exc.session}")
    except location_url_factory_domain_exceptions.LocationRequestError as exc:
        logger.exception("Error retrieving location url")
    except base_domain_exceptions.GenericBotoError as exc:
        logger.exception("Generic boto error, Lambda will retry")
        raise

    #logger.info("KRONOS: SERVICES EVENTS SUBSCRIBER: END")
