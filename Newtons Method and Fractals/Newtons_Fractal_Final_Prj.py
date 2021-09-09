"""created by Jordan and Colon
    Final project on Newtons method and the making of fractals
"""

import matplotlib.pyplot as plt
import numpy as np



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


def newtons_method(func, d_func, x0, step_lim,
                    tol, Prtlst=False):
    """
        Takes in the function, manually computed deriv, starting point,
    step_lim is how many iterations you want the method to take,
    tol is how exact you want your error of the sol to be (distance from zero),
    note we use this tol value elsewhere where it is needed

        The function returns the final step value, and arrays of the difference
    steps and other relevant information
        
        If Prtlst == True the you can see the step and diff to the next step at every iteration
    """
    diff = 1  # arbitraty value
    step = 0
    step_array = []
    diff_array = []
    while diff > tol and step < step_lim:
        step += 1
        if d_func(x0) == 0:
            print(f"function has zero derivative at {x0}")
            return 0, step_lim + 1
        x1 = x0 - (func(x0) / d_func(x0))  # solve for next point
        diff = abs(x0 - x1)
        if Prtlst == True:
            print(f"{x0:.3f} , {diff:.3f}")
        step_array.append(x0)
        diff_array.append(diff)
        x0 = x1
    if diff > tol:
        print(
            "failure to find root \n number of steps is \n {} n With the final step of {}".format(
                step, x0))
        return 0, step_lim + 1
    else:
        return x0, step


def fast_newtons_method(func, d_func, x0, step_lim, tol):
    """
        Same as "newtons_method, but just stripped down in order to allow for a
    faster computation
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


def data_construct(arange, brange, point, func, d_func, step_lim, tol):
    """
        "arange" defines the x range and b defines the y range for the box that contains the data,
    point is the number of points used to graph given (ypoints, xpoints)
    """
    I_arr = np.zeros((point[1], point[0])) #initializes array of steps for each x,y
    rootarr = np.zeros((point[1], point[0]), dtype=np.complex_) #not used but useful
    xarr = np.linspace(arange[0], arange[1], point[0]) # given amount of even points in arange
    yarr = np.linspace(brange[0], brange[1], point[1]) #given amount of even points in brange
    for k in range(len(xarr)): #creates step array
        for m in range(len(yarr)):
            rootarr[m][k], I_arr[m][k] = fast_newtons_method(func, d_func,
                                                        complex(xarr[k],
                                                                yarr[m]),
                                                        step_lim, tol)
    return xarr, yarr, I_arr, rootarr
def plot(arange, brange, point, func, title, d_func, step_lim, tol,
         figsize1=(20, 10),
         save = False):
    x, y, z, rootarr = data_construct(arange, brange, point, func, d_func,
                                      step_lim, tol)
    z_min = z.min()
    z_max = z.max()
    plt.figure(figsize=figsize1)
    c = plt.pcolor(x, y, z, cmap='RdBu', vmin=z_min, vmax=z_max) #sets color scale using xarr, yarr, and I_arr
    plt.title(title)
    plt.colorbar(c)
    if save == True:
        plt.savefig('{}.png'.format(title)) #saves as png
    plt.show()


def singraph(step_lim, tol): #shows graph for sinx and its derivative
    func = lambda x: sin(x)
    d_func = lambda x: d_sin(x)
    arange = (-6, 6)
    brange = (-6, 6)
    point = (200, 100)
    title = 'sin(x)'
    plot(arange, brange, point, func, title, d_func, step_lim, tol)
    plt.close()
    arange = (-5.25, -4.2)
    brange = (-0.7, 0.7)
    title = 'sin(x) zoomed'
    plot(arange, brange, point, func, title, d_func, step_lim, tol)
    plt.close()

def exgraph(step_lim, tol): #shows graph for e^x and its derivative (no steps)
    func = lambda x: np.exp(x)
    d_func = lambda x: np.exp(x)
    step_lim = 50
    tol = 1e-10
    arange = (-10, 10)
    brange = (10, 20)
    point = (200, 100)
    title = "e**x - should be blank"
    plot(arange, brange, point, func, title, d_func, step_lim, tol)
    plt.close()

def polygraph(step_lim, tol): #shows graph for x^3 -1 and its derivative
    func = lambda x: x ** 3 - 1
    d_func = lambda x: 3 * x ** 2
    arange = (-6, 6)
    brange = (-6, 6)
    point = (200, 100)
    title = 'x^3 -1'
    plot(arange, brange, point, func, title, d_func, step_lim, tol)
    plt.close()
    arange = (-1, 1)
    brange = (-0.5, 0.6)
    title = 'x^3 -1 zoom'
    plot(arange, brange, point, func, title, d_func, step_lim, tol)
    plt.close()
if __name__ == "__main__":
    def f(x):
        return x ** 2 + 2

    step_lim = 20
    tol = 1e-10
    polygraph(step_lim, tol)
    exgraph(step_lim, tol)
    singraph(step_lim, tol)
