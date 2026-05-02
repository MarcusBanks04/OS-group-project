# FCFS Scheduling with one I/O operation per process
# Includes:
# Completion Time
# Turnaround Time
# Waiting Time
# Ready Queue Time
# Response Time
# CPU Idle Time

def fcfs_with_io(process_list):
    processes = []

    for index, p in enumerate(process_list):
        processes.append({
            "pid": p[0],
            "burst": p[1],
            "arrival": p[2],
            "io_start": p[3][0],
            "io_time": p[3][1],
            "remaining": p[1],
            "executed": 0,
            "io_done": False,
            "in_io": False,
            "done": False,
            "order": index,
            "finish_time": None,
            "first_start_time": None,
            "ready_queue_time": 0
        })

    time = 0
    gantt = []

    io_waiting = []
    current_io = None
    io_finish_time = None

    while not all(p["done"] for p in processes):

        # Finish current I/O if done
        if current_io is not None and time == io_finish_time:
            current_io["in_io"] = False
            current_io["io_done"] = True
            current_io = None
            io_finish_time = None

        # Start next I/O if I/O device is free
        if current_io is None and len(io_waiting) > 0:
            current_io = io_waiting.pop(0)
            io_finish_time = time + current_io["io_time"]

        # Build ready queue
        ready = []
        for p in processes:
            if (
                p["arrival"] <= time
                and not p["done"]
                and not p["in_io"]
                and p["remaining"] > 0
            ):
                ready.append(p)

        # If no process is ready, CPU is wasted
        if len(ready) == 0:
            gantt.append("waste")
            time += 1
            continue

        # FCFS: sort by original arrival/input order
        ready.sort(key=lambda x: x["order"])
        current = ready[0]

        # Add ready queue time for all ready processes except the one running
        for p in ready:
            if p != current:
                p["ready_queue_time"] += 1

        # Set response time when process first gets CPU
        if current["first_start_time"] is None:
            current["first_start_time"] = time

        # Run process for 1 CPU unit
        gantt.append(current["pid"])
        current["remaining"] -= 1
        current["executed"] += 1
        time += 1

        # If process finishes
        if current["remaining"] == 0:
            current["done"] = True
            current["finish_time"] = time

        # If process reaches I/O request point
        elif current["executed"] == current["io_start"] and not current["io_done"]:
            current["in_io"] = True
            io_waiting.append(current)

    # Compress Gantt chart
    compressed = []
    start = 0

    for i in range(1, len(gantt)):
        if gantt[i] != gantt[i - 1]:
            compressed.append((gantt[i - 1], start, i))
            start = i

    compressed.append((gantt[-1], start, len(gantt)))

    # Print Gantt Chart
    print("\n==============================")
    print("FCFS Scheduling With I/O")
    print("==============================")

    print("\nGantt Chart:")

    top = ""
    bottom = ""

    for block in compressed:
        label = block[0]
        start_time = block[1]

        if label == "waste":
            segment = "|_waste_"
        else:
            segment = f"|__{label}__"

        top += segment
        bottom += str(start_time).ljust(len(segment))

    top += "|"
    bottom += str(compressed[-1][2])

    print(top)
    print(bottom)

    # CPU idle time
    idle_time = gantt.count("waste")

    # Print Results
    print("\nProcess Results:")
    print("PID\tAT\tBT\tIO Start\tIO Time\tCT\tTAT\tWT\tRQT\tRT")

    total_tat = 0
    total_wt = 0
    total_rqt = 0
    total_rt = 0

    for p in processes:
        turnaround_time = p["finish_time"] - p["arrival"]
        waiting_time = turnaround_time - p["burst"] - p["io_time"]
        response_time = p["first_start_time"] - p["arrival"]

        total_tat += turnaround_time
        total_wt += waiting_time
        total_rqt += p["ready_queue_time"]
        total_rt += response_time

        print(
            p["pid"], "\t",
            p["arrival"], "\t",
            p["burst"], "\t",
            p["io_start"], "\t\t",
            p["io_time"], "\t",
            p["finish_time"], "\t",
            turnaround_time, "\t",
            waiting_time, "\t",
            p["ready_queue_time"], "\t",
            response_time
        )

    number_of_processes = len(processes)

    print("\nSummary:")
    print("Total CPU Idle/Waste Time:", idle_time)
    print("Average Turnaround Time:", round(total_tat / number_of_processes, 2))
    print("Average Waiting Time:", round(total_wt / number_of_processes, 2))
    print("Average Ready Queue Time:", round(total_rqt / number_of_processes, 2))
    print("Average Response Time:", round(total_rt / number_of_processes, 2))


if __name__ == "__main__":

    process_list = [
        ["P1", 10, 0, [2, 3]],
        ["P2", 6, 2, [1, 2]],
        ["P3", 8, 4, [3, 1]],
        ["P4", 7, 5, [2, 2]],
        ["P5", 5, 6, [1, 2]],

        ["P6", 9, 7, [4, 3]],
        ["P7", 4, 8, [2, 1]],
        ["P8", 11, 9, [5, 2]],
        ["P9", 6, 10, [2, 3]],
        ["P10", 8, 11, [3, 2]],

        ["P11", 7, 12, [2, 1]],
        ["P12", 5, 13, [1, 3]],
        ["P13", 9, 14, [4, 2]],
        ["P14", 6, 15, [2, 2]],
        ["P15", 10, 16, [5, 3]],

        ["P16", 4, 17, [1, 1]],
        ["P17", 8, 18, [3, 2]],
        ["P18", 7, 19, [2, 3]],
        ["P19", 5, 20, [1, 2]],
        ["P20", 9, 21, [4, 1]]
    ]

    fcfs_with_io(process_list)