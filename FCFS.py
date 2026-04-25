# FCFS CPU Scheduling algorithm
# input: process list
# Process: [Arrival time, Burst time, pid]

def fcfs(process_list):
    t = 0
    gantt = []
    completed = {}

    # sort by arrival time
    process_list.sort()

    for process in process_list:
        arrival_time = process[0]
        burst_time = process[1]
        pid = process[2]

        # CPU is idle until this process arrives
        while t < arrival_time:
            gantt.append("Idle")
            t += 1

        # run process completely
        gantt.append(pid)
        t += burst_time

        ct = t
        tat = ct - arrival_time
        wt = tat - burst_time

        completed[pid] = {
            "CT": ct,
            "TAT": tat,
            "WT": wt
        }

    print("Gantt Chart:", gantt)
    print("Completed:", completed)


if __name__ == "__main__":
    process_list = [[2,6,"p1"], [5,2,"p2"], [1,8,"p3"], [0,3,"p4"], [4,4,"p5"]]
    fcfs(process_list)