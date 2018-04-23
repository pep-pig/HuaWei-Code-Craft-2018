# coding=utf-8
import sys
import os
import predictor
import knapsack_problem

def main():
    print ('main function begin.')
    # if len(sys.argv) != 4:
    #       print ('parameter is incorrect!')
    #       print ('Usage: python esc.py ecsDataPath inputFilePath resultFilePath')
    #       exit(1)
    #Read the input files
    ecsDataPath ='data_train.txt'#sys.argv[1]
    inputFilePath ='input.txt'#sys.argv[2]
    resultFilePath ='output.txt'#sys.argv[3]

    ecs_infor_array = read_lines(ecsDataPath)
    input_file_array = read_lines(inputFilePath)

    input_infor = getinput(input_file_array)

    predic_result = predictor.predict_vm(ecs_infor_array, input_infor)
    server, utilization = knapsack_problem.assign(predic_result, input_infor)  # TODO 2

    result = []
    result.append(sum(predic_result))
    i = 0
    for flavor in input_infor['flavor']:
        result.append(flavor + ' ' + str(predic_result[i]))
        i += 1
    result.append('')
    result.append(len(server))
    for i in range(len(server)):
        string = str(i + 1)
        j = 1
        for value in server[i][1:]:
            if value != 0:
                string += '  ' + 'flavor' + str(j) + '  ' + str(value)
            j += 1
        result.append(string)

    # write the result to output file
    if len(result) != 0:
        write_result(result, resultFilePath)
    else:
        result.append("NA")
        write_result(result, resultFilePath)
    print('main function end.')

def getinput(input_lines):
    flavor = []
    cpu_num = input_lines[0].split(' ')[0]
    memory_num = input_lines[0].split(' ')[1]
    i = 3
    while input_lines[i] != '\n':
        flavor.append(input_lines[i].split(' ')[0])
        i += 1
    i += 1
    optimize = input_lines[i].strip('\n')
    i += 2
    end = int(input_lines[i + 1].split(' ')[0].split('-')[-1])
    start = int(input_lines[i].split(' ')[0].split('-')[-1])
    span = int(end-start)

    input_infor = {'cpu': cpu_num, 'memory': memory_num, 'flavor': flavor, 'optimize': optimize, 'span': span}
    return input_infor

def write_result(array, outpuFilePath):
    with open(outpuFilePath, 'w') as output_file:
        for item in array:
            output_file.write("%s\n" % item)

def read_lines(file_path):
    if os.path.exists(file_path):
        array = []
        with open(file_path, 'r') as lines:
            for line in lines:
                array.append(line)
        return array
    else:
        print('file not exist: ' + file_path)
        return None
if __name__ == "__main__":
    main()