
#here is the code where we define Newtons Method

def deriv(x, func): #works for analytic functions !
    h = 1e-5
    return (func(x+h)-func(x-h))/(2*h) #using the symmetric derivative
       

def newtons_method(func, x0):
    diff = 1 #arbitraty value
    while diff > 1e-7:
        x1 = x0 - (func(x0)/deriv(x0,func)) #solve for next point
        diff = abs(func(x0) - func(x1))
        x0 = x1
        
    #x0 = round(x0,2)
    func_x0 = func(x0)
   # func_x0 = round(func_x0,2)
    return(x0, func_x0)


if __name__ == "__main__":
    def f(x):
        return x**2 +1
    res = newtons_method(f,1j)
    print(res)
    
    
    
