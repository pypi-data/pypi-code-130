import random

def partition_batch_size(data, batch_size):
    result = []
    if batch_size <= 0:
        return result
    k = len(data) // batch_size
    for i in range(0, k):
        result.append(data[i * batch_size : (i+1) * batch_size])
    if len(data) % batch_size > 0:
        result.append(data[k * batch_size : ])
    return result


def partition_num_batches(data, num_batches):
    result = []
    if num_batches <= 0:
        return result
    batch_size = len(data) // num_batches
    r = len(data) % num_batches
    for i in range(0, num_batches):
        if i < r:
            result.append( data[ i * (batch_size+1): (i+1) * (batch_size + 1)] )
            continue
        result.append( data[ r * (batch_size+1) + (i-r) * batch_size : r * (batch_size+1) + (i-r+1) * batch_size ] )
    return result


def partition_data(data, batch_size):
    result = []
    if batch_size <= 0:
        return result
    k = len(data) // batch_size
    for i in range(0, k-1):
        result.append(data[i * batch_size : (i+1) * batch_size])
    result.append(data[(k-1) * batch_size : ])
    return result
