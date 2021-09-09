"""created by Jordan and Colon
    Final project on Newtons method and the making of fractals

    The goal or this project is to create fractals using Newtons Method

    Newtons Method is a way to algorithmically find roots of functions.

    Fractrals are produced when, given a starting point in Real numbers, you count how many steps Newtons Method takes to find a root. 
    If you map the number of steps to the starting point an imagine can be created that will result in a fractal!

    This code here is how we decided to approach this process!

"""

import matplotlib.pyplot as plt
import numpy as np

"""
We are simply defining functions to be used later here
"""

def deriv(x, func):  # works for analytic functions !
    h = 1e-5
    return (func(x + h) - func(x - h)) / (
            2 * h)  # using the symmetric derivative


def sin(x):
    return np.sin(x)


def d_sin(x):
    return np.cos(x)


def comp_sol(x):
    return x ** 3 - 1


def d_com_sol(x):
    return (3 * x) ** 2


def real_sol(x):
    return np.exp(x) - 5 * x


def d_real_sol(x):
    return np.exp(x) - 5





def fast_newtons_method(func, d_func, x0, step_lim, tol):
    """
        Takes in the function, manually computed deriv, starting point,
    step_lim is how many iterations you want the method to take,
    tol is how exact you want your error of the sol to be (distance from zero),
    note we use this "tol" value elsewhere where it is needed


        The function returns the final step value (which is an approximation of the found root)
        ,and how many steps (passes through the loop) it took to get to this point
        
    """
    diff = 1
    step = 0
    while diff > tol and step < step_lim:
        step += 1
        if d_func(x0) == 0:
            return 0, step_lim + 1
        x1 = x0 - (func(x0) / d_func(x0))
        diff = abs(x0 - x1)
        x0 = x1
    if diff > tol:
        return 0, step_lim + 1
    else:
        return x0, step


def data_construct(x_range, y_range, point, func, d_func, step_lim, tol):
    """
        "x_range" defines the x range and y_range defines the y range for the box that contains the data,
    point is the number of points used to graph given (ypoints, xpoints)
    """
    step_arr = np.zeros((point[1], point[0])) #initializes array of steps for each x,y
    rootarr = np.zeros((point[1], point[0]), dtype=np.complex_) #not used but useful for mathematical purposes
    xarr = np.linspace(x_range[0], x_range[1], point[0]) # arr of evenly spaced  points in x_range
    yarr = np.linspace(y_range[0], y_range[1], point[1]) # arr of evenly spaced  points in y_range
    for x in range(len(xarr)): 
        for y in range(len(yarr)):
            """
                EXTREMELY IMPORTANT STEP!

                Here we fill in two arrays with information located at (x,y) in the real plane.

                rootarr[x][y] is an approximation of the root found at (x,y)
                step_arr[x][y] is how many steps it took to a root starting at (x,y)

                We will use step_arr to create the plots. The rootarr is useful because sometimes
                the algorithm can take too many steps (step_lim) and thus to identify where this occurs
                can help programers analyze the function. 

            """
            rootarr[x][y], step_arr[x][y] = fast_newtons_method(func, d_func, 
                                                        complex(xarr[x],
                                                                yarr[y]),
                                                        step_lim, tol)
    return xarr, yarr, step_arr, rootarr
def plot(x_range, y_range, point, func, title, d_func, step_lim, tol,
         figsize1=(20, 10),
         save = False):
    x, y, z, rootarr = data_construct(x_range, y_range, point, func, d_func,
                                      step_lim, tol)
    z_min = z.min()
    z_max = z.max()
    plt.figure(figsize=figsize1)
    c = plt.pcolor(x, y, z, cmap='RdBu', vmin=z_min, vmax=z_max) #sets color scale using xarr, yarr, and step_arr
    plt.title(title)
    plt.colorbar(c)
    if save == True:
        plt.savefig('{}.png'.format(title)) #saves as png
    plt.show()


def singraph(step_lim, tol): #shows graph for sinx and its derivative
    func = lambda x: sin(x)
    d_func = lambda x: d_sin(x)
    x_range = (-6, 6)
    y_range = (-6, 6)
    point = (200, 100)
    title = 'sin(x)'
    plot(x_range, y_range, point, func, title, d_func, step_lim, tol)
    plt.close()
    x_range = (-5.25, -4.2)
    y_range = (-0.7, 0.7)
    title = 'sin(x) zoomed'
    plot(x_range, y_range, point, func, title, d_func, step_lim, tol)
    plt.close()

def exgraph(step_lim, tol): #shows graph for e^x and its derivative (no steps)
    func = lambda x: np.exp(x)
    d_func = lambda x: np.exp(x)
    step_lim = 50
    tol = 1e-10
    x_range = (-10, 10)
    y_range = (10, 20)
    point = (200, 100)
    title = "e**x - should be blank"
    plot(x_range, y_range, point, func, title, d_func, step_lim, tol)
    plt.close()

def polygraph(step_lim, tol): #shows graph for x^3 -1 and its derivative
    func = lambda x: x ** 3 - 1
    d_func = lambda x: 3 * x ** 2
    x_range = (-6, 6)
    y_range = (-6, 6)
    point = (200, 100)
    title = 'x^3 -1'
    plot(x_range, y_range, point, func, title, d_func, step_lim, tol)
    plt.close()
    x_range = (-1, 1)
    y_range = (-0.5, 0.6)
    title = 'x^3 -1 zoom'
    plot(x_range, y_range, point, func, title, d_func, step_lim, tol)
    plt.close()
if __name__ == "__main__":
    def f(x):
        return x ** 2 + 2

    step_lim = 20
    tol = 1e-10
    polygraph(step_lim, tol)
    exgraph(step_lim, tol)
    singraph(step_lim, tol)
