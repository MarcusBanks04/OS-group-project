#Round Robin CPU Scheduling algorithm
#input: process list, time quantam
#Process: [Arrival time, Burst time, pid]

def round_robin(process_list, time_quantam):
    t = 0
    gantt = []
    completed = {}
    #sorts the process based on arrival time
    process_list.sort()
    burst_times = {}
    for p in process_list:
        pid = p[2]
        burst_time = p[1]
        burst_times[pid] = burst_time

    
    while process_list != []:
        available = []
        for p in process_list:
            at = p[0]
            if p[0] <= t:
                available.append(p)
        #boundary condition 1
        if available == []:
            gantt.append("Idle")
            t += 1
            continue
        else:
            process = available[0]
            #Service this process now
            gantt.append(process[2])
            #Remove the process
            process_list.remove(process)
            #Update the burst time
            rem_burst = process[1]
            if rem_burst <= time_quantam: 
                t += rem_burst
                ct = t
                arrival_time = process[0]
                pid = process[2]
                arrival_time = burst_times[pid]
                tat = ct - arrival_time
                wt = tat - burst_time
                completed[process[2]] = {ct, tat, wt}
                continue
            else: 
                t += time_quantam
                process[1] -= time_quantam
                process_list.append(process)
    print(gantt)
    print(completed)

if __name__ == "__main__":
    process_list = [[2,6, "p1"],[5,2,"p2"],[1,8, "p3"],[0,3,"p4"],[4,4,"p5"]]
    time_quantam = 2
    round_robin(process_list, time_quantam)

