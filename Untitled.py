
# coding: utf-8

# In[23]:


import numpy as np
from collections import namedtuple





Result = namedtuple('Result', ('nfev', 'cost', 'gradnorm', 'x'))

Result.__doc__ = """Результаты оптимизации



Attributes

----------

nfev : int

    Полное число вызовов модельной функции

cost : 1-d array

    Значения функции потерь 0.5 sum(y - f)^2 на каждом итерационном шаге.

    В случае метода Гаусса—Ньютона длина массива равна nfev, в случае ЛМ-метода

    длина массива — менее nfev

gradnorm : float

    Норма градиента на финальном итерационном шаге

x : 1-d array

    Финальное значение вектора, минимизирующего функцию потерь
    """
def gauss_newton(y, f, j, x0, k=1, tol=1e-4):
    nfev = 0
    cost = [] #значе6ние потерь
    #x норнма градиента
    
    x=x0.copy()
    gradnorm = 2 * tol
    delta_x = np.full.like(x0, 2*tol) #ranshe bil grad a ne delta
    while np.linalg.norm(delta_x) > tol:
        nfev+=1
        residual = y - f(*x) #raznitsa y i f
        cost.append( 0.5 * residual @ residual) #@ permnozhaet matritsy
        jac = j(*x)
        grad = jac.T @ residual
        gradnorm = np.linalg.norm(grad) # np.sqrt(grad @ grad)
        
        delta_x = np.linalg.solve(jac.T @ jac, grad)
        x+= k * delta_x
    cost = np.array(cost)
    return Result(nfev, cost, gradnorm, x)


def a(t,a,b): # a i b eto x
    return a * t + b #t nash numpy masiiv
def j(t,a,b):
    j=np.empty((t.size,2))
    j[:, 0] = t
    j[:, 1] = 1
    return j
a = 1.0
b = 2.0
t = np.arange(10)
y = f(t, a, b) + np.random.rand(t.size) - 0.5 # chtoby srednee = 0

#def func(*x):
    #return f(t, *x) eto lambda

result = gauss_newton(
    y=y,
    f = lambda *x: f(t, *x),
    j = lambda *x: j(t, *x),
    x0 = np.array([5.0, -7.0]),
)
print(result)


#b * exp (-at)
           


# In[24]:


def f(a, b, c):
    return a * b + c 
x=[1,2,3]
f(*x)


# In[ ]:


b * exp (-at) 


# In[28]:


def tsk():
    a = 0,75
    b = 2
    c = 0.5
    x0 = [1,1,1]
    n = 30
    t = np.linspace (0, 10, n)
    y = f(t, x) + np.random.normal (0, 0.1, n)
    tsk = b * exp (-at)*t**2 + c
    return tsk

# uslovie takoe chto pri k=1 alg ne rabotaet

