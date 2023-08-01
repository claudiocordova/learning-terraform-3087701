from datetime import datetime
from typing import Iterator, Optional, Union

from boto3.dynamodb.conditions import And, Attr, Key
from ksuid import KsuidMs
from mypy_boto3_dynamodb.type_defs import (
    GetItemOutputTableTypeDef,
    PutItemOutputTableTypeDef,
    TransactWriteItemTypeDef,
)
from ..data_models.base_model import ValidateEditableAttrsMixin, handle_auth_exceptions
from ..conf import settings
from ..utils import time_utils
from ..utils.boto3_utils import get_table_resource
from ..utils.dynamodb_utils import (
    dynamize,
    get_pagination_config,
    serialize_to_dynamodb,
)

from ..repository import service_run_repository 

from ..utils.log_utils import logger
from ..data_models import base_model_exceptions, region_singleton_model_exceptions
from ..data_models import service_run_model_exceptions as exceptions
from ..data_models.base_model import ValidateEditableAttrsMixin, handle_auth_exceptions
from ..data_models.dataset_model import DatasetFacet
from ..data_models.latest_service_run_model import LatestServiceRunFacet
from ..data_models.region_singleton_model import RegionSingletonFacet


class GsiServiceRunPerDrivelogConst:
    NAME = "GSIServiceRunPerDrivelog"
    PK_ATTR = "gsi_service_run_per_drivelog_pk_drivelog"
    IS_PK_NULLABLE = True
    PK_BOUND_ATTRS = ("drivelog",)
    SK_ATTR = "gsi_service_run_per_drivelog_sk_timestamp"
    IS_SK_NULLABLE = False
    SK_BOUND_ATTRS = ("timestamp",)
    PROJECTION_TYPE = "ALL"

class ServiceRun:

    ITEM_TYPE = "ServiceRun"

    ATTRIBUTES_MAP = dict(
        pk = "pk",
        sk = "sk",
        item_type = "item_type",         
        service_run_id = "service_run_id",
        service_run_try_number = "service_run_try_number",

        region = "region",
        session = "session",
        drivelog = "drivelog",
        snapshot_id = "snapshot_id",
        basemap_id = "basemap_id",

        tracking_activity_alias_id = "tracking_activity_alias_id",
        event_ksuid = "event_ksuid",
        service_id = "service_id",
        service_progress_url = "service_progress_url",
        is_test_data = "is_test_data",
        event_source = "event_source",
        hdmap_slackbot = "hdmap_slackbot",
        service_start_timestamp = "service_start_timestamp",
        service_stop_timestamp = "service_stop_timestamp",

        created_timestamp = "created_timestamp",
        updated_timestamp = "updated_timestamp",

        duration = "duration",
        slack_message = "slack_message",
        service_error_message = "service_error_message",
        service_status= "service_status",
        force_skip_subscribed_services = "force_skip_subscribed_services",
        has_colored_point_cloud = "has_colored_point_cloud",
        tracking_activity_id = "tracking_activity_id",



    )



    def __init__(
        self,
        pk: str,
        sk: str,
        item_type: str,         
        service_run_id: str,
        service_run_try_number: int,
        region: str,
        session: str,
        drivelog: str,
        snapshot_id: str,
        basemap_id: str,
        tracking_activity_alias_id: str,
        event_ksuid: str,
        service_id: str,
        service_progress_url: str,
        is_test_data: bool,
        event_source: str,
        hdmap_slackbot: dict,
        service_start_timestamp: datetime,
        service_stop_timestamp: datetime,
        created_timestamp: datetime,
        updated_timestamp: datetime,        
        duration: int,
        slack_message: dict,
        service_error_message: str,
        service_status: str,
        force_skip_subscribed_services: str,
        has_colored_point_cloud: str,
        tracking_activity_id: str
    ):
        # TODO add validation (marshmallow?).

        self.item_type = item_type         
        self.service_run_id = service_run_id
        self.service_run_try_number = service_run_try_number

        self.region = region
        self.session = session
        self.drivelog = drivelog
        self.snapshot_id = snapshot_id
        self.basemap_id = basemap_id

        self.tracking_activity_alias_id = tracking_activity_alias_id
        self.event_ksuid = event_ksuid
        self.service_id = service_id
        self.service_progress_url = service_progress_url
        self.is_test_data = is_test_data
        self.event_source = event_source
        self.hdmap_slackbot = hdmap_slackbot
        self.service_start_timestamp = service_start_timestamp
        self.service_stop_timestamp = service_stop_timestamp
        self.created_timestamp = created_timestamp
        self.updated_timestamp = updated_timestamp        
        self.duration = duration
        self.slack_message = slack_message
        self.service_error_message = service_error_message
        self.service_status= service_status
        self.force_skip_subscribed_services = force_skip_subscribed_services
        self.has_colored_point_cloud = has_colored_point_cloud
        self.tracking_activity_id = tracking_activity_id
        if pk == None:
            self.pk = self.create_pk()
        else:
            self.pk = pk
        if sk == None:
            self.sk = self.create_sk()
        else:
            self.sk = sk     

    def create_pk(self) -> str:
        
        if self.drivelog is not None:
            self.pk_type = 'DRIVELOG'
            return f"SERVICERUN#DRIVELOG#{self.drivelog}"
        elif self.region is not None and self.session is not None:
            self.pk_type = 'REGION|SESSION'
            return f"SERVICERUN#REGION|SESSION#{self.region}|{self.session}"
        elif self.service_progress_url is not None:
            self.pk_type = 'SERVICEPROGRESSURL'
            return f"SERVICERUN#SERVICEPROGRESSURL#{self.service_progress_url}"
        elif self.snapshot_id is not None and self.basemap_id is not None:
            self.pk_type = 'SNAPSHOTID|BASEMAPID'
            return f"SERVICERUN#SNAPSHOTID|BASEMAPID#{self.snapshot_id}|{self.basemap_id}"      

    
    def create_sk(self) -> str:
        return f"SERVICERUN#{self.event_ksuid}"

    
    def create_dynamo_expression_for_update_item(self) -> dict:

        expression = {
            "Key": {
                "pk": self.pk,
                "sk": self.sk
            },
            "UpdateExpression": """
                SET
                item_type = :item_type_val,
                service_run_id = :service_run_id_val,
                service_run_try_number = :service_run_try_number_val,    

                #region = :region_val,
                #session = :session_val,
                drivelog = :drivelog_val,
                snapshot_id = :snapshot_id_val,
                basemap_id = :basemap_id_val,

                tracking_activity_alias_id = :tracking_activity_alias_id_val,
                event_ksuid = :event_ksuid_val,
                service_id = :service_id_val,
                service_progress_url = :service_progress_url_val,
                is_test_data = :is_test_data_val,
                event_source = :event_source_val,
                hdmap_slackbot = :hdmap_slackbot_val,
                service_start_timestamp = :service_start_timestamp_val,
                service_stop_timestamp = :service_stop_timestamp_val,
                created_timestamp = :created_timestamp_val,
                updated_timestamp = :updated_timestamp_val,                
                #duration = :duration_val,
                slack_message = :slack_message_val,
                service_error_message = :service_error_message_val,
                service_status = :service_status_val,
                force_skip_subscribed_services = :force_skip_subscribed_services_val,
                has_colored_point_cloud = :has_colored_point_cloud_val,
                tracking_activity_id = :tracking_activity_id_val
                """
            ,
            "ExpressionAttributeNames" :{
                "#session": "session",
                "#region" : "region",
                "#duration": "duration"
            },
            "ExpressionAttributeValues" : {
                ':item_type_val':  self.item_type,
                ':service_run_id_val':  self.service_run_id,
                ':service_run_try_number_val':  self.service_run_try_number,    

                ':region_val':  self.region,
                ':session_val':  self.session,
                ':drivelog_val':  self.drivelog,
                ':snapshot_id_val':  self.snapshot_id,
                ':basemap_id_val':  self.basemap_id,


                ':tracking_activity_alias_id_val':  self.tracking_activity_alias_id,
                ':event_ksuid_val':  str(self.event_ksuid),
                ':service_id_val':  self.service_id,
                ':service_progress_url_val':  self.service_progress_url,
                ':is_test_data_val':  self.is_test_data,
                ':event_source_val':  self.event_source,
                ':hdmap_slackbot_val':  self.hdmap_slackbot,
                ':service_start_timestamp_val':  str(self.service_start_timestamp) if self.service_start_timestamp else None,
                ':service_stop_timestamp_val':  str(self.service_stop_timestamp) if self.service_stop_timestamp else None,
                ':created_timestamp_val':  str(self.created_timestamp) if self.created_timestamp else None,
                ':updated_timestamp_val':  str(self.updated_timestamp) if self.updated_timestamp else None,                
                ':duration_val':  self.duration,
                ':slack_message_val':  self.slack_message,
                ':service_error_message_val':  self.service_error_message,
                ':service_status_val':  self.service_status,
                ':force_skip_subscribed_services_val':  self.force_skip_subscribed_services,
                ':has_colored_point_cloud_val':  self.has_colored_point_cloud,
                ':tracking_activity_id_val':  self.tracking_activity_id
            },
            # Do not overwrite.
            #"ConditionExpression": Attr("PK").not_exists(),
            "ReturnValues": "NONE"
        }

        # Remove the None values.
        # for key, value in {**expression["Key"]}.items():
        #     if value is None:
        #         pass
                #del expression["Item"][key]

        return expression



    def create_dynamo_expression_for_put_item(self) -> dict:

        expression = {
            "Item": {
                "pk": self.pk,
                "sk": self.sk,
                self.dynamize2("item_type"): self.item_type,
                self.dynamize2("service_run_id"): self.service_run_id,
                self.dynamize2("service_run_try_number"): self.service_run_try_number,    

                self.dynamize2("region"): self.region,
                self.dynamize2("session"): self.session,
                self.dynamize2("drivelog"): self.drivelog,
                self.dynamize2("snapshot_id"): self.snapshot_id,
                self.dynamize2("basemap_id"): self.basemap_id,


                self.dynamize2("tracking_activity_alias_id"): self.tracking_activity_alias_id,
                self.dynamize2("event_ksuid"): str(self.event_ksuid),
                self.dynamize2("service_id"): self.service_id,
                self.dynamize2("service_progress_url"): self.service_progress_url,
                self.dynamize2("is_test_data"): self.is_test_data,
                self.dynamize2("event_source"): self.event_source,
                self.dynamize2("hdmap_slackbot"): self.hdmap_slackbot,
                self.dynamize2("service_start_timestamp"): str(self.service_start_timestamp) if self.service_start_timestamp else None,
                self.dynamize2("service_stop_timestamp"): str(self.service_stop_timestamp) if self.service_stop_timestamp else None,
                self.dynamize2("created_timestamp"): str(self.created_timestamp) if self.created_timestamp else None,
                self.dynamize2("updated_timestamp"): str(self.updated_timestamp) if self.updated_timestamp else None,                
                self.dynamize2("duration"): self.duration,
                self.dynamize2("slack_message"): self.slack_message,
                self.dynamize2("service_error_message"): self.service_error_message,
                self.dynamize2("service_status"): self.service_status,
                self.dynamize2(
                    "force_skip_subscribed_services"
                ): self.force_skip_subscribed_services,
                self.dynamize2("has_colored_point_cloud"): self.has_colored_point_cloud,
                self.dynamize2("tracking_activity_id"): self.tracking_activity_id,
            },
            # Do not overwrite.
            #"ConditionExpression": Attr("PK").not_exists(),
            "ReturnValues": "NONE",
        }

        # Remove the None values.
        for key, value in {**expression["Item"]}.items():
            if value is None:
                pass
                #del expression["Item"][key]

        return expression



    def dynamize2(self, text: str) -> str:
     return text


    # @property
    # def pk(self):
    #     return ServiceRunFacet.make_pk(self.region, self.session)

    # @property
    # def sk(self):
    #     return ServiceRunFacet.make_sk(self.service_id, self.event_ksuid)

    @classmethod
    def from_db(cls, data) -> "ServiceRun":
        if data.get("item_type") != ServiceRun.ITEM_TYPE:
            raise exceptions.NotAServiceRunItem
        item = cls(

            pk = data.get(cls.ATTRIBUTES_MAP["pk"]),
            sk = data.get(cls.ATTRIBUTES_MAP["sk"]),
            item_type = data.get(cls.ATTRIBUTES_MAP["item_type"]),
            service_run_id = data.get(cls.ATTRIBUTES_MAP["service_run_id"]),
            service_run_try_number = data.get(cls.ATTRIBUTES_MAP["service_run_try_number"]),

            region=data.get(cls.ATTRIBUTES_MAP["region"]), 
            session=data.get(cls.ATTRIBUTES_MAP["session"]),
            drivelog=data.get(cls.ATTRIBUTES_MAP["drivelog"]),
            snapshot_id = data.get(cls.ATTRIBUTES_MAP["snapshot_id"]),
            basemap_id = data.get(cls.ATTRIBUTES_MAP["basemap_id"]),

            tracking_activity_alias_id = data.get(cls.ATTRIBUTES_MAP["tracking_activity_alias_id"]),            
            event_ksuid=KsuidMs.from_base62(
                data.get(cls.ATTRIBUTES_MAP["event_ksuid"])
            ),
            service_id=data.get(cls.ATTRIBUTES_MAP["service_id"]),
            service_progress_url=data.get(
                cls.ATTRIBUTES_MAP["service_progress_url"]
            ),
            is_test_data=data.get(cls.ATTRIBUTES_MAP["is_test_data"]),            
            event_source=data.get(cls.ATTRIBUTES_MAP["event_source"]),
            hdmap_slackbot=data.get(cls.ATTRIBUTES_MAP["hdmap_slackbot"]),

            service_start_timestamp = data.get(cls.ATTRIBUTES_MAP["service_start_timestamp"]),
            service_stop_timestamp = data.get(cls.ATTRIBUTES_MAP["service_stop_timestamp"]),
            created_timestamp = data.get(cls.ATTRIBUTES_MAP["created_timestamp"]),
            updated_timestamp = data.get(cls.ATTRIBUTES_MAP["updated_timestamp"]),


            duration = data.get(cls.ATTRIBUTES_MAP["duration"]),

            # It's in the SNS message automatically added by AWS.
            #timestamp=datetime.fromisoformat(
            #    data.get(cls.ATTRIBUTES_MAP["timestamp"])
            #),

            slack_message=data.get(cls.ATTRIBUTES_MAP["slack_message"]),
            service_error_message=data.get(
                cls.ATTRIBUTES_MAP["service_error_message"]
            ),
            service_status=data.get(
                cls.ATTRIBUTES_MAP["service_status"]
            ),

            force_skip_subscribed_services=data.get(
                cls.ATTRIBUTES_MAP["force_skip_subscribed_services"]
            ),
            has_colored_point_cloud=data.get(
                cls.ATTRIBUTES_MAP["has_colored_point_cloud"]
            ),
            tracking_activity_id = data.get(cls.ATTRIBUTES_MAP["tracking_activity_id"]),
        )
        #item.item_type = data.get(cls.ATTRIBUTES_MAP["item_type"])

        return item

    # @property
    # def gsi_service_run_per_drivelog_pk_drivelog(self):
    #     # This GSI can be sparse (so None values will not be part of the index).
    #     if self.drivelog:
    #         return f"SERVICERUN#DRIVELOG#{self.drivelog}".upper()

    # @property
    # def gsi_service_run_per_drivelog_sk_timestamp(self):
    #     return serialize_to_dynamodb(self.timestamp)

    def to_dict(self):
        data = dict()
        #for attr in sorted(set(ServiceRunRepository.ATTRIBUTES_MAP.keys()) - {"item_type"}):
        for attr in sorted(set(self.ATTRIBUTES_MAP.keys())):    
            value = getattr(self, attr)
            # Parse dates to strings.
            if isinstance(value, datetime):
                value = value.isoformat()
            if isinstance(value, KsuidMs):
                value = str(value)
            data[attr] = value
        # TODO remove this when we write these timestamps in the right format.
        #  Note that in this specific case, this is necessary only in tests.
        for attr in ("service_start_timestamp","service_start_timestamp",):
            if data[attr] and not data[attr].endswith("+00:00"):
                data[attr] += "+00:00"
        return data


