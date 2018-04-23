# coding=utf-8
#user defined import
import feature_engineering
import regressor
import cv
import os

def predict_vm(ecs_lines,input_lines):
    # Do your work from here#
    result = []
    if ecs_lines is None:
        print ('ecs information is none')
        return result
    if input_lines is None:
        print('input file information is none')
        return result
    #generate trainset and testset

    trainSet, predictSet = feature_engineering.trainingSet(ecs_lines, input_lines)
    #train_set, test_set, test_y = cv.timesplit(train_Set,len(input_lines['flavor']))

    # choose the best parameter searched by cv
    y = [5,9,2,2,36,26,5,44,11,1,22,14,0,3,1]
    maxScore = 0
    best_parameter = []
    for tree_number in [4,6,8,10]:
        for depth in [3,4]:
            for leaf_num in [4,5,6,8]:
                for step in [1.0]:
                    parameter = [tree_number, 0.1, 0.00000000001, leaf_num, depth]
                    # choose best model
                    print(tree_number, depth, leaf_num,step)
                    gbdt = regressor.GBDT(m=tree_number,ops=[parameter[2], parameter[3], parameter[4]])
                    # gbdt = regressor.GBDT(stopcond=parameter[1], m=parameter[0],
                                          # ops=[parameter[2], parameter[3], parameter[4]])
                    # using pre-trained model information
                    # gbdt.estimators = GBDT_tree.tree
                    yHat = []
                    i = 0
                    for train_set in trainSet:
                        gbdt.fit(train_set,1.0)
                        yHat += gbdt.predict(predictSet[i],1.0)
                        i += 1

                    yHat = list(map(round, yHat))
                    yHat = list(map(int, yHat))
                    score = cv.tic(yHat, y)
                    print("score:", score)
                    if score > maxScore:
                        maxScore = score
                        yHat_best = yHat
                        best_parameter = parameter
                        best_estimators = gbdt.estimators
                        featImp = gbdt.featImportance(len(train_set[0]) - 1)
    featImp = list(map(round,featImp,[4]*len(featImp)))
    print("maxScore", maxScore)
    print('best_parameter',best_parameter)
    print(featImp)
    print(yHat)
    return yHat

if __name__ == '__main__':
    ecsDataPath = "data_train.txt"
    ecs_infor_array = read_lines(ecsDataPath)
    yHat = predict_vm(ecs_infor_array)

