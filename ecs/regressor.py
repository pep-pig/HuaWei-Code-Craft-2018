# coding=utf-8
#permit import
import cv
from math import log
import random


def binSplitDataSet(dataSet, feature, value):
    index = [dataSet[feature][i] > value for i in range(len(dataSet[feature]))]
    index0 = []
    index1 = []
    for i in range(len(index)):
        if index[i]:
            index0.append(i)
        else:
            index1.append(i)
    mat0 = [[] for _ in range(len(dataSet))]
    mat1 = [[] for _ in range(len(dataSet))]
    for i in range(len(dataSet)):
        mat0[i] = [dataSet[i][j] for j in index0]
        mat1[i] = [dataSet[i][j] for j in index1]
    return mat0, mat1

def leaf_mean(dataSet):  # returns the value used for each leaf
    return sum(dataSet[-1]) / len(dataSet[-1])

def variance(dataSet):
    variance_ = sum([(dataSet[-1][i] - sum(dataSet[-1]) / len(dataSet[-1])) ** 2 for i in range(len(dataSet[-1]))])
    return variance_

def chooseBestSplit(dataSet, depth, ops=[1, 15, 10], ratio='log'):
    convergent_criterion = ops[0];
    tolN = ops[1];
    maxDepth = ops[2]

    # exit cond 0:depth>ops[2]
    if depth >= maxDepth:
        return None, leaf_mean(dataSet), None
    # exit cond 1:all the value in the node is the same
    if len(set(dataSet[-1])) == 1:
        return None, leaf_mean(dataSet), None

    n = len(dataSet)
    S = variance(dataSet)
    bestS = S;
    bestIndex = 0;
    bestValue = 0

    if ratio == 'log':
        index = random.sample(range(n - 1), k=int(log(len(dataSet), 2)))
    if ratio == '1/3':
        index = random.sample(range(n - 1), k=int(0.4 * len(dataSet)))
    else:
        index = range(n - 1)
    for featIndex in index:
        for splitVal in set(dataSet[featIndex]):
            mat0, mat1 = binSplitDataSet(dataSet, featIndex, splitVal)
            if (len(mat0[-1]) < tolN) or (len(mat1[-1]) < tolN):
                continue
            newS = variance(mat0) + variance(mat1)
            if newS < bestS:
                bestIndex = featIndex
                bestValue = splitVal
                bestS = newS
    if (S - bestS) < convergent_criterion:
        return None, leaf_mean(dataSet), None

    # exit cond3：least number of sample contained in a leafnode
    mat0, mat1 = binSplitDataSet(dataSet, bestIndex, bestValue)
    if (len(mat0[-1]) < tolN) or (len(mat1[-1]) < tolN):
        return None, leaf_mean(dataSet), None
    varDecrease = S - bestS
    # returns the best feature to split on and the value used for that split
    return bestIndex, bestValue, varDecrease

def createTree(dataSet, ops=[1, 10, 6], depth=0, subfeat_ratio='log'):


    if ops[2] <= 0:
        ops[2] = 1
    feat, val, varDecrease = chooseBestSplit(dataSet, depth, ops, ratio=subfeat_ratio)
    depth += 1
    if feat == None:
        return val
    else:
        retTree = {}
        retTree['spInd'] = feat
        retTree['spVal'] = val
        retTree['varDecrease'] = varDecrease
        lSet, rSet = binSplitDataSet(dataSet, feat, val)
        retTree['left'] = createTree(lSet, ops, depth)
        retTree['right'] = createTree(rSet, ops, depth)
        return retTree

def prune(tree, testData):
    if shape(testData)[0] == 0:
        return getMean(tree)  # if we have no test data collapse the tree
    if (isTree(tree['right']) or isTree(tree['left'])):  # if the branches are not trees try to prune them
        lSet, rSet = binSplitDataSet(testData, tree['spInd'], tree['spVal'])
    if isTree(tree['left']): tree['left'] = prune(tree['left'], lSet)
    if isTree(tree['right']): tree['right'] = prune(tree['right'], rSet)

    # if they are now both leafs, see if we can merge them
    if not isTree(tree['left']) and not isTree(tree['right']):
        lSet, rSet = binSplitDataSet(testData, tree['spInd'], tree['spVal'])
        errorNoMerge = sum(power(lSet[:, -1] - tree['left'], 2)) + \
                       sum(power(rSet[:, -1] - tree['right'], 2))
        treeMean = (tree['left'] + tree['right']) / 2.0
        errorMerge = sum(power(testData[:, -1] - treeMean, 2))
        if errorMerge < errorNoMerge:
            print("merging")
            return treeMean
        else:
            return tree
    else:
        return tree

def getMean(tree):
    '''
    get the mean of all  leafnodes
    '''
    if isTree(tree['right']):
        tree['right'] = getMean(tree['right'])
    if isTree(tree['left']):
        tree['left'] = getMean(tree['left'])
    return (tree['left'] + tree['right']) / 2.0

def feature_importance(tree, tolFeature):
    featImportance = [0 for _ in range(tolFeature)]
    for feature in range(tolFeature):
        featImportance[feature] = getImportance(tree, feature)
    return featImportance

def getImportance(tree, feature):
    # condition1: both left and right is leafnode
    if not isTree(tree):
        return 0
    if not (isTree(tree['left'])) and not (isTree(tree['right'])):
        if tree['spInd'] == feature:
            return tree['varDecrease']
        else:
            return 0
    # condition2：left child is tree
    if isTree(tree['left']):
        if tree['spInd'] == feature:
            varDecrease = tree['varDecrease'] + getImportance(tree['left'], feature)
        else:
            varDecrease = getImportance(tree['left'], feature)
    else:
        if tree['spInd'] == feature:
            varDecrease = tree['varDecrease']
        else:
            varDecrease = 0
    # condition3：right child is tree
    if isTree(tree['right']):
        varDecrease += getImportance(tree['right'], feature)
    return varDecrease

def isTree(obj):

    return (type(obj).__name__ == 'dict')

def singleForecast(tree, inData):
    '''

    inData:[x(1),x(2),...,x(n)]
    '''
    # get into leafnodes
    if not isTree(tree):
        return tree

    if inData[tree['spInd']] > tree['spVal']:
        if isTree(tree['left']):
            return singleForecast(tree['left'], inData)
        else:
            return float(tree['left'])
    else:
        if isTree(tree['right']):
            return singleForecast(tree['right'], inData)
        else:
            return float(tree['right'])

def datasetForecast(tree, testData):
    m = len(testData)
    yHat = []
    for i in range(m):
        yHat.append(singleForecast(tree, testData[i]))
    return yHat

class RandomForest(object):
    '''
    row sample：bagging
    column sample：random
    '''
    def __init__(self,n_estimators=100,ops=[0.1,2,10000],subfeat_ratio='log'):
        self.n_estimators = n_estimators
        self.ops = ops
        self.subfeat_ratio = subfeat_ratio
        self.estimators = []


    def random_sample(self, dataSet):
        '''
        有放回的行采样
        '''
        dataSet_row = []
        indexs = random.choices(list(range(0, len(dataSet))), k=len(dataSet))
        a = set(indexs)
        for index in indexs:
            dataSet_row.append(dataSet[index])
        dataset_col = [[] for _ in range(len(dataSet_row[0]))]
        for i in range(len(dataSet_row[0])):
            for j in range(len(dataSet_row)):
                dataset_col[i].append(dataSet_row[j][i])
        return dataSet_row, dataset_col

    def fit(self,dataSet):
        self.estimators = []
        for i in range(self.n_estimators):
            dataSet_row, dataSet_col = self.random_sample(dataSet)
            myTree = createTree(dataSet_col,self.ops,subfeat_ratio = self.subfeat_ratio)
            self.estimators.append(myTree)

    def predict(self,testSet):
        yHat = [0 for _ in range(len(testSet))]
        for estimator in self.estimators :
            yHat_n = datasetForecast(estimator, testSet)
            for i in range(len(yHat)):
                yHat[i] += yHat_n[i]
        yHat = [round(yHat[i]/self.n_estimators,1) for i in range(len(yHat))]
        return yHat

class GBDT(object):

    def __init__(self,stopcond=0.1, m=6 ,ops = [0.1,2,6]):
        self.estimators = []
        self.m = m
        self.stopcond = stopcond
        self.ops = ops
    def fit(self,dataSet,step):
        self.estimators = []
        dataSet_col = transpose(dataSet)
        #del dataSet_col[0]
        yHat = [0 for i in range(len(dataSet))]
        for i in range(self.m):
            #print('creating tree:', i)
            r = [(dataSet_col[-1][j] - yHat[j]) for j in range(len(yHat))]
            if i >=1:
                dataSet_col[-1] =[step* r[k] for k in range(len(r))]
            else:
                dataSet_col[-1] = r
            myTree = createTree(dataSet_col, self.ops, subfeat_ratio='1')
            self.estimators.append(myTree)
            dataSet = transpose(dataSet_col)
            yHat=datasetForecast(myTree,dataSet)

    def predict(self,testSet,weight):
        yHat = [0 for _ in range(len(testSet))]
        j = 1
        for estimator in self.estimators:
            yHat_n = datasetForecast(estimator, testSet)
            for i in range(len(yHat_n)):
                if yHat_n[i]<0:
                    yHat_n[i] = 0
            for i in range(len(yHat)):
                if j <=1 :
                    yHat[i] += yHat_n[i]
                else:
                    yHat[i] += weight*yHat_n[i]
            j += 1
        return yHat

    
    def featImportance(self,tolFeatures):
        featImp = [0 for _ in range(tolFeatures)]
        for tree in self.estimators:
            featImportance_m = feature_importance(tree,tolFeatures)
            for i in range(tolFeatures):
                featImp[i] += featImportance_m[i]
        sum_importance = sum(featImp)
        featImp = [featImp[i]/sum_importance for i in range(tolFeatures)]
        return featImp

class StackModel(object):
    pass
def transpose(dataSet):
    dataset_T = []
    for i in range(len(dataSet[0])):
        dataset_T.append([dataSet[j][i] for j in range(len(dataSet))])
    return dataset_T

