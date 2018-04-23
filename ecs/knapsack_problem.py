# coding=utf-8
def assign(yHat_,input_infor):
    '''
    cpu_disk = {"flavor1": [1, 1], "flavor2": [1, 2], "flavor3": [1, 4], "flavor4": [2, 2],
                "flavor5": [2, 4], "flavor6": [2, 8], "flavor7": [4, 4], "flavor8": [4, 8],
                "flavor9": [4, 16], "flavor10": [8, 8], "flavor11": [8, 16], "flavor12": [8, 32],
                "flavor13": [16, 16], "flavor14": [16, 32], "flavor15": [16, 64]}
    '''
    optimize = input_infor['optimize']
    flavors = ['flavor1', 'flavor2', 'flavor3', 'flavor4', 'flavor5', 'flavor6', 'flavor7', 'flavor8', 'flavor9', 'flavor10', \
     'flavor11', 'flavor12', 'flavor13', 'flavor14', 'flavor15']
    yHat = [0]*len(flavors)
    i = 0
    for flavor  in input_infor['flavor']:
        yHat[int(flavor[6:])-1] = yHat_[i]
        i+=1

    if optimize =='CPU':
        weight = [0, 1, 2, 4, 2, 4, 8, 4, 8, 16, 8, 16, 32, 16, 32, 64]
        value = [0, 1, 1, 1, 2, 2, 2, 4, 4, 4, 8, 8, 8, 16, 16, 16]
        volume_max =int( input_infor['memory'])
        value_max=int(input_infor['cpu'])
    if optimize == 'MEM':
        weight = [0, 1, 1, 1, 2, 2, 2, 4, 4, 4, 8, 8, 8, 16, 16, 16]
        value = [0, 1, 2, 4, 2, 4, 8, 4, 8, 16, 8, 16, 32, 16, 32, 64]
        volume_max = int(input_infor['cpu'])
        value_max = int(input_infor['memory'])

    highest_utilization = 0
    server = []
    total_values=[]
    amount = [0] + yHat
    total_value,flavor_ = dynamic_programming_cpuAnddisk(volume_max,value_max,weight,value,amount)
    total_values.append(total_value)
    server.append(count_flavor(flavor_))
    amount = [(amount[i]-server[-1][i]) for i in range(len(amount))]
    while sum(amount) != 0:
        total_value, flavor_ = dynamic_programming_cpuAnddisk(volume_max,value_max, weight, value, amount)
        total_values.append(total_value)
        server.append(count_flavor(flavor_))
        amount = [(amount[i] - server[-1][i]) for i in range(len(amount))]
    utilization =float(sum(total_values))/ (value_max*len(server))
    return server,utilization
def count_flavor(flavor_):
    flavors = [0 for _ in range(0,16)]
    for flavor in flavor_:
        if flavor == 1:
            flavors[1] += 1
        if flavor == 2:
            flavors[2] += 1
        if flavor == 3:
            flavors[3] += 1
        if flavor == 4:
            flavors[4] += 1
        if flavor == 5:
            flavors[5] += 1
        if flavor == 6:
            flavors[6] += 1
        if flavor == 7:
            flavors[7] += 1
        if flavor == 8:
            flavors[8] += 1
        if flavor == 9:
            flavors[9] += 1
        if flavor == 10:
            flavors[10] += 1
        if flavor == 11:
            flavors[11] += 1
        if flavor == 12:
            flavors[12] += 1
        if flavor == 13:
            flavors[13] += 1
        if flavor == 14:
            flavors[14] += 1
        if flavor == 15:
            flavors[15] += 1
    return flavors
def dynamic_programming_cpuAnddisk(volume_max, value_max, weight, value, num):
    bagID = [[] for i in range(volume_max + 1)]
    maxTotalValue = [0] * (volume_max + 1);  # maxTotalValue[i]:背包已装容量为i时,背包里所装物品的最大总价值
    for j in range(1, len(weight)):
        for i in range(volume_max, 0, -1):
            if i >= weight[j]:
                counts = int(min((i) / weight[j], num[j]))
                for k in range(1, counts + 1):
                    if maxTotalValue[i] >= k * value[j] + maxTotalValue[i - k * weight[j]]:
                        continue
                    else:
                        if maxTotalValue[i] < maxTotalValue[i - k * weight[j]] + k * value[j] and maxTotalValue[i - k * weight[j]] + k * value[j] <=value_max:
                            maxTotalValue[i] = maxTotalValue[i - k * weight[j]] + k * value[j]
                            last_ID = bagID[i - k * weight[j]][:]
                            for _ in range(k): last_ID.append(j)
                            bagID[i] = last_ID
                        else:
                            continue
            else:
                continue
    return maxTotalValue[volume_max], bagID[volume_max]
