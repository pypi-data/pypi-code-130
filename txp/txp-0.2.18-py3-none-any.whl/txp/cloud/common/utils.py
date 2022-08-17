import numpy as np
import google.cloud.firestore as firestore
from txp.cloud.common.config import settings
from typing import List, Optional
import logging
from enum import Enum
from datetime import datetime, timedelta, timezone
import json
from txp.common.ml.models import ModelStateValue, ModelRegistry
from txp.common.ml.tasks import AssetTask

configurations_collection_name = settings.firestore.configurations_collection
tenants_collection_name = settings.firestore.tenants_collection
configuration_reference_field_path = "configuration_ref"
configuration_id_field = "configuration_id"
log = logging.getLogger(__name__)
edges_collection_name = settings.firestore.edges_collection
machines_collection_name = settings.firestore.machines_collection


class SignalMode(Enum):
    TIME = 0
    TIME_FFT = 1
    TIME_PSD = 2
    TIME_FFT_PSD = 3
    FFT = 4
    FFT_PSD = 5
    PSD = 6
    IMAGE = 7

    @staticmethod
    def is_image(mode):
        return mode == SignalMode.IMAGE.value

    @staticmethod
    def is_time_only(mode):
        return not SignalMode.is_fft(mode) and not SignalMode.is_psd(mode)

    @staticmethod
    def is_time(mode):
        return mode in [SignalMode.TIME.value, SignalMode.TIME_FFT.value, SignalMode.TIME_FFT_PSD.value,
                        SignalMode.TIME_PSD.value,
                        SignalMode.IMAGE.value]

    @staticmethod
    def is_fft(mode):
        return mode in [SignalMode.TIME_FFT.value, SignalMode.TIME_FFT_PSD.value, SignalMode.FFT.value,
                        SignalMode.FFT_PSD.value]

    @staticmethod
    def is_psd(mode):
        return mode in [SignalMode.TIME_PSD.value, SignalMode.TIME_FFT_PSD.value, SignalMode.PSD.value,
                        SignalMode.FFT_PSD.value]


def insert_ml_model(db: firestore.Client, model_registry, model_registry_name, collection_name):
    db.collection(collection_name).document(model_registry.metadata.tenant_id). \
        collection(model_registry.metadata.machine_id).document(model_registry.metadata.task_id).collection("models"). \
        document(model_registry_name).set(json.loads(model_registry.json()))


def get_model_registry_doc_ref(db: firestore.Client, tenant_id, machine_id, task_id, model_registry_name,
                               collection_name):
    return db.collection(collection_name).document(tenant_id).collection(machine_id). \
        document(task_id).collection("models").document(model_registry_name)


def set_ml_model_feedback_and_status(db: firestore.Client, tenant_id, machine_id, task_id, model_registry_name,
                                     model_feedback, status, collection_name):
    doc_ref = get_model_registry_doc_ref(db, tenant_id, machine_id, task_id, model_registry_name, collection_name)
    if not doc_ref.get().exists:
        return False
    doc_ref.update({
        "state.value": status,
        "metadata.feedback": json.loads(model_feedback.json())
    })
    return True


def set_error_ml_model(db: firestore.Client, tenant_id, machine_id, task_id, model_registry_name, model_feedback,
                       collection_name):
    return set_ml_model_feedback_and_status(db, tenant_id, machine_id, task_id, model_registry_name, model_feedback,
                                            ModelStateValue.ERROR.value, collection_name)


def acknowledge_ml_model(db: firestore.Client, tenant_id, machine_id, task_id, model_registry_name, model_feedback,
                         collection_name):
    return set_ml_model_feedback_and_status(db, tenant_id, machine_id, task_id, model_registry_name, model_feedback,
                                            ModelStateValue.ACKNOWLEDGE.value, collection_name)


def get_ml_model(db: firestore.Client, tenant_id, machine_id, task_id, model_registry_name, collection_name) -> \
        ModelRegistry:
    doc_ref = get_model_registry_doc_ref(db, tenant_id, machine_id, task_id, model_registry_name, collection_name).get()

    if not doc_ref.exists:
        return None
    try:
        return ModelRegistry(**doc_ref.to_dict())
    except Exception as e:
        log.error(f"Error trying to create ModelRegistry instance based on dict: {e}")
        return None


def publish_ml_model(db: firestore.Client, tenant_id, machine_id, task_id, model_registry_name, collection_name):
    doc_ref = get_model_registry_doc_ref(db, tenant_id, machine_id, task_id, model_registry_name, collection_name)
    if not doc_ref.get().exists or doc_ref.get().to_dict()['state']['value'] == ModelStateValue.ACTIVE.value:
        return False
    doc_ref.update({
        "state.publishment_date": get_current_utc_datetime_str(),
        "state.deprecation_date": "",
        "state.value": ModelStateValue.ACTIVE.value
    })
    return True


def deprecate_active_ml_model(db: firestore.Client, tenant_id, machine_id, task_id,
                              collection_name):
    documents = db.collection(collection_name).document(tenant_id).collection(machine_id). \
        document(task_id).collection("models"). \
        where("state.value", "==", ModelStateValue.ACTIVE.value).get()

    if not documents:
        return None
    doc = documents[0]
    doc_ref = doc.reference
    doc_ref.update({
        "state.deprecation_date": get_current_utc_datetime_str(),
        "state.value": ModelStateValue.OLD.value
    })
    return doc.to_dict()


def get_all_model_registries(db: firestore.Client, tenant_id, machine_id, task_id, collection_name):
    documents = db.collection(collection_name).document(tenant_id).collection(machine_id). \
        document(task_id).collection("models").get()
    models = []
    for doc in documents:
        models.append(doc.to_dict())
    return models


def get_sampling_frequency(signal, client):
    configuration = pull_configuration_from_firestore(client, signal["configuration_id"], signal["tenant_id"])
    documents = client.collection(edges_collection_name). \
        where(configuration_reference_field_path, "==", configuration.reference). \
        where("logical_id", "==", signal["edge_logical_id"]).get()
    if len(documents) != 1:
        return 1
    edge_document = documents[0]
    return edge_document.get("is_of_kind_ref").get().get("perceptions")[signal["perception_name"]]["sampling_frequency"]


def from_proto_to_json(proto):
    timestamp, index = proto.metadata.package_id.split("_")
    timestamp = int(timestamp)
    index = int(index)
    prev_index = proto.metadata.previous_part_index
    res = []
    for signal in proto.signals:
        row = {
            "data": [],
            "package_timestamp": timestamp,
            "signal_timestamp": signal.timestamp,
            "previous_part_index": prev_index,
            "part_index": index,
            "perception_name": signal.perception_name,
            "edge_logical_id": proto.metadata.edge_descriptor.logical_id,
            "configuration_id": proto.configuration_id,
            "label": "{'label_value': "", 'parameters':{}}",
            "observation_timestamp": proto.metadata.sampling_window.observation_timestamp,
            "gateway_task_id": proto.metadata.sampling_window.gateway_task_id,
            "sampling_window_index": proto.metadata.sampling_window.sampling_window_index,
            "number_of_sampling_windows": proto.metadata.sampling_window.number_of_sampling_windows,
            "tenant_id": proto.metadata.tenant_id
        }
        row["partition_timestamp"] = str(get_partition_utc_date(row["observation_timestamp"]))
        for i, dimension_signal_sample in enumerate(signal.samples):
            row["data"].append({
                "values": list(dimension_signal_sample.samples),
                "index": i
            })
            i += 1
        res.append(row)
    return res


def get_gcs_dataset_prefix(dataset_name, dataset_versions):
    dataset_versions.sort()
    suffix = ""
    for i, tag in enumerate(dataset_versions):
        suffix += tag
        if i + 1 < len(dataset_versions):
            suffix += "_"
    return f"{dataset_name}_{suffix}"


def get_gcs_task_bucket_path(tenant_id, machine_id, task_id):
    return f"{tenant_id}/{machine_id}/{task_id}"


def get_gcs_dataset_file_name(task_path, dataset_name, table, dataset_versions):
    return f"{task_path}/{get_gcs_dataset_prefix(dataset_name, dataset_versions)}/{table}.gzip"


def get_current_utc_datetime_str():
    return datetime.now(timezone.utc).strftime(settings.time.start_date_timezone_format)


def get_gcs_model_file_name(dataset_name, dataset_versions):
    return f"{get_gcs_dataset_prefix(dataset_name, dataset_versions)}.joblib"


def get_partition_utc_date(observation_timestamp):
    partition_timestamp = datetime.utcfromtimestamp(observation_timestamp // 1e9)
    partition_timestamp = partition_timestamp - timedelta(minutes=partition_timestamp.minute,
                                                          seconds=partition_timestamp.second)
    return partition_timestamp


def merge_signal_chunks(signal_chunks):
    """Merges all signal chunks for a given signal row.

    Args:
        signal_chunks: chunks of a signal, the signal is split in chunks due to MQTT maximum size per package

    Return:
        merged element.
    """

    signal_chunks = sorted(signal_chunks, key=lambda d: d['part_index'])
    data = []
    for i in range(len(signal_chunks[0]["data"])):
        data.append([])
    for i in range(0, len(signal_chunks)):
        for j, dimension_signal_sample in enumerate(signal_chunks[i]["data"]):
            data[j] = np.concatenate((data[j], dimension_signal_sample["values"]), axis=0)
            data[j] = list(data[j])
    signal_chunks[0]["data"] = [{"values": dimension, "index": i} for i, dimension in enumerate(data)]
    signal_chunks[0]["previous_part_index"] = 0
    return signal_chunks[0]


def get_fft_as_np_array(bigquery_fft):
    fft_per_dimensions = []
    for dimension in bigquery_fft:
        fft_dimension = []
        for z in dimension["values"]:
            fft_dimension.append(np.complex128(complex(z["real"], z["imag"])))
        fft_per_dimensions.append(np.array(fft_dimension))

    return np.array(fft_per_dimensions)


def pull_tenant_doc(db: firestore.Client, tenant_id: str) -> Optional[firestore.DocumentSnapshot]:
    """Pull the tenant document from the Firestore database, given
    the tenant_id value"""
    tenant_doc = db.collection(tenants_collection_name).where(
        "tenant_id", "==", tenant_id
    ).get()

    if not tenant_doc:
        log.warning(f"Tenant Document with tenant_id: {tenant_id} not found.")
        return None

    return tenant_doc[0]


def pull_current_configuration_from_firestore(
        db: firestore.Client,
        tenant_id: str
) -> firestore.DocumentSnapshot:
    """Pull down from the Firestore DB the most recent configuration document.

    Args:
        db: The instance of a Firestore authenticated client.
        tenant_id (str): The tenant_id value to download the current configuration.

    Returns:
        The configuration firestore.DocumentReference.
    """
    tenant_doc: firestore.DocumentSnapshot = pull_tenant_doc(
        db, tenant_id
    )

    if not tenant_doc:
        log.warning(f"Configuration Document was not found, because "
                    f"Tenant with tenant_id: {tenant_id} not found.")
        return None

    configuration = db.collection(configurations_collection_name).where(
        "tenant_ref", "==", tenant_doc.reference
    ).order_by(
        "server_timestamp", direction=firestore.Query.DESCENDING
    ).limit(1).get()

    if not configuration:
        log.warning("No Configuration document was found.")
        return None

    return configuration[0]


def pull_configuration_from_firestore(db: firestore.Client, configuration_id, tenant_id) -> firestore.DocumentSnapshot:
    """Pull down from the Firestore DB a configuration document given tenant_id and configuration_id.

    Returns:
        The configuration firestore.DocumentReference.
    """

    tenant_doc: firestore.DocumentSnapshot = pull_tenant_doc(db, tenant_id)

    if not tenant_doc:
        log.warning(f"Configuration Document was not found, because "
                    f"Tenant with tenant_id: {tenant_id} not found.")
        return None

    configuration = db.collection(configurations_collection_name). \
        where("tenant_ref", "==", tenant_doc.reference).where(configuration_id_field, "==", configuration_id). \
        limit(1).get()

    if not configuration:
        log.warning("No Configuration document was found.")
        return None

    return configuration[0]


def pull_docs_from_collection_associated_with_configuration(db: firestore.Client,
                                                            collection_name: str,
                                                            configuration_ref: firestore.DocumentReference) -> \
        List[firestore.DocumentSnapshot]:
    """Returns the documents of a collection that has the configuration value equal to
    the configuration reference received.

    Returns:
        The list of documents found for the query.
    """
    documents = db.collection(collection_name).where(configuration_reference_field_path, "==", configuration_ref).get()

    if not documents:
        log.warning(f"No documents found in collection {collection_name} for configuration {configuration_ref.id}")

    return documents


def get_perception_from_firestore(config_id, tenant_id, edge_logical_id, perception_name, client):
    configuration = pull_configuration_from_firestore(client, config_id, tenant_id)
    documents = client.collection(edges_collection_name). \
        where(configuration_reference_field_path, "==", configuration.reference). \
        where("logical_id", "==", edge_logical_id).get()
    if len(documents) != 1:
        return None
    edge_document = documents[0]
    return edge_document.get("is_of_kind_ref").get().get("perceptions")[perception_name]


def get_all_tenants_from_firestore(db: firestore.Client):
    documents = db.collection(tenants_collection_name).get()
    return [doc.to_dict() for doc in documents]


def get_machines_from_firestore(db: firestore.Client, tenant_id):
    configuration = pull_current_configuration_from_firestore(db, tenant_id)
    if configuration is None:
        return []
    documents = db.collection(machines_collection_name). \
        where(configuration_reference_field_path, "==", configuration.reference).get()
    return [doc.to_dict() for doc in documents]


def get_machine_from_firestore(db: firestore.Client, tenant_id, machine_id):
    configuration = pull_current_configuration_from_firestore(db, tenant_id)
    documents = db.collection(machines_collection_name). \
        where(configuration_reference_field_path, "==", configuration.reference). \
        where("machine_id", "==", machine_id).get()
    if not documents:
        return None
    return documents[0].to_dict()


def update_model_in_task(db: firestore.Client, tenant_id, machine_id, task_id, model_path):
    configuration = pull_current_configuration_from_firestore(db, tenant_id)
    documents = db.collection(machines_collection_name). \
        where(configuration_reference_field_path, "==", configuration.reference). \
        where("machine_id", "==", machine_id).get()
    if len(documents) != 1:
        print(f"Machine not found {machine_id}")
        return False
    document = documents[0]
    tasks = document.get("tasks")
    if task_id not in tasks:
        print(f"Task not found {task_id}")
        return False
    document_ref = document.reference
    path = f"tasks.{task_id}.task_data"
    document_ref.update({path: model_path})
    return True


def get_task_from_firestore(db: firestore.Client, tenant_id, machine_id, task_id):
    machine = get_machine_from_firestore(db, tenant_id, machine_id)
    if machine is None or task_id not in machine["tasks"]:
        print(f"Task not found {task_id}")
        return None
    return AssetTask(**machine["tasks"][task_id])


def get_signal_mode_from_firestore(config_id, tenant_id, edge_logical_id, perception_name, client):
    return get_perception_from_firestore(config_id, tenant_id, edge_logical_id, perception_name, client)["mode"]


def get_signal_dimensions_from_firestore(config_id, tenant_id, edge_logical_id, perception_name, client):
    return get_perception_from_firestore(config_id, tenant_id, edge_logical_id, perception_name, client)["dimensions"]


def get_pubsub_event_log(message):
    return f"edge_logical_id: {message['edge_logical_id']}, " \
           f"perception_name: {message['perception_name']}, " \
           f"tenant_id: {message['tenant_id']}, " \
           f"table_id: {message['table_id']}," \
           f"observation_timestamp: {message['observation_timestamp']}"


def get_ml_event_log(event):
    return f"event: {event['event']}, " \
           f"task_id: {event['task_id']}" \
           f"asset_id: {event['asset_id']}, " \
           f"tenant_id: {event['tenant_id']}, " \
           f"event_id: {event['event_id']}," \
           f"observation_timestamp: {event['observation_timestamp']}"
