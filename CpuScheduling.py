from collections import deque

# =========================
# ROUND ROBIN
# =========================
def round_robin(process_list, time_quantum):

    time = 0
    ready_queue = deque()
    waiting_queue = []
    gantt = []

    processes = {}

 
    for p in process_list:

        pid = p[0]
        bt = p[1]
        at = p[2]
        io_start = p[3][0]
        io_time = p[3][1]

        processes[pid] = {
            "arrival": at,
            "burst": bt,
            "remaining": bt,
            "io_start": io_start,
            "io_time": io_time,
            "has_done_io": False,
            "completion": None
        }

    # SORT BY ARRIVAL
    process_list.sort(key=lambda x: x[2])

    i = 0

    current = None
    quantum_left = 0

    def all_done():
        return all(p["remaining"] == 0 for p in processes.values())

    while not all_done():

        # Add arrivals
        while i < len(process_list) and process_list[i][2] <= time:
            ready_queue.append(process_list[i][0])
            i += 1

        # Check I/O completion
        new_wait = []
        for pid, end in waiting_queue:
            if time >= end:
                ready_queue.append(pid)
            else:
                new_wait.append((pid, end))
        waiting_queue = new_wait

        # Get process
        if current is None:
            if ready_queue:
                current = ready_queue.popleft()
                quantum_left = time_quantum
                gantt.append((time, current))
            else:
                if not gantt or gantt[-1][1] != "Idle":
                    gantt.append((time, "Idle"))
                time += 1
                continue

        proc = processes[current]

        # Execute
        proc["remaining"] -= 1
        quantum_left -= 1
        time += 1

        executed = proc["burst"] - proc["remaining"]

        # I/O Trigger
        if (not proc["has_done_io"]) and executed == proc["io_start"]:
            proc["has_done_io"] = True

            start_io = time
            if waiting_queue:
                last_end = max(x[1] for x in waiting_queue)
                start_io = max(start_io, last_end)

            io_end = start_io + proc["io_time"]
            waiting_queue.append((current, io_end))

            current = None
            continue

        # Finished
        if proc["remaining"] == 0:
            proc["completion"] = time
            current = None
            continue

        # Quantum expired
        if quantum_left == 0:
            ready_queue.append(current)
            current = None

    # =========================
    # OUTPUT
    # =========================

    print("\n==============================")
    print("ROUND ROBIN Scheduling With I/O")
    print("==============================")

    print("\nProcess Table:")
    print("PID\tAT\tBT\tCT\tTAT\tWT")

    total_wt = 0
    total_tat = 0

    for pid, p in processes.items():

        at = p["arrival"]
        bt = p["burst"]
        ct = p["completion"]

        tat = ct - at
        wt = tat - bt

        total_wt += wt
        total_tat += tat

        print(f"{pid}\t{at}\t{bt}\t{ct}\t{tat}\t{wt}")

    n = len(processes)

    print("\nAverage WT:", round(total_wt / n, 2))
    print("Average TAT:", round(total_tat / n, 2))

    # Gantt
    print("\nGantt Chart:")

    timeline = ""
    times = ""

    for i in range(len(gantt)):
        start, pid = gantt[i]

        timeline += f"| {pid} "
        times += f"{start}".ljust(5)

    times += str(time)

    print(timeline + "|")
    print(times)


# =================================================
# FCFS Scheduling with one I/O operation per process
# ==================================================

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

    #fcfs_with_io(process_list)
#===================================
# END OF FCFS
#===================================



#==================================================================
# Preemptive Priority Scheduling with one I/O operation per process
#==================================================================
def priority_with_io(process_list):
    processes = []

    for index, p in enumerate(process_list):
        processes.append({
            "pid": p[0],
            "burst": p[1],
            "arrival": p[2],
            "io_start": p[3][0],
            "io_time": p[3][1],
            "priority": p[4],
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

        # Finish I/O
        if current_io is not None and time == io_finish_time:
            current_io["in_io"] = False
            current_io["io_done"] = True
            current_io = None
            io_finish_time = None

        # Start next I/O
        if current_io is None and len(io_waiting) > 0:
            current_io = io_waiting.pop(0)
            io_finish_time = time + current_io["io_time"]

        ready = []

        for p in processes:
            if (
                p["arrival"] <= time
                and not p["done"]
                and not p["in_io"]
                and p["remaining"] > 0
            ):
                ready.append(p)

        if len(ready) == 0:
            gantt.append("waste")
            time += 1
            continue

        # Preemptive priority
        ready.sort(key=lambda x: (x["priority"], x["arrival"], x["order"]))
        current = ready[0]

        for p in ready:
            if p != current:
                p["ready_queue_time"] += 1

        if current["first_start_time"] is None:
            current["first_start_time"] = time

        gantt.append(current["pid"])
        current["remaining"] -= 1
        current["executed"] += 1
        time += 1

        if current["remaining"] == 0:
            current["done"] = True
            current["finish_time"] = time

        elif current["executed"] == current["io_start"] and not current["io_done"]:
            current["in_io"] = True
            io_waiting.append(current)

    print_results("Priority Scheduling With I/O", processes, gantt)

def print_results(title, processes, gantt):
    compressed = []
    start = 0

    for i in range(1, len(gantt)):
        if gantt[i] != gantt[i - 1]:
            compressed.append((gantt[i - 1], start, i))
            start = i

    compressed.append((gantt[-1], start, len(gantt)))

    print("\n==============================")
    print(title)
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

    idle_time = gantt.count("waste")

    print("\nProcess Results:")
    print("PID\tAT\tBT\tIO Start\tIO Time\tPriority\tCT\tTAT\tWT\tRQT\tRT")

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

        priority = p["priority"] if "priority" in p else "-"

        print(
            p["pid"], "\t",
            p["arrival"], "\t",
            p["burst"], "\t",
            p["io_start"], "\t\t",
            p["io_time"], "\t",
            priority, "\t\t",
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

    priority_process_list = [
        ["P1", 10, 0, [2, 3], 3],
        ["P2", 6, 2, [1, 2], 1],
        ["P3", 8, 4, [3, 1], 4],
        ["P4", 7, 5, [2, 2], 2],
        ["P5", 5, 6, [1, 2], 5],
        ["P6", 9, 7, [4, 3], 3],
        ["P7", 4, 8, [2, 1], 1],
        ["P8", 11, 9, [5, 2], 4],
        ["P9", 6, 10, [2, 3], 2],
        ["P10", 8, 11, [3, 2], 5],
        ["P11", 7, 12, [2, 1], 3],
        ["P12", 5, 13, [1, 3], 1],
        ["P13", 9, 14, [4, 2], 4],
        ["P14", 6, 15, [2, 2], 2],
        ["P15", 10, 16, [5, 3], 5],
        ["P16", 4, 17, [1, 1], 1],
        ["P17", 8, 18, [3, 2], 3],
        ["P18", 7, 19, [2, 3], 2],
        ["P19", 5, 20, [1, 2], 4],
        ["P20", 9, 21, [4, 1], 5]
    ]

   # priority_with_io(priority_process_list)

#=========================================
# END OF PRIORITY
#=========================================



# =========================
# MAIN MENU BELOW
# =========================
if __name__ == "__main__":

    # SAME FORMAT FOR ALL
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
        ["P10", 8, 11, [3, 2]]
    ]

    # FOR PRIORITY ONLY
    priority_process_list = [
        ["P1", 10, 0, [2, 3], 3],
        ["P2", 6, 2, [1, 2], 1],
        ["P3", 8, 4, [3, 1], 4],
        ["P4", 7, 5, [2, 2], 2],
        ["P5", 5, 6, [1, 2], 5]
    ]

    print("\nCPU Scheduling Algorithms")
    print("1. Round Robin")
    print("2. FCFS")
    print("3. Priority")

    choice = input("\nEnter Choice: ")

    if choice == "1":

        tq = int(input("Enter Time Quantum: "))
        round_robin(process_list, tq)

    elif choice == "2":

        fcfs_with_io(process_list)

    elif choice == "3":

        priority_with_io(priority_process_list)

    else:
        print("Invalid Choice")