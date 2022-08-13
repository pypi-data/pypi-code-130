def selection_sort(array):
    length = len(array)
    for step in range(length):
        min_idx = step

        for i in range(step + 1, length):

            if array[i] < array[min_idx]:
                min_idx = i

        (array[step], array[min_idx]) = (array[min_idx], array[step])