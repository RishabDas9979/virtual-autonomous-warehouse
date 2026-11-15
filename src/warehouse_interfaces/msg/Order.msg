uint32 id             # 0 on submission, the manager assigns the real id
string pickup         # a name from locations.yaml
string dropoff
uint8 priority        # 1 urgent, 2 normal, 3 low
float32 deadline_sec  # allowed time from submission, 0 = none
