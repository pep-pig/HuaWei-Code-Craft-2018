import os
from datetime import datetime
import copy
'''
generate feature
'''

def feature_modeling(raw_dataSet,input_infor):
    vm =     {'flavor1' : [],
              'flavor2' : [],
              'flavor3' : [],
              'flavor4' : [],
              'flavor5' : [],
              'flavor6' : [],
              'flavor7' : [],
              'flavor8' : [],
              'flavor9' : [],
              'flavor10': [],
              'flavor11': [],
              'flavor12': [],
              'flavor13': [],
              'flavor14': [],
              'flavor15': [],}
    date = raw_dataSet[0].split("\t")[2].split(" ")[0].split('-')
    last_date = date[0] + '-' + date[1] + '-' + str(int(date[2]) - 1)
    span = input_infor['span']
    for item in raw_dataSet:
        values = item.split("\t")
        uuid = values[0]
        flavorName = values[1]
        current_date,createtimeFrame = values[2].split(" ")[0:]
        if flavorName in vm.keys():
            feature_day_amount(vm,flavorName,current_date,last_date)
        last_date = current_date
    #reduce_noise(vm)
    feature_others(vm)
    label_y(vm,span)
    test_set = pressece(vm, input_infor,span)
    return vm,test_set
def reduce_noise(vm):
    for flavor in vm.keys():
        for i in range(1,len(vm[flavor])-1):
            if (vm[flavor][i][0]-vm[flavor][i-1][0])>=8 and (vm[flavor][i][0]-vm[flavor][i+1][0])>=8:
                vm[flavor][i][0] = round((vm[flavor][i-1][0]+vm[flavor][i+1][0])/2.0)
def feature_day_amount(vm,flavorName,now,last):

    '''
    x: [x1,x2,...,xn], subscript n reprensent day of month or day of year
    xi:[today_amount,last_2days_amount,last_week_amount,last_2week_amount,day_of_week,request_timeframe]
    '''

    feature = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0]
    #,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    if now==last :
        vm[flavorName][-1][0] +=1
    else :
        [year, month, day] = now.split('-')
        day = int(day)
        [year1, month1, day1] = last.split('-')
        day1 = int(day1)

        if month == month1:
            while (day - day1) != 1:
                day1 += 1
                for flavorName_ in vm.keys():
                    vm[flavorName_].append(feature[:])
                    vm[flavorName_][-1][-1] = year+'-'+month+'-'+str(day1)
            if day - day1 == 1:
                for flavorName_ in vm.keys():
                    vm[flavorName_].append(feature[:])
                    vm[flavorName_][-1][-1] = now
        else:
            for flavorName_ in vm.keys():
                vm[flavorName_].append(feature[:])
                vm[flavorName_][-1][-1] = now
        vm[flavorName][-1][0] +=1
def feature_others(vm):

    '''
    construct xi ,i =1,2,3...
    you can add any other features you want as:
    vm[flavorName_][0][i][...] = your_function(),but you should change the length in line
    'vm[flavorName_][0].append([0,0,0,0,0,0])' in function feature_x() at the same time
    '''
    cpu_disk = {"flavor1":[1,1],"flavor2":[1,2], "flavor3":[1,4],"flavor4":[2,2],
    "flavor5":[2,4], "flavor6": [2,8] ,"flavor7": [4,4] ,"flavor8": [4,8] ,
    "flavor9":[4,16],"flavor10": [8,8] ,"flavor11": [8,16],"flavor12": [8,32],
    "flavor13":[16,16],"flavor14":[16,32],"flavor15":[16,64]}

    for flavorName_ in vm.keys():
	    for i in range(len(vm[flavorName_])):
                #vm[flavorName_][i][1] = dif_nday(flavorName_, i, vm, 1)
                vm[flavorName_][i][1] = dif_nday(flavorName_, i, vm, 2)
                vm[flavorName_][i][2] = dif_nday(flavorName_, i, vm, 3)
                vm[flavorName_][i][3] = dif_nday(flavorName_, i, vm, 4)
                vm[flavorName_][i][4] = dif_nday(flavorName_, i, vm, 5)
                #vm[flavorName_][i][6] = num_nday_ago(flavorName_, i, vm, 1)
                #vm[flavorName_][i][7] = num_nday_ago(flavorName_, i, vm, 2)
                #vm[flavorName_][i][8] = num_nday_ago(flavorName_, i, vm, 3)
                vm[flavorName_][i][5] = num_nday_ago(flavorName_, i, vm, 4)
                vm[flavorName_][i][6] = num_nday_ago(flavorName_, i, vm, 7)
                vm[flavorName_][i][7] = dif_day_order2(flavorName_, i, vm)
                #vm[flavorName_][i][12] = dif_ndayamount_order1(flavorName_, i, vm, 2)
                #vm[flavorName_][i][13] = dif_ndayamount_order1(flavorName_, i, vm, 3)
                #vm[flavorName_][i][14] = dif_ndayamount_order1(flavorName_, i, vm, 4)
                #vm[flavorName_][i][15] = dif_ndayamount_order1(flavorName_, i, vm, 5)
                vm[flavorName_][i][8] = last_nday_amount(flavorName_, i, vm, 2)
                vm[flavorName_][i][9] = last_nday_amount(flavorName_, i, vm, 3)
                #vm[flavorName_][i][18] = last_nday_amount(flavorName_, i, vm, 4)
                #vm[flavorName_][i][19] = last_nday_amount(flavorName_, i, vm, 5)
                vm[flavorName_][i][10] = i + 1
                vm[flavorName_][i][11] = average7days(flavorName_, i, vm)
                #vm[flavorName_][i][22] = min7days(flavorName_, i, vm)
                vm[flavorName_][i][12] = max7days(flavorName_, i, vm)
                vm[flavorName_][i][13] = std7days(flavorName_, i, vm)
                vm[flavorName_][i][14] = average14days(flavorName_, i, vm)
                #vm[flavorName_][i][26] = min14days(flavorName_, i, vm)
                vm[flavorName_][i][15] = max14days(flavorName_, i, vm)
                vm[flavorName_][i][16] = std14days(flavorName_, i, vm)
                vm[flavorName_][i][17] = cpu_disk[flavorName_][0]
                vm[flavorName_][i][18] = cpu_disk[flavorName_][1]
                day_of_week(flavorName_, i, vm)
                # del vm[flavorName_][i][0]
def average7days(flavorName_,i,vm):
    average = 0
    if i>5:
        for j in range(i-6,i+1):
            average += vm[flavorName_][j][0]
        return round(average/7.0,4)
    else:
        return None
def min7days(flavorName_,i,vm):
    min_ = []
    if i>5:
        for j in range(i-6,i+1):
            min_.append(vm[flavorName_][j][0])
        return min(min_)
    else:
        return None
def max7days(flavorName_,i,vm):
    max_ = []
    if i > 5:
        for j in range(i - 6, i + 1):
            max_.append(vm[flavorName_][j][0])
        return max(max_)
    else:
        return None
def std7days(flavorName_,i,vm):
    std = 0
    if i>5:
        average = average7days(flavorName_,i,vm)
        for j in range(i-6,i+1):
            std += ((vm[flavorName_][j][0])-average)**2
        return round(std/7.0,4)
    else:
        return None
def average14days(flavorName_,i,vm):
    average = 0
    if i > 12:
        for j in range(i - 13, i + 1):
            average += vm[flavorName_][j][0]
        return round(average/14.0,4)
    else:
        return None
def min14days(flavorName_,i,vm):
    min_ = []
    if i>12:
        for j in range(i-13,i+1):
            min_.append(vm[flavorName_][j][0])
        return min(min_)
    else:
        return None
def max14days(flavorName_,i,vm):
    max_ = []
    if i > 12:
        for j in range(i - 13, i + 1):
            max_.append(vm[flavorName_][j][0])
        return max(max_)
    else:
        return None
def std14days(flavorName_,i,vm):
    std = 0
    if i > 12:
        average = average7days(flavorName_, i, vm)
        for j in range(i - 13, i + 1):
            std += ((vm[flavorName_][j][0]) - average) ** 2
        return round(std/14.0,4)
    else:
        return None

def num_nday_ago(flavorName,i,vm,n):
    dif = 0
    if i > (n-1):
        dif = vm[flavorName][i - n][0]
    else:
        dif = None
    return dif
def dif_nday(flavorName,i,vm,n):
    dif = 0
    if i > (n-1):
        dif = vm[flavorName][i][0] - vm[flavorName][i - n][0]
    else:
        dif = None
    return dif
def last_nday_amount(flavorName,i,vm,n):
    amount = 0
    if i > (n-1):
        for j in range(i - n, i + 1):
            amount += vm[flavorName][j][0]
    else:
        amount = None
    return amount
def dif_day_order2(flavorName,i,vm):
    if i >=2:
        dif = dif_nday(flavorName,i,vm,1)-dif_nday(flavorName,i-1,vm,1)
        return dif
    else:
        return None
def dif_ndayamount_order1(flavorName,i,vm,n):
    a = last_nday_amount(flavorName,i,vm,n)
    b = last_nday_amount(flavorName,i-1,vm,n)
    if a!=None and b!=None:
        dif = a-b
        return dif
    else:
        return None
def day_of_week(flavorName,i,vm):

    '''
    label modeling
    '''
    [year,month,day]=vm[flavorName][i][-1].split('-')

    dt = datetime(int(year), int(month), int(day))
    vm[flavorName][i][-1] = dt.weekday()+1

'''
generate label
'''
def label_y(vm,span):
    '''
    y: [forward_1day_amount,forward_1week_amout,forward_2week_amout]

    '''
    for flavorName_ in vm.keys():
        for i in range(len(vm[flavorName_])):
            vm[flavorName_][i] +=[forward_nday_amount(i,flavorName_,vm,span)]
def forward_nday_amount(i,flavorName,vm,span):
    amount = 0
    if (len(vm[flavorName])-i)<=span:
        amount = None
    else:
        for j in range(i+1,i+1+span):
            amount += vm[flavorName][j][0]
    return amount

'''dataset precece'''
def pressece(vm,input_infor,span):
    test_set = []
    for flavorName in input_infor['flavor']:
        test_set.append(vm[flavorName][-1])
    for flavorName_ in vm.keys():
        vm[flavorName_] = vm[flavorName_][14:-span]
        vm[flavorName_] = vm[flavorName_][-60:]
        #vm[flavorName_] = vm[flavorName_][0:49]+vm[flavorName_][59:]
    return test_set
def reconstr(vm,index):
    dataSet = []
    for i in range(len(vm['flavor1'])):
        for flavor in index:
            dataSet.append(vm[flavor][i])
    return dataSet
def trainingSet(raw_dataSet,input_infor,space = 'partial',train_type='merge'):
    vm, test_set = feature_modeling(raw_dataSet,input_infor)
    if space == 'total':
        if train_type == 'merge':
            tpye_class = [['flavor1', 'flavor2', 'flavor3','flavor4', 'flavor5', 'flavor6', 'flavor7', 'flavor8', 'flavor9', 'flavor10',\
                       'flavor11', 'flavor12', 'flavor13', 'flavor14', 'flavor15']]
        test_set = [test_set]
    if space == 'partial':
        if train_type == 'merge':
            tpye_class = [input_infor['flavor']]
            test_set = [test_set]
        if train_type == 'seperate':
            tpye_class = [[input_infor['flavor'][i]] for i in range(len(input_infor['flavor']))]
            testSet = []
            for data in test_set:
                testSet.append([data])
            test_set = testSet
    trainSet = []
    for index in tpye_class:
        trainSet.append(reconstr(vm,index))
    return trainSet,test_set
