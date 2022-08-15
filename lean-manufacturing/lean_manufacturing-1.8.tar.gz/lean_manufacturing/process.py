import atexit
import logging
import traceback
from typing import Tuple
from datetime import datetime
from random import sample
from .logging_handler import _MongoHandler

import pymongo

from .statistics import statistics

localdb                             = pymongo.MongoClient('mongodb://localhost:27017')
global_cap                          = 20

log = logging.getLogger('logs')
log.addHandler(_MongoHandler())
log.setLevel(logging.DEBUG)


def setup(collection_name: str, this_process: dict, decorator_kwargs: dict, function_kwargs: dict) -> Tuple[datetime, int, dict, list, int]:
    started_setup_at                = datetime.now()
    log_started_setup               = log.info('Started setup', extra={'collection': collection_name})

    supplier_config                 = decorator_kwargs['supplier']
    client_config                   = decorator_kwargs['client']
    schedule                        = decorator_kwargs.get('schedule', None)

    process_saved_config            = localdb['monitor']['processes'].find_one(this_process)
    last_success                    = process_saved_config.get('last_event', {}).get('last_success', None)

    if last_success:
        delta                       = started_setup_at - last_success
        delta_hours                 = delta.seconds / 60
        delta_days                  = delta.days
        skip                        = 0
        if schedule == '@hourly' and delta_hours < 1:
            log_not_scheduled_h     = log.info('Scheduled to run @hourly. Already run.')
            skip                    += 1
        elif schedule == '@daily' and delta_days < 1:
            log_not_scheduled_d     = log.info('Scheduled to run @daily. Already run.')
            skip                    += 1
        elif schedule == '@weekly' and delta_days < 7:
            log_not_scheduled_w     = log.info('Scheduled to run @weekly. Already run.')
            skip                    += 1
        elif schedule == '@monthly' and delta_days < 30:
            log_not_scheduled_m     = log.info('Scheduled to run @monthly. Already run.')
            skip                    += 1
        elif schedule == '@annually' and delta_days < 365:
            log_not_scheduled_a     = log.info('Scheduled to run @annually. Already run.')
            skip                    += 1
        if skip:
            return started_setup_at, 0, function_kwargs, [], 0, 0, {}

    list                            = supplier_config.get('list', None)
    batch_size                      = process_saved_config.get('batch_size', sample(range(1,10), 1)[0] * 10)
    log_batch_size                  = log.info(f'Working with batch size {batch_size}', extra={'collection': collection_name})
    complemented_kwargs             = function_kwargs | {'config': process_saved_config, 'batch_size': batch_size, 'last_success': last_success} if process_saved_config else function_kwargs

    if list:
        return batch_size, complemented_kwargs, list, len(list), min(batch_size, len(list)), {}

    update                          = supplier_config.get('update', False)

    supplier_db                     = pymongo.MongoClient(supplier_config['uri'])[supplier_config['db']] if 'uri' in supplier_config and 'db' in supplier_config else localdb['products']
    client_collection               = pymongo.MongoClient(client_config['uri'])[client_config['db']][client_config['collection']] if 'uri' in client_config and 'db' in client_config and 'collection' in client_config else localdb['products'][collection_name]
    collection                      = supplier_config['collection']
    supplier_unique                 = supplier_config['unique']
    base_aggregation                = supplier_config['aggregation'] if 'aggregation' in supplier_config else []

    order                           = supplier_config.get('order', False)
    regex                           = supplier_config.get('regex', False)
    gt                              = supplier_config.get('gt', False)
    content                         = supplier_config.get('content', ['@inventory'])

    queue_from_supplier             = [element[supplier_unique] for element in list(supplier_db[collection].aggregate(base_aggregation + [{'$project': { '_id': 0, supplier_unique: 1 } }]))]
    local_queue                     = [element[supplier_unique] for element in list(localdb['inventory'][collection_name].aggregate([])) if supplier_unique in element]

    queue_to_add                    = [x for x in queue_from_supplier if x not in local_queue]
    update_inventory                = localdb['inventory'][collection_name].insert_many([{supplier_unique:element} for element in queue_to_add]) if queue_to_add else None

    log_updated_queue               = log.info(f'Added {len(queue_to_add)} new items to the inventory.', extra={'collection': collection_name})

    type_of_match                   = {'$or': [{'last_process': {'$exists': False}}, {'last_process': {'$lt': started_setup_at}}] } if update else {'processed': {'$exists': False}}

    queue_size                      = queue[0]['count'] if (queue:= list(localdb['inventory'][collection_name].aggregate([{'$match': type_of_match},{'$count': 'count'}]))) and len(queue) > 0 and 'count' in queue[0] else 0
    processed_queue_size            = queue[0]['count'] if (queue:= list(localdb['inventory'][collection_name].aggregate([{'$match':{'processed': True}},{'$count': 'count'}]))) and len(queue) > 0 and 'count' in queue[0] else 0
    
    batch_pipeline                  = [{'$match': type_of_match}]
    batch_pipeline                 += [{'$addFields': { '_unique': { '$toInt': f'${supplier_unique}' } } }] if order or gt else []
    batch_pipeline                 += [{'$match': {'_unique': {'$gt': gt}}}] if gt else []
    batch_pipeline                 += [{'$sort': { '_unique': order }}] if order else []
    batch_pipeline                 += [{'$match': { supplier_unique: { '$regex': f'.*{regex}.*' } }}] if regex else []
    batch_pipeline                 += [{'$sample': {'size': batch_size}}]

    batch_queue                     = [element[supplier_unique] for element in list(localdb['inventory'][collection_name].aggregate(batch_pipeline)) if supplier_unique in element]
    this_batch                      = {supplier_unique: {'$in': batch_queue}}
    
    input                           = [{supplier_unique: unique} for unique in batch_queue]

    if '@all' in content or '@inventory' in content:
        inventory_dict              = {element[supplier_unique]: element for element in list(localdb['inventory'][collection_name].aggregate([{'$match': this_batch}]))}
        input                       = [dict(element, **{'inventory': inventory_dict[element[supplier_unique]]}) for element in input]
        log_add_inventory           = log.info(f'Added inventory content for {len(inventory_dict)} elements.')

    if '@all' in content or '@supplier' in content:
        supplier_input_dict         = {element[supplier_unique]: element for element in list(supplier_db[collection].aggregate(base_aggregation + [{'$match': this_batch}]))}
        input                       = [dict(element, **{'supplier': supplier_input_dict[element[supplier_unique]]}) for element in input]
        log_add_supplier            = log.info(f'Added supplier content for {len(supplier_input_dict)} elements.')

    if '@all' in content or '@existing' in content:
        existing_product_dict       = {element[supplier_unique]: element for element in list(client_collection.aggregate([{'$match': this_batch}]))}
        input                       = [dict(element, **{'existing_product': existing_product_dict[element[supplier_unique]]}) for element in input]
        log_add_existing            = log.info(f'Added existing content for {len(existing_product_dict)} elements.')

    batch_elements_size             = len(input)

    current_queue                   = {'current_batch_size':batch_size, 'queue.pending':queue_size, 'queue.processed':processed_queue_size, 'queue.total': (queue_size if update else queue_size + processed_queue_size)}
    update_queue_and_products       = localdb['monitor']['processes'].update_one({'collection': collection_name}, {'$set': current_queue })

    return started_setup_at, batch_size, complemented_kwargs, input, queue_size, batch_elements_size, this_batch

def process(collection_name, function, input, queue_size, batch_elements_size, complemented_kwargs):
    if batch_elements_size > 0:
        started_process_at          = datetime.now()
        log_started_process         = log.info(f'Started process with {batch_elements_size}', extra={'collection': collection_name})

        output                      = function(input, **complemented_kwargs)
        batch_products_size         = len(output) if output else 0
        queue_after_processing      = queue_size - batch_products_size

        return started_process_at, output, queue_after_processing
    else:
        log_no_queue_for_process    = log.info('No queue for processing', extra={'collection': collection_name})
        return None, None, 0

def pack(collection_name, decorator_kwargs, this_process, started_setup_at, batch_size, started_process_at, output, this_batch, queue_after_processing):
    output                          = [{key: val for key, val in element.items() if key not in ['inventory', 'supplier', 'existing_product']} for element in output if element] if output else []
    
    if output:

        started_packing_at          = datetime.now()
        log_packing                 = log.info(f'Started packing {len(output)} elements.', extra={'collection': collection_name})
        group_control_by            = f'batch_size_{batch_size}'
        client_config               = decorator_kwargs['client']
        client_collection           = pymongo.MongoClient(client_config['uri'])[client_config['db']][client_config['collection']] if 'uri' in client_config and 'db' in client_config and 'collection' in client_config else localdb['products'][collection_name]
        client_unique               = client_config['unique']
        update                      = decorator_kwargs['supplier'].get('update', False)

        existing_products_ids       = [element[client_unique] for element in list(client_collection.aggregate([{'$project':{'_id': 0, client_unique: 1}}])) if client_unique in element]
        output_ids                  = [element[client_unique] for element in output]
        output_dict                 = {element[client_unique]: element for element in output}

        new_output_ids              = [x for x in output_ids if x not in existing_products_ids]
        new_output                  = [output_dict[id] for id in new_output_ids]

        documents_to_insert         = [document for document in new_output if type(output) == list and document[client_unique] not in existing_products_ids]
        documents_to_update         = [document for document in output if document not in documents_to_insert] if update else []
        
        sure                        = input(f'Do you want to insert {len(documents_to_insert)} and update {len(documents_to_update)} to {client_config["uri"]}? (Y/N) ') if 'uri' in client_config else 'Y'

        if sure == 'Y':
            bulk_insert                 = client_collection.insert_many(documents_to_insert).inserted_ids if documents_to_insert else []
            bulk_update_orders          = [pymongo.UpdateOne({client_unique: element[client_unique]}, {'$set' : dict(**element, updated=True) }, upsert=False) for element in documents_to_update]
            bulk_update                 = client_collection.bulk_write(bulk_update_orders).bulk_api_result if bulk_update_orders else {}

            log_db_changes              = log.info(f'Inserted {len(bulk_insert)} and updated {bulk_update.get("nModified", 0)}', extra={'collection': collection_name})
            update_inventory            = localdb['inventory'][collection_name].update_many(this_batch, {'$set': {'processed': True, 'last_process': started_packing_at}})

        ended_at                    = datetime.now()
        cycle_time                  = ended_at - started_setup_at
        setup_time                  = started_process_at - started_setup_at
        process_time                = started_packing_at - started_process_at
        packing_time                = ended_at - started_packing_at
        chosen_metric_1             = lambda object: object.total_seconds()
        chosen_metric_2             = lambda object: object.total_seconds()
        batch_products_size         = len(output)
        
        turn_worker_off             = localdb['monitor']['processes'].update_one(this_process, {
                                    '$set': {
                                        'running': False,
                                        'products': len(existing_products_ids), 
                                        'last_event.last_success': ended_at, 
                                        'last_event.last_setup': started_setup_at,
                                        'last_event.last_process': started_process_at,
                                        'last_event.last_packing': started_packing_at,
                                        'last_duration.batch_size': batch_size,
                                        'last_duration.output': batch_products_size,
                                        'last_duration.last_duration': chosen_metric_1(cycle_time), 
                                        'last_duration.last_duration_per_product': chosen_metric_1(cycle_time) / batch_size,
                                        'last_duration.last_setup_duration': chosen_metric_1(setup_time),
                                        'last_duration.last_process_duration': chosen_metric_1(process_time),
                                        'last_duration.last_packing_duration': chosen_metric_1(packing_time)
                                        }, 
                                    '$push': { 
                                        f'history.{group_control_by}': {
                                            'started_at': started_setup_at,
                                            'ended_at': ended_at,
                                            'batch_size': batch_size,
                                            'output': batch_products_size,
                                            'duration': chosen_metric_2(cycle_time), 
                                            'duration_per_product': chosen_metric_2(cycle_time) / batch_size,
                                            'setup_duration': chosen_metric_2(setup_time),
                                            'process_duration': chosen_metric_2(process_time),
                                            'packing_duration': chosen_metric_2(packing_time)
                                        }}}, upsert=True)
        cap_history                 = localdb['monitor']['processes'].update_one(this_process, {'$push': { f'history.{group_control_by}': { '$each': [], '$slice': -global_cap }}})

    else:
        log_no_product_for_packing  = log.info('No product for packing', extra={'collection': collection_name})
        also_turn_worker_off        = localdb['monitor']['processes'].update_one(this_process, { '$set': {'running': False }})
    
    run_statistics                  = statistics(log, localdb, collection_name, this_process, batch_size, global_cap, queue_after_processing, decorator_kwargs)

def attempt(this_process, collection_name):
    def selected_function(subprocess):
        def inner_function(*subprocess_args, **subprocess_kwargs):
            try:
                return subprocess(*subprocess_args, **subprocess_kwargs)
            except Exception as e:
                error_time              = datetime.now()
                error_message           = f'{type(e).__name__}: {" ".join(e.args)}'
                turn_worker_off         = localdb['monitor']['processes'].update_one(this_process, {'$set': {'running': False, 'last_failure': error_time}, '$addToSet': {'errors': {'error_time': error_time, 'phase': subprocess.__name__, 'message': error_message, 'traceback': traceback.format_exc()}}}, upsert=True)
                cap_errors              = localdb['monitor']['processes'].update_one(this_process, {'$push': { f'errors': { '$each': [], '$slice': -global_cap }}})
                log_error               = log.error(f'{error_message}', extra={'collection': collection_name})
                raise
        return inner_function
    return selected_function

def process_until_completed(value_stream, function, decorator_kwargs, function_kwargs):
    collection_name                 = f'{value_stream}.{function.__name__}'
    this_process                    = {'collection': collection_name, 'name': function.__name__, 'value_stream': value_stream}
    turn_process_on                 = localdb['monitor']['processes'].update_one(this_process, {'$set': {'running': True}, '$inc': {'current_workers': 1}}, upsert=True)
    turn_process_off                = lambda: localdb['monitor']['processes'].update_one(this_process, {'$set': {'running': False}, '$inc': {'current_workers': -1}})
    register_turn_process_off       = atexit.register(turn_process_off)

    started_setup_at, batch_size, complemented_kwargs, input, queue_size, batch_elements_size, this_batch       = attempt(this_process, collection_name)(setup)(collection_name, this_process, decorator_kwargs, function_kwargs)
    started_process_at, output, queue_after_processing                                                          = attempt(this_process, collection_name)(process)(collection_name, function, input, queue_size, batch_elements_size, complemented_kwargs)
    pack_products                                                                                               = attempt(this_process, collection_name)(pack)(collection_name, decorator_kwargs, this_process, started_setup_at, batch_size, started_process_at, output, this_batch, queue_after_processing)

    if queue_after_processing > 0:
        turn_process_off()
        process_until_completed(value_stream, function, decorator_kwargs, function_kwargs)
    
    turn_process_off()
