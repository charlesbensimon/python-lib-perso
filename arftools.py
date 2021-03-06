# -*- coding: utf-8 -*-

import sys
import numpy as np
from numpy import random
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from collections import namedtuple
from collections import Counter

Fonction = namedtuple("Fonction", ["f", "grad", "dim"])

def print_percent(n, N, callback=None):
    if N > 100:
        if n != 0 and (n+1)%(int(N/100)) != 0:
            return
    percentage = int(round((n*100.0)/N))
    result = str(percentage) +' %'
    if callback:
        result += ' : ' + str(callback())
        print(result)
    else:
        sys.stdout.write('\r'+ result)
        if percentage == 100:
            sys.stdout.write('\n')
        sys.stdout.flush()

def load_usps(filename='/users/Etu0/3000120/Master/ARF/TME2/2015_tme3_usps_train.txt'):
    with open(filename, "r") as f:
         f.readline()
         data = [ [ float(x) for x in l.split() ] for l in f if len(l.split()) > 2 ]
    tmp = np.array(data)
    return tmp[:, 1:], tmp[:, 0].astype(int)

def show_image(v):
    shapes = np.array(list(v.shape))
    total = shapes.prod()
    s = int(np.sqrt(total))
    plt.imshow(v.reshape((s,s)), cmap=cm.gray_r)
    
def separe_train_test(datay, ratio, balanced=False):
    
    classes = Counter(datay)
    train = np.zeros(0, dtype=int)
    test = np.zeros(0, dtype=int)
    
    if balanced:
        
        mClass, mCount = classes.most_common()[0]
        mCount_train = int(round(mCount * ratio))
        mCount_test = mCount - mCount_train
        for c in classes:
            indexes = np.where(datay == c)[0]
            random.shuffle(indexes)
            if len(indexes) < mCount:
                limit = int(round(len(indexes)*ratio))
                cTrain = indexes[:limit]
                cTest = indexes[limit:]
                nRepeats_train = int(np.ceil(mCount_train/float(len(cTrain))))
                nRepeats_test = int(np.ceil(mCount_train/float(len(cTest))))
                cTrain = np.tile(cTrain, nRepeats_train)
                cTest = np.tile(cTest, nRepeats_test)
                train = np.append(train, cTrain[:mCount_train])
                test = np.append(test, cTest[:mCount_test])
            else:
                train = np.append(train, indexes[:mCount_train])
                test = np.append(test, indexes[mCount_train:])
            
    else:
        
        for c in classes:
            indexes = np.where(datay == c)[0]
            random.shuffle(indexes)
            limit = int(round(len(indexes)*ratio))
            train = np.append(train, indexes[:limit])
            test = np.append(test, indexes[limit:])
        
    return train, test

def v2m(x):
    return x.reshape((1, x.size)) if len(x.shape)==1 else x
    
def v2col(x):
    return x.reshape((x.size, 1)) if len(x.shape)==1 else x
    
def v2row(x):
    return v2m(x)
    
def optimize_grad(fonc, eps=0.01, max_iter=100, xinit=None):
    
    if xinit == None:
        xinit = v2m(np.random.randn(fonc.dim))
    
    log_x = np.zeros((max_iter, fonc.dim))
    log_f = np.zeros((max_iter, 1))
    log_grad = np.zeros((max_iter, fonc.dim))
    
    log_x[0] = xinit
    log_f[0] = fonc.f(xinit)
    log_grad[0] = fonc.grad(xinit).reshape(fonc.dim)
    
    for i in range(max_iter - 1):
       log_x[i+1] = log_x[i] - eps*log_grad[i]
       log_f[i+1] = fonc.f(v2m(log_x[i+1]))
       log_grad[i+1] = fonc.grad(v2m(log_x[i+1])).reshape(fonc.dim)
    
    return (log_x, log_f, log_grad)

def to_array(x):
    """ Convert an vector to array if needed """
    if len(x.shape)==1:
        x=x.reshape(1,x.shape[0])
    return x


def gen_arti(centerx=1,centery=1,sigma=0.1,nbex=1000,data_type=0,epsilon=0.02):
    """ Generateur de donnees,
        :param centerx: centre des gaussiennes
        :param centery:
        :param sigma: des gaussiennes
        :param nbex: nombre d'exemples
        :param data_type: 0: melange 2 gaussiennes, 1: melange 4 gaussiennes, 2:echequier
        :param epsilon: bruit dans les donnees
        :return: data matrice 2d des donnnes,y etiquette des donnnees
    """
    if data_type==0:
         #melange de 2 gaussiennes
         xpos=np.random.multivariate_normal([centerx,centerx],np.diag([sigma,sigma]),nbex/2)
         xneg=np.random.multivariate_normal([-centerx,-centerx],np.diag([sigma,sigma]),nbex/2)
         data=np.vstack((xpos,xneg))
         y=np.hstack((np.ones(nbex/2),-np.ones(nbex/2)))
    if data_type==1:
        #melange de 4 gaussiennes
        xpos=np.vstack((np.random.multivariate_normal([centerx,centerx],np.diag([sigma,sigma]),nbex/4),np.random.multivariate_normal([-centerx,-centerx],np.diag([sigma,sigma]),nbex/4)))
        xneg=np.vstack((np.random.multivariate_normal([-centerx,centerx],np.diag([sigma,sigma]),nbex/4),np.random.multivariate_normal([centerx,-centerx],np.diag([sigma,sigma]),nbex/4)))
        data=np.vstack((xpos,xneg))
        y=np.hstack((np.ones(nbex/2),-np.ones(nbex/2)))

    if data_type==2:
        #echiquier
        data=np.reshape(np.random.uniform(-4,4,2*nbex),(nbex,2))
        y=np.ceil(data[:,0])+np.ceil(data[:,1])
        y=2*(y % 2)-1
    # un peu de bruit
    data[:,0]+=np.random.normal(0,epsilon,nbex)
    data[:,1]+=np.random.normal(0,epsilon,nbex)
    # on mélange les données
    idx = np.random.permutation((range(y.size)))
    data=data[idx,:]
    y=y[idx]
    return data,y

def plot_data(data,labels=None):
    """
    Affiche des donnees 2D
    :param data: matrice des donnees 2d
    :param labels: vecteur des labels (discrets)
    :return:
    """
    cols,marks = ["red", "green", "blue", "orange", "black", "cyan"],[".","+","*","o","x","^"]
    if labels is None:
        plt.scatter(data[:,0],data[:,1],marker="x")
        return
    for i,l in enumerate(sorted(list(set(labels.flatten())))):
        plt.scatter(data[labels==l,0],data[labels==l,1],c=cols[i],marker=marks[i])



def make_grid(data=None,xmin=-5,xmax=5,ymin=-5,ymax=5,step=20):
    """ Cree une grille sous forme de matrice 2d de la liste des points
    :param data: pour calcluler les bornes du graphe
    :param xmin: si pas data, alors bornes du graphe
    :param xmax:
    :param ymin:
    :param ymax:
    :param step: pas de la grille
    :return: une matrice 2d contenant les points de la grille
    """
    if data!=None:
        xmax, xmin, ymax, ymin = np.max(data[:,0]),  np.min(data[:,0]), np.max(data[:,1]), np.min(data[:,1])
    x, y =np.meshgrid(np.arange(xmin,xmax,(xmax-xmin)*1./step), np.arange(ymin,ymax,(ymax-ymin)*1./step))
    grid=np.c_[x.ravel(),y.ravel()]
    return grid, x, y


def plot_frontiere(data,f,step=20):
    """ Trace un graphe de la frontiere de decision de f
    :param data: donnees
    :param f: fonction de decision
    :param step: pas de la grille
    :return:
    """
    grid,x,y=make_grid(data=data,step=step)
    plt.contourf(x,y,f(grid).reshape(x.shape),colors=('gray','blue'),levels=[-1,0,1])

##################################################################"
class Classifier(object):
    """ Classe generique d'un classifieur
        Dispose de 3 méthodes :
            fit pour apprendre
            predict pour predire
            score pour evaluer la precision
    """
    def fit(self,x,y):
        raise NotImplementedError("fit non  implemente")
    def predict(self,x):
        raise NotImplementedError("predict non implemente")
    def score(self,x,y):
        return (self.predict(x)==y).mean()
