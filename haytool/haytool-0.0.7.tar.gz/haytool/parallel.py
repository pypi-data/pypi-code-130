from concurrent.futures import ThreadPoolExecutor, as_completed
import glog as log


def threadhandler(infunc, list_items, max_workers=None):
    """Function applies function parallely, `infunc`, to list of items

    Args:
        infunc (function): Function that takes in 1 or 2 inputs, and outputs
        list_items (list): List of items. Can be tuple [(x,y),(a,b)]
        max_workers (int, optional): Number of workers, or number of threads you want to initiate to parallelize the task. Defaults to None.

    Returns:
        [type]: [description]
    """
    log(f"-- Initiating thread for processing {len(list_items)} items with {infunc.__name__} function")
    list_results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # If items within list are tuples to unpack. If function requires more than 1 argument.
        if all([isinstance(x, tuple) for x in list_items]):
            future_to_row = {executor.submit(infunc, item[0], item[1]): item for item in list_items}
        else:
            future_to_row = {executor.submit(infunc, item): item for item in list_items}
        for future in as_completed(future_to_row):
            results = future.result()
            list_results.append(results)
    return list_results
