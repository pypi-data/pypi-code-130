from typing import Any
from data_sorter.algos.selection_sort import selection_sort


def bucket_sort(arr):
    '''
    Bucket sort, or bin sort, is a sorting algorithm that works by distributing the elements of an array into a number of buckets.\n
    Bucket sort cannot be performed for integer value, so we convert all integer into fraction
    ```
    bucketSort()
      create N buckets each of which can hold a range of values
      for all the buckets
        initialize each bucket with 0 values
      for all the buckets
        put elements into buckets matching the range
      for all the buckets 
        sort elements in each bucket
      gather elements from each bucket
    end bucketSort
    ```
    '''
    m: Any = max(arr)
    n: int = len(arr)
    i: int = 1
    while int(m/i) > 0:
        i *= 10

    for i in range(n):
        arr[i] = arr[i]/i

    output: list = list()
    index: list = [[] for _ in range(n)]

    for i in range(n):
        index[int(arr[i]*n)].append(arr[i])

    for i in range(n):
        index[i] = selection_sort(index[i])

    for i in range(n):
        output = output + index[i]

    for i in range(n):
        output[i] = int(output[i]*i)
    
    return output
