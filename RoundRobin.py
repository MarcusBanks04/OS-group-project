from collections import deque

def round_robin(process_list, time_quantum):
    time = 0
    ready_queue = deque()
    waiting_queue = []  # (pid, io_end_time)
    gantt = []

    processes = {}

    # Initialize processes
    for p in process_list:
        pid, at, bt, io_start, io_time = p
        processes[pid] = {
            "arrival": at,
            "burst": bt,
            "remaining": bt,
            "io_start": io_start,
            "io_time": io_time,
            "has_done_io": False,
            "completion": None
        }

    process_list.sort(key=lambda x: x[1])
    i = 0

    current = None
    quantum_left = 0

    def all_done():
        return all(p["remaining"] == 0 for p in processes.values())

    while not all_done():

        # Add arrivals
        while i < len(process_list) and process_list[i][1] <= time:
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

        # If no current process, get one
        if current is None:
            if ready_queue:
                current = ready_queue.popleft()
                quantum_left = time_quantum
                gantt.append((time, current))
            else:
                # CPU idle
                if not gantt or gantt[-1][1] != "Idle":
                    gantt.append((time, "Idle"))
                time += 1
                continue

        proc = processes[current]

        # Execute 1 unit
        proc["remaining"] -= 1
        quantum_left -= 1
        time += 1

        executed = proc["burst"] - proc["remaining"]

        # I/O trigger
        if (not proc["has_done_io"]) and executed == proc["io_start"]:
            proc["has_done_io"] = True

            # Single I/O device (queue it)
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

    # ===== OUTPUT =====
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
    print("\nAverage WT:", total_wt / n)
    print("Average TAT:", total_tat / n)

    # ===== CLEAN GANTT =====
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


# ===== TEST INPUT =====
if __name__ == "__main__":
    process_list = [
        ["P1", 0, 10, 2, 3],
        ["P2", 2, 6, 1, 2],
        ["P3", 4, 8, 3, 1],
        ["p4", 5, 7, 2, 2],
        ["P5", 6, 5, 1, 2],
        ["P6", 7, 9, 4, 3],
        ["P7", 8, 4, 2, 1],
        ["P8", 9, 11, 5, 2],
        ["P9", 10, 6, 2, 3],
        ["P10", 11, 8, 3, 2],
        ["P11", 12, 7, 2, 1],
        ["P12", 13, 5, 1, 3],
        ["P13", 14, 9, 4, 2],
        ["P14", 15, 6, 2, 2],
        ["P15", 16, 10, 5, 3],
        ["P16", 17, 4, 1, 1],
        ["P17", 18, 8, 3, 2],
        ["P18", 19, 7, 2, 3],
        ["P19", 20, 5, 1, 2],
        ["P20", 21, 9, 4, 1]
    ]

    time_quantum = 2
    round_robin(process_list, time_quantum)