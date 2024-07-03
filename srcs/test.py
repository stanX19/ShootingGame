import time


def test_double_sort_time(repeats=100000):
    # Original list
    lst = [5, 2, 9, 1, 5, 6]

    # Initialize time accumulators
    total_time_double_sort = 0
    total_time_single_sort = 0

    for _ in range(repeats):
        # Copy the list for sorting
        lst_for_sort = lst.copy()

        # Measure time for double sort (sort(), sort())
        start_time = time.time()
        lst_for_sort.sort()
        lst_for_sort.sort()
        end_time = time.time()
        total_time_double_sort += (end_time - start_time)

        # Measure time for single sort (sort())
        lst_for_sort = lst.copy()
        start_time = time.time()
        lst_for_sort.sort()
        end_time = time.time()
        total_time_single_sort += (end_time - start_time)

    # Calculate average times
    avg_time_double_sort = total_time_double_sort / repeats
    avg_time_single_sort = total_time_single_sort / repeats

    print(f"Average time for double sort (sort(), sort()): {avg_time_double_sort:.10f} seconds")
    print(f"Average time for single sort (sort()): {avg_time_single_sort:.10f} seconds")


# Run the test 1000 times
test_double_sort_time()
