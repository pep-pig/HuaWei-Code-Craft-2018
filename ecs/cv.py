# coding=utf-8
from math import sqrt
import regressor


def split(dataSet,ratio):
    train_set=[]
    test_set =[]
    for i in range(0,int(ratio*len(dataSet))):
        train_set.append(dataSet[i])
    for i in range(int(ratio*len(dataSet)),len(dataSet)):
        test_set.append(dataSet[i])

    test_y = []
    for i in range(len(test_set)):
        test_y.append(test_set[i][-1])
    return train_set,test_set,test_y

def timesplit(dataSet,flavors):
    train_set = dataSet[0:-flavors]
    test_set = dataSet[-flavors:]
    test_y = []
    for i in range(len(test_set)):
        test_y.append(test_set[i][-1])
    return train_set,test_set,test_y

def ksplit(dataSet,train_index,test_index):
    train_set = []
    test_set =[]
    y = []
    for i in train_index:
        train_set.append(dataSet[i])
    for i in test_index:
        test_set.append(dataSet[i])
    for i in range(len(test_set)):
        y.append(test_set[i][-1])
    return train_set ,test_set, y

def tic(yHat, y):
    a = sqrt(sum([(yHat[i]-y[i])**2 for i in range(len(yHat))])/len(yHat))
    b = sqrt(sum([yHat[i]**2 for i in range(len(yHat))])/len(yHat))+sqrt(sum([y[i]**2 for i in range(len(y))])/len(yHat))
    score = 1-a/b
    return score

def Kfold(regressor,dataSet,type='standard',k=5,rollingstep = 7,rollinglen=0.7,testlen=7):
    score = [0 for _ in range(k)]
    if type == 'standard':
        for i in range(k):
            train_index = list(range(0, len(dataSet)))
            print('start kfold, round:',i)
            test_index = list(range(int(i/k*len(dataSet)),int((1+i)/k*len(dataSet))))
            for j in test_index:
                train_index.remove(j)
            train_set,test_set,y = ksplit(dataSet,train_index,test_index)
            regressor.fit(dataSet = train_set)
            yHat = regressor.predict(test_set)
            score[i] = tic(yHat, y)

    if type=='timeseries':
        score = [0 for i in range(k)]
        for i in range(k):
            train_set,test_set,y=split(dataSet,(i+1)/(k+1))
            regressor.fit(dataSet=train_set)
            yHat = regressor.predict(test_set[0:testlen])
            score[i] = tic(yHat, y[0:testlen])

    if type == 'rolling':
        score = [0 for i in range(k)]
        for i  in range(k):
            train_index = [range(int(i / k * len(dataSet)), int(rollinglen * len(dataSet) + i / k * len(dataSet)))]
            test_index = [i for i in range(train_index[-1]+1,train_index[-1]+1+testlen)]
            train_set, test_set, y = ksplit(dataSet, train_index, test_index)
            regressor.fit(dataSet=train_set)
            yHat = regressor.predict(test_set)
            score[i] = tic(yHat, y)
    if type == 'no_cv':
        score = [0]
        train_set,test_set,y = timesplit(dataSet,flavors =15)
        regressor.fit(dataSet=train_set)
        yHat = regressor.predict(test_set)
        score[0] = tic(yHat,y)
        return score
    score.append(sum(score) / len(score))
    return score

def savefig(yHat,y,name):
    plt.close()
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.axis('auto')
    ax.set_xlabel('flavor')
    ax.set_ylabel('predict')
    ax.scatter([i for i in range(len(y))], y, s=50, color='b')
    ax.plot(yHat,'-o', linewidth=1.0)
    plt.savefig(name)

class GridSearchCV(object):
    #TODO 改成*kagw更加简洁
    def __init__(self,tpye ='GBDT',m = [1],stopcond=[0.1],n_estimators=100,subfeat_ratio = 'log',ops =[0.1,2,6],variance=[0.1],leaf_num=[2],depth=[6]):
        if tpye == 'GBDT':
            self.hyperparameter = [m,stopcond,variance,leaf_num,depth]
            self.regressor = regressor.GBDT(m=6 ,stopcond=0.1, ops = ops)
        if tpye == 'RF':
            self.hyperparameter = [n_estimators,subfeat_ratio,variance,leaf_num,depth]
            self.regressor = regeressor.RandomForest(n_estimators=100,ops=[0.1,2,10000],subfeat_ratio='log')
    def gbdt_search(self,dataSet,kfoldtpye = 'standard'):
        #GBDT 算法的参数 ： 树的个数，树的深度，收敛条件
        hyperparameter = self.hyperparameter
        maxScore = 0
        k =1
        print('开始网格搜索')
        print("      树的个数  GBDT迭代停止条件  cart残差  cart叶子节点包含的最少样本数 cart数的深度  得分")
        for i in range(len(hyperparameter[0])):
            for j in range(len(hyperparameter[1])):
                for l in range(len(hyperparameter[2])):
                    for m in range(len(hyperparameter[3])):
                        for n in range(len(hyperparameter[4])):
                            parameter = [hyperparameter[0][i],hyperparameter[1][j],hyperparameter[2][l],
                                         hyperparameter[3][m],hyperparameter[4][n]]
                            self.regressor.m = parameter[0]
                            self.regressor.stopcond = parameter[1]
                            self.regressor.ops[0] = parameter[2]
                            self.regressor.ops[1] = parameter[3]
                            self.regressor.ops[2] = parameter[4]


                            score = Kfold(self.regressor,dataSet,type = kfoldtpye)
                            print('  第{}轮：{:^6}{:^16.2f}{:^16.2f}{:10}{:>20}{:^20.4f}'.format(k, parameter[0],parameter[1],parameter[2],parameter[3],parameter[4],score[-1]))
                            k +=1
                            if score[-1] > maxScore:
                                best_parameter = parameter
                                maxScore = score[-1]
        print("最优参数:{:^6}{:^16.2f}{:^16.2f}{:10}{:>20}{:^20.4f}".format(best_parameter[0],\
        best_parameter[1],best_parameter[2],best_parameter[3], best_parameter[4], maxScore))
        return best_parameter,maxScore

    def rf_search(self,dataSet,kfoldtpye = 'standard'):
        maxScore = 0
        for i in range(len(hyperparameter[0])):
            for j in range(len(hyperparameter[1])):
                for l in range(len(hyperparameter[2])):
                    for m in range(len(hyperparameter[3])):
                        for n in range(len(hyperparamter[4])):
                            parameter = [hyperparameter[0][i], hyperparameter[1][j], hyperparameter[2][l],
                                         hyperparameter[3][m], hyperparameter[4][n]]
                            self.regressor.n_estimators = parameter[0]
                            self.regressor.subfeat_ratio = parameter[1]
                            self.regressor.ops[0] = parameter[2]
                            self.regressor.ops[1] = parameter[3]
                            self.regressor.ops[2] = parameter[4]
                            score = Kfold(self.regeressor, dataSet,type = kfoldtpye)
                            print("stopcond:", parameter[0], "tree number:", parameter[1], "delta:", parameter[2],
                                  "leaf_number:", parameter[3], "depth:", parameter[4],
                                  "score:", score)
                            if score > maxScore:
                                best_parameter = parameter
                                maxScore = score
        print('maxScore:', maxScore)
        return best_parameter, maxScore