import math

mean                = lambda data: sum(data) / len(data)
variance            = lambda data, ddof=0: sum((x - mean(data)) ** 2 for x in data) / (len(data) - ddof)
stdev               = lambda data: math.sqrt(variance(data))
ucl                 = lambda data: mean(data) + 3 * stdev(data)
lcl                 = lambda data: mean(data) - 3 * stdev(data)

def statistics(log, localdb, collection_name, one_to_update, batch_size, global_cap, queue_after_processing, decorator_kwargs):
    inventory_size              = localdb['inventory'].command("collstats", collection_name)
    products_size               = localdb['products'].command("collstats", collection_name)
    storage_content             = {'$set': {
        'storage.total_size': ( inventory_size["size"] + products_size["size"] ) / 1000000, 
        'storage.total_size_inventory': inventory_size["size"] / 1000000, 
        'storage.total_size_products': products_size["size"] / 1000000, 
        'storage.avg_size': ( inventory_size["avgObjSize"] + products_size["avgObjSize"] ) / 1000000, 
        'storage.avg_size_inventory': inventory_size["avgObjSize"] / 1000000, 
        'storage.avg_size_products': products_size["avgObjSize"] / 1000000,
        'storage.inventory_count': inventory_size["count"],
        'storage.products_count': products_size["count"],
        'storage.inventory_type': decorator_kwargs["supplier"]['unique'],
        'storage.products_type': decorator_kwargs["client"]['unique'],
        }
    }
        
    if queue_after_processing > 0:
        storage_content['$set']['storage.additional_capacity_to_completion'] = queue_after_processing * (products_size["avgObjSize"] + inventory_size["avgObjSize"]) / 1000000
        current_group           = f'batch_size_{batch_size}'
        field_control_by        = 'duration_per_product'
        controlled_history      = data[0]['history'] if len((data:=list(localdb['monitor']['processes'].aggregate([{'$match': one_to_update}, {'$project': {'_id': False, 'history': 1}}])))) > 0 and 'history' in data[0] else None
        if controlled_history: 
            log_started_statistics  = log.info(f'Started statistics', extra={'collection': collection_name})
            groups_means            = [(controlled_history[group][0]['batch_size'], mean([instance[field_control_by] for instance in controlled_history[group]]) ) for group in controlled_history if len(controlled_history[group]) > 0]
            optimal_batch_size      = min(groups_means, key = lambda t: t[1])
            log_optimal_batch       = log.info(f'Optimal batch size {optimal_batch_size[0]} with {optimal_batch_size[1] / 1000000} seconds {field_control_by}.', extra={'collection': collection_name})
            update_statistics       = localdb['monitor']['processes'].update_one(one_to_update, {'$set': {'duration.optimal_batch_size':optimal_batch_size[0], f'duration.optimal_{field_control_by}':optimal_batch_size[1], 'duration.ETC_in_hours': (queue_in_seconds := optimal_batch_size[1] * queue_after_processing) / 3600, 'duration.ETC_in_days': queue_in_seconds / 86400 }})
            for group in controlled_history:
                chosen_group_instances = controlled_history[group]
                if len(chosen_group_instances) == global_cap:
                    data_for_stats  = [instance[field_control_by] for instance in chosen_group_instances if field_control_by in instance]
                    stats_to_update = { f'duration.control.{group}': { '$exists' : False }, **one_to_update }
                    calculated_mean = mean(data_for_stats)
                    calculated_lcl  = lcl(data_for_stats)
                    sigma           = stdev(data_for_stats)
                    calculated_ucl  = ucl(data_for_stats)
                    statistics      = localdb['monitor']['processes'].update_one(stats_to_update, {
                                            '$set': {
                                                f'duration.control.{group}.mean': calculated_mean,
                                                f'duration.control.{group}.variance': variance(data_for_stats),
                                                f'duration.control.{group}.sigma': sigma,
                                                f'duration.control.{group}.upper_control_limit': calculated_ucl,
                                                f'duration.control.{group}.lower_control_limit': calculated_lcl if calculated_ucl > 0 else 0,
                                                f'duration.control.{group}.process_capability': ((calculated_ucl - calculated_lcl) / (6 * sigma)),
                                                f'duration.control.{group}.process_capability_right': ((calculated_ucl - calculated_mean) / (3 * sigma)),
                                                f'duration.control.{group}.process_capability_left': ((calculated_mean - calculated_lcl) / (3 * sigma)),
                                            }})
                    
                    if group == current_group:
                        data_points     = localdb['monitor']['processes'].update_one(one_to_update, {'$push': { f'duration.control.{current_group}.data_points': mean(data_for_stats) }})
                        cap_data_points = localdb['monitor']['processes'].update_one(one_to_update, {'$push': { f'duration.control.{current_group}.data_points': { '$each': [], '$slice': -global_cap }}})

        else:
            log_not_enough_history  = log.info(f'Not enought historic data to start statistics', extra={'collection': collection_name})
    else:
        no_queue                = localdb['monitor']['processes'].update_one(one_to_update, {'$set': {'duration.ETC_in_hours': 0, 'duration.ETC_in_days': 0, 'storage.additional_capacity_to_completion': 0 }})

    update_storage              = localdb['monitor']['processes'].update_one(one_to_update, storage_content)
