import json
from datetime import datetime
from typing import Any, Dict, Optional, Union
from decimal import Decimal

from botocore import exceptions as botocore_exceptions
from ksuid import KsuidMs
from ..utils import time_utils
from events.hdmap_services_events import ServiceStartEvent, ServiceStopEvent
from events.hdmap_services_events import exceptions as hdmap_services_events_exceptions
from events.hdmap_services_events.hdmap_services_event_base import (
    ServiceFinalStatus,
    ServiceId,
    EventId
)

from ..conf import settings
from ..data_models import (
    base_model_exceptions,
    region_singleton_model_exceptions,
    service_run_model_exceptions,
)
from ..data_models.dataset_model import (
    REQUIRED_HDMAP_SERVICE_IDS,
    DatasetFacet,
    ServicesStatusEnum,
)

from ..repository.service_run_repository import ServiceRunRepository
from ..entity.service_run import ServiceRun
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




class ServiceRunService:


    def process_sns_event(self, sns_event: Dict[str, Any], **extra_attrs):

        respository = ServiceRunRepository()
        hdmap_service_event = self._parse_hdmap_service_event(sns_event)

        print("process_sns_event: " + str(type(hdmap_service_event)))
        print("process_sns_event: " + str(hdmap_service_event))  
        
        service_run = self._create_service_run_entity(hdmap_service_event, sns_event)

        print("created service_run")
        print(json.dumps(service_run.to_dict(),sort_keys=True, indent=4))    

        if type(hdmap_service_event) == ServiceStartEvent:
            service_run.service_status = 'STARTED'




            
        elif type(hdmap_service_event) == ServiceStopEvent:
            service_runs = [found_service_run for found_service_run in respository.find_service_runs_by_pk_service_id(service_run.pk, service_run.service_id)]
            found_start_service_run = None
            for found_service_run in service_runs:
                if found_service_run.service_stop_timestamp is None:
                    found_start_service_run = found_service_run
            if found_start_service_run != None:        
                #Merge Start and Stop        
                service_run.sk = found_start_service_run.sk
                service_run.service_run_id = found_start_service_run.service_run_id
                service_run.service_start_timestamp = found_start_service_run.service_start_timestamp
                service_run.created_timestamp = found_start_service_run.created_timestamp
                service_run.updated_timestamp = datetime.isoformat(datetime.now())
                start_timestamp = datetime.fromisoformat(service_run.service_start_timestamp)
                stop_timestamp = datetime.fromisoformat(service_run.service_stop_timestamp)

                time_delta =  stop_timestamp - start_timestamp
                duration_seconds = time_delta.total_seconds() 
                service_run.duration = round(duration_seconds)




        try:
      
            respository.upsert_service_run(service_run)
        except (
            base_model_exceptions.ReadOnlyAttribute,
            base_model_exceptions.UnknownAttribute,
            base_model_exceptions.PrimaryKeyConstraintError,
            service_run_model_exceptions.TimestampMissing,
        ) as exc:
            raise exceptions.DynamodbServiceRunCreateError from exc
        except base_model_exceptions.AuthError as exc:
            raise base_domain_exceptions.DynamodbAuthError from exc
        except region_singleton_model_exceptions.RegionSingletonRegionsAttrNotAStringSet as exc:
            raise base_domain_exceptions.DynamodbRegionsSingletonUpdateError(
                hdmap_service_event.dataset_region
            ) from exc


    def _create_service_run_entity(self, hdmap_service_event, sns_event) -> ServiceRun:
        # Note that extra_attrs is used in tests to override the default attrs in order to test for exceptions.
        timestamp = self._parse_timestamp(sns_event)

        serviceStartTimestamp = None
        serviceStopTimestamp = None
        
        print(hdmap_service_event.event_id+ " "+str(timestamp)+ " "+ str(EventId.SERVICE_START.value))

        if hdmap_service_event.event_id == EventId.SERVICE_START.value:
            serviceStartTimestamp = datetime.isoformat(timestamp)
        elif hdmap_service_event.event_id == EventId.SERVICE_STOP.value:
            serviceStopTimestamp = datetime.isoformat(timestamp)   

        eventKsuid = KsuidMs(time_utils.now())

        params = dict(
            pk = None,
            sk = None,    
            item_type = ServiceRun.ITEM_TYPE,            
            service_run_id = 'SERVICERUN#'+str(eventKsuid),
            service_run_try_number = 1,

            # Possible Ids
            region = hdmap_service_event.dataset_region,
            session = hdmap_service_event.dataset_session,
            drivelog = hdmap_service_event.drivelog,
            snapshot_id = None,
            basemap_id = None,

            tracking_activity_alias_id = None,
            event_ksuid = eventKsuid, 
            service_id = hdmap_service_event.service_id,
            service_progress_url = hdmap_service_event.service_progress_url,
            is_test_data = hdmap_service_event.is_test_data,
            event_source = hdmap_service_event.event_source,
            hdmap_slackbot = hdmap_service_event.hdmap_slackbot,
            service_start_timestamp = serviceStartTimestamp,
            service_stop_timestamp = serviceStopTimestamp,
            created_timestamp = datetime.isoformat(datetime.now()),
            updated_timestamp = datetime.isoformat(datetime.now()),            
            duration = 0,
            slack_message = hdmap_service_event.slack_message,
            service_error_message=getattr(
                hdmap_service_event, "service_error_message", None
            ),
            service_status=getattr(
                hdmap_service_event, "service_final_status", None
            ),
            force_skip_subscribed_services=getattr(
                hdmap_service_event, "force_skip_subscribed_services", None
            ),
            has_colored_point_cloud = hdmap_service_event.has_colored_point_cloud,
            tracking_activity_id = 'ORPHAN',
        )
        
        
        #params.update(extra_attrs)
        serviceRun = ServiceRun( **params)
        return serviceRun
    


    def _parse_hdmap_service_event(self,sns_event) -> Union[ServiceStartEvent, ServiceStopEvent]:
        # Try to make a service START event. If it fails validation then try to make
        #  a service STOP event.
        try:
            return ServiceStartEvent.make_from_raw_event_json(
                sns_event.sns_message
            )
        except hdmap_services_events_exceptions.ValidationError:
            pass

        try:
            return ServiceStopEvent.make_from_raw_event_json(sns_event.sns_message)
        except hdmap_services_events_exceptions.ValidationError:
            pass

        raise exceptions.IncomingEventUnknown(sns_event=sns_event)

    def _parse_timestamp(self,sns_event) -> Optional[datetime]:
        # The timestamp is in: ["Records"][0]["Sns"]["Timestamp"]
        try:
            # Eg. "2022-06-22T13:41:33.726Z".
            timestamp_string: str = sns_event.record.sns.timestamp
            timestamp: Optional[datetime] = datetime.fromisoformat(
                #timestamp_string.replace("Z", "+00:00")
                timestamp_string.replace("Z", "")
            )
        except (KeyError, IndexError, ValueError) as exc:
            logger.exception("Failed to parse timestamp, setting it to None")
            timestamp = None
        return timestamp















    # def are_region_and_session_names_valid(self) -> bool:
    #     # If the region name or the session name is invalid, it means that this will
    #     #  never be a dataset (because map-cli will forbid it), so skip the creation of
    #     #  LatestServiceRun and Dataset and RegionSingleton.
    #     try:
    #         dataset_utils.validate_region_name(self.hdmap_service_event.dataset_region)
    #         dataset_utils.validate_session_name(
    #             self.hdmap_service_event.dataset_session
    #         )
    #     except InvalidRegionName as exc:
    #         logger.warning("Invalid region name", extra=dict(invalid_name=exc.name))
    #         return False
    #     except InvalidSessionName as exc:
    #         logger.warning("Invalid session name", extra=dict(invalid_name=exc.name))
    #         return False
    #     return True
    

    







   
