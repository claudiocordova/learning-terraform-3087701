import json
from datetime import datetime
from typing import Any, Dict, Optional, Union, Iterator


from boto3.dynamodb.conditions import And, Attr, Key
from ..conf import settings
from botocore import exceptions as botocore_exceptions

from events.hdmap_services_events import ServiceStartEvent, ServiceStopEvent
from events.hdmap_services_events import exceptions as hdmap_services_events_exceptions
from events.hdmap_services_events.hdmap_services_event_base import (
    ServiceFinalStatus,
    ServiceId,
)
from ..entity.service_run import ServiceRun
from ..data_models.base_model import ValidateEditableAttrsMixin, handle_auth_exceptions
from ..conf import settings
from ..data_models import (
    base_model_exceptions,
    region_singleton_model_exceptions,
    service_run_model_exceptions,
)

from ..utils.dynamodb_utils import (
    dynamize,
    get_pagination_config,
    serialize_to_dynamodb,
)

from ..data_models.dataset_model import (
    REQUIRED_HDMAP_SERVICE_IDS,
    DatasetFacet,
    ServicesStatusEnum,
)
from ..data_models.latest_service_run_model import LatestServiceRunFacet
from ..data_models.slack_notification_drivelogs_singleton_model import (
    SlackNotificationDrivelogsSingletonFacet,
)
from ..utils import dataset_utils
from ..utils.boto3_utils import get_sns_client
from ..utils.dataset_utils_exceptions import InvalidRegionName, InvalidSessionName
from ..utils.log_utils import logger
from ..domains import base_domain_exceptions
from ..domains import service_run_domain_exceptions as exceptions
from ..domains.location_url_factory_domain import LocationUrlFactory

from mypy_boto3_dynamodb.type_defs import (
    GetItemOutputTableTypeDef,
    PutItemOutputTableTypeDef,
    TransactWriteItemTypeDef,
)
from ..utils.boto3_utils import get_table_resource




class ServiceRunRepository:


    

    # ALL_INDEXES: set = {
    #     GsiServiceRunPerDrivelogConst,
    # }



    # READ_ONLY_ATTRIBUTES: set = {
    #     "pk",
    #     "sk",
    #     "item_type",
    #     "region",
    #     "session",
    #     "event_ksuid",
    # }
    # EDITABLE_ATTRIBUTES: set = set(ATTRIBUTES_MAP.keys()) - set(READ_ONLY_ATTRIBUTES)

    def __init__(self):
        pass




    def __init__(self):
        pass
        
    def create_service_run(self, ServiceRun):
        pass
        
    def delete_service_run(self, ServiceRun):
        pass 

    #def find_service_run_by_pk(self, pk) -> list:
    @handle_auth_exceptions
    def find_service_runs_by_pk_service_id(self, pk, service_id) -> Iterator[ServiceRun]:

        paginator = get_table_resource().meta.client.get_paginator("query")
        response_iterator = paginator.paginate(
            TableName=settings.DYNAMODB_TABLE_NAME,
            Select="ALL_ATTRIBUTES",
            KeyConditionExpression=And(
                Key("pk").eq(pk), Key("sk").begins_with("SERVICERUN#"  )
            ),
            FilterExpression=And(Attr("service_id").eq(service_id), Attr("item_type").eq("ServiceRun")),
            ScanIndexForward=False,  # Reverse sorting.
            PaginationConfig=get_pagination_config(do_read_all_items=True),
        )

        for response in response_iterator:
            logger.debug("Response", extra=dict(response=response))
            if not response.get("Items"):
                continue
            for item in response.get("Items"):
                print(item) 
                yield ServiceRun.from_db(item)



    @handle_auth_exceptions
    def upsert_service_run(
        self,
        service_run: ServiceRun,
        **attrs_to_create,
    ) -> ServiceRun:

        try:
            dynamo_expression = service_run.create_dynamo_expression_for_update_item()
            print("expression")
            print(json.dumps(dynamo_expression,sort_keys=True, indent=4)) 

            # Docs: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Table.put_item
            response: PutItemOutputTableTypeDef = get_table_resource().update_item(
                 **dynamo_expression
            )
        except get_table_resource().meta.client.exceptions.ConditionalCheckFailedException as exc:
            raise base_model_exceptions.PrimaryKeyConstraintError(service_run) from exc


        return service_run

    # @handle_auth_exceptions
    # def read(self, service_id: str, event_ksuid: Union[str, KsuidMs]) -> ServiceRunItem:
    #     pk = self.make_pk(self.region, self.session)
    #     sk = self.make_sk(service_id, event_ksuid)
    #     # Docs: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Table.put_item
    #     response: GetItemOutputTableTypeDef = get_table_resource().get_item(
    #         Key={"PK": pk, "SK": sk}
    #     )

    #     logger.debug("Response", extra=dict(response=response))
    #     if not response.get("Item"):
    #         raise base_model_exceptions.ItemNotFound

    #     item = ServiceRunItem.from_db(response["Item"])
    #     return item

    # @handle_auth_exceptions
    # def read_all_for_region_and_session_and_service_id(
    #     self,
    #     service_id: str,
    #     do_read_all_items=False,
    # ) -> Iterator[ServiceRunItem]:
    #     pk = self.make_pk(self.region, self.session)
    #     sk = self.make_sk(service_id, "")
    #     # Docs: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Paginator.Query
    #     pagination_config = get_pagination_config(do_read_all_items=do_read_all_items)
    #     paginator = get_table_resource().meta.client.get_paginator("query")
    #     response_iterator = paginator.paginate(
    #         TableName=settings.DYNAMODB_TABLE_NAME,
    #         Select="ALL_ATTRIBUTES",
    #         KeyConditionExpression=And(Key("PK").eq(pk), Key("SK").begins_with(sk)),
    #         ScanIndexForward=False,  # Reverse sorting.
    #         PaginationConfig=pagination_config,
    #     )

    #     for response in response_iterator:
    #         logger.debug("Response", extra=dict(response=response))
    #         if not response.get("Items"):
    #             continue
    #         for item in response.get("Items"):
    #             yield ServiceRunItem.from_db(item)

    # # TODO BAS-2515 test this.
    # @handle_auth_exceptions
    # def read_all_for_region_and_session(self) -> Iterator[ServiceRunItem]:
    #     pk = self.make_pk(self.region, self.session)
    #     # Docs: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Paginator.Query
    #     paginator = get_table_resource().meta.client.get_paginator("query")
    #     response_iterator = paginator.paginate(
    #         TableName=settings.DYNAMODB_TABLE_NAME,
    #         Select="ALL_ATTRIBUTES",
    #         KeyConditionExpression=And(
    #             Key("PK").eq(pk), Key("SK").begins_with("SERVICE#")
    #         ),
    #         ScanIndexForward=False,  # Reverse sorting.
    #         PaginationConfig=get_pagination_config(do_read_all_items=True),
    #     )

    #     for response in response_iterator:
    #         logger.debug("Response", extra=dict(response=response))
    #         if not response.get("Items"):
    #             continue
    #         for item in response.get("Items"):
    #             yield ServiceRunItem.from_db(item)

    # @staticmethod
    # @handle_auth_exceptions
    # def read_all_for_drivelog(
    #     drivelog: str,
    #     do_read_all_items=False,
    # ) -> Iterator[ServiceRunItem]:
    #     # Docs: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Paginator.Query
    #     pagination_config = get_pagination_config(do_read_all_items=do_read_all_items)
    #     paginator = get_table_resource().meta.client.get_paginator("query")
    #     response_iterator = paginator.paginate(
    #         TableName=settings.DYNAMODB_TABLE_NAME,
    #         IndexName=GsiServiceRunPerDrivelogConst.NAME,
    #         Select="ALL_ATTRIBUTES",
    #         KeyConditionExpression=Key(
    #             dynamize(GsiServiceRunPerDrivelogConst.PK_ATTR)
    #         ).eq(f"SERVICERUN#DRIVELOG#{drivelog}".upper()),
    #         ScanIndexForward=False,  # Reverse sorting.
    #         PaginationConfig=pagination_config,
    #     )

    #     for response in response_iterator:
    #         logger.debug("Response", extra=dict(response=response))
    #         if not response.get("Items"):
    #             continue
    #         for item in response.get("Items"):
    #             yield ServiceRunItem.from_db(item)





    def update_dataset_services_status(self):
        services_status = self._compute_dataset_services_status()
        try:
            DatasetFacet(
                self.hdmap_service_event.dataset_region,
                self.hdmap_service_event.dataset_session,
            ).update(services_status=services_status)
        except base_model_exceptions.AuthError as exc:
            raise base_domain_exceptions.DynamodbAuthError from exc
        except botocore_exceptions.ClientError as exc:
            raise base_domain_exceptions.GenericBotoError from exc
        except base_model_exceptions.ItemNotFound as exc:
            raise exceptions.DynamodbDatasetDoesNotExist from exc

        if services_status == ServicesStatusEnum.SUCCESS.value:
            self._publish_sns_event()

    def _publish_sns_event(self) -> None:
        dataset_item = DatasetFacet(
            self.hdmap_service_event.dataset_region,
            self.hdmap_service_event.dataset_session,
        ).read()
        slack_notification_drivelogs_singleton = (
            SlackNotificationDrivelogsSingletonFacet()
        )
        if (
            dataset_item.do_send_slack_notification_on_service_status_success
            or slack_notification_drivelogs_singleton.contains_drivelog(
                dataset_item.drivelog
            )
        ):
            message_dict = dict(
                dataset_region=dataset_item.region,
                dataset_session=dataset_item.session,
                location_url=LocationUrlFactory(
                    region=dataset_item.region,
                    session=dataset_item.session,
                ).make_location_url(),
                mundi_url=settings.API_GATEWAY_HOST
                + f"/dataset/{dataset_item.region}+{dataset_item.session}",
            )
            if dataset_item.drivelog:
                message_dict.update(
                    dict(
                        drivelog_or_operation_type=dataset_item.drivelog,
                        drivelog_url=f"https://drivelogs.data.motional.com/log/{dataset_item.drivelog}",
                    )
                )
            else:
                message_dict.update(
                    dict(
                        drivelog_or_operation_type=dataset_item.operation_type,
                        drivelog_url=None,
                    )
                )

            sns_client = get_sns_client()
            try:
                sns_client.publish(
                    TopicArn=settings.MUNDI_EVENTS_SNS_TOPIC_ARN,
                    Message=json.dumps(message_dict),
                )
            except sns_client.exceptions.AuthorizationErrorException as exc:
                raise exceptions.SnsAuthError from exc

    def are_region_and_session_names_valid(self) -> bool:
        # If the region name or the session name is invalid, it means that this will
        #  never be a dataset (because map-cli will forbid it), so skip the creation of
        #  LatestServiceRun and Dataset and RegionSingleton.
        try:
            dataset_utils.validate_region_name(self.hdmap_service_event.dataset_region)
            dataset_utils.validate_session_name(
                self.hdmap_service_event.dataset_session
            )
        except InvalidRegionName as exc:
            logger.warning("Invalid region name", extra=dict(invalid_name=exc.name))
            return False
        except InvalidSessionName as exc:
            logger.warning("Invalid session name", extra=dict(invalid_name=exc.name))
            return False
        return True

    def _compute_dataset_services_status(self) -> Optional[str]:
        # Collect all required HDMap Service ids and their event_id.
        statuses = list()
        lsr_facet = LatestServiceRunFacet(
            self.hdmap_service_event.dataset_region,
            self.hdmap_service_event.dataset_session,
        )
        try:
            for item in lsr_facet.read_all_for_region_and_session():
                if item.service_id not in REQUIRED_HDMAP_SERVICE_IDS:
                    continue
                statuses.append(item.service_final_status)
        except base_model_exceptions.AuthError as exc:
            raise base_domain_exceptions.DynamodbAuthError from exc
        except botocore_exceptions.ClientError as exc:
            raise base_domain_exceptions.GenericBotoError from exc

        # A. Zero LatestServiceRun: Dataset.services_status = NONE
        if not statuses:
            result = None
            return result

        # B. *At least one* required HDMap service_id.
        result = ServicesStatusEnum.SOME_REQUIRED_STARTED.value

        # C. *All required* HDMap service_id.
        if len(statuses) >= len(REQUIRED_HDMAP_SERVICE_IDS):
            result = ServicesStatusEnum.ALL_REQUIRED_STARTED.value

        is_at_least_one_running = False
        for status in statuses:
            if status is None:
                is_at_least_one_running = True
            # D. At least one required HDMap service_id in *error* state.
            if status and status != ServiceFinalStatus.SUCCESS.value:
                result = ServicesStatusEnum.ERROR.value
                return result

        # E. All required HDMap service_id in *success* state.
        if (
            result == ServicesStatusEnum.ALL_REQUIRED_STARTED.value
            and not is_at_least_one_running
        ):
            result = ServicesStatusEnum.SUCCESS.value
        return result


    def _parse_hdmap_service_event_single_record(self) -> "ServiceStopEvent":
        # Try to make a service START event. If it fails validation then try to make
        #  a service STOP event.
        try:
            return ServiceStartEvent.make_from_raw_event_json(
                self.sns_event.sns_message
            )
        except hdmap_services_events_exceptions.ValidationError:
            pass


        raise exceptions.IncomingEventUnknown(sns_event=self.sns_event)



    def _parse_hdmap_service_event(self) -> Union[ServiceStartEvent, ServiceStopEvent]:
        # Try to make a service START event. If it fails validation then try to make
        #  a service STOP event.
        try:
            return ServiceStartEvent.make_from_raw_event_json(
                self.sns_event.sns_message
            )
        except hdmap_services_events_exceptions.ValidationError:
            pass

        try:
            return ServiceStopEvent.make_from_raw_event_json(self.sns_event.sns_message)
        except hdmap_services_events_exceptions.ValidationError:
            pass

        raise exceptions.IncomingEventUnknown(sns_event=self.sns_event)

    def _parse_timestamp(self) -> Optional[datetime]:
        # The timestamp is in: ["Records"][0]["Sns"]["Timestamp"]
        try:
            # Eg. "2022-06-22T13:41:33.726Z".
            timestamp_string: str = self.sns_event.record.sns.timestamp
            timestamp: Optional[datetime] = datetime.fromisoformat(
                timestamp_string.replace("Z", "+00:00")
            )
        except (KeyError, IndexError, ValueError) as exc:
            logger.exception("Failed to parse timestamp, setting it to None")
            timestamp = None
        return timestamp
