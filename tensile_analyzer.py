import matplotlib.pyplot as plt
import matplotlib.lines as lines
import numpy as np
from sklearn.linear_model import LinearRegression
import scipy


class draggable_lines:
    def __init__(self, ax, kind, XorY,size):
        self.ax = ax
        self.c = ax.get_figure().canvas
        self.o = kind
        self.XorY = XorY

        if kind == "h":
            x = [-1, 1]
            y = [XorY, XorY]

        elif kind == "v":
            x = [XorY, XorY]
            y = [-1, 1]

        self.line = lines.Line2D(size, y, picker=5)
        self.ax.add_line(self.line)
        self.c.draw_idle()
        self.sid = self.c.mpl_connect('pick_event', self.clickonline)

    def clickonline(self, event):
        if event.artist == self.line:
            print("line selected ", event.artist)
            self.follower = self.c.mpl_connect("motion_notify_event", self.followmouse)
            self.releaser = self.c.mpl_connect("button_press_event", self.releaseonclick)

    def followmouse(self, event):
        if self.o == "h":
            self.line.set_ydata([event.ydata, event.ydata])
        else:
            self.line.set_xdata([event.xdata, event.xdata])
        self.c.draw_idle()

    def releaseonclick(self, event):
        if self.o == "h":
            self.XorY = self.line.get_ydata()[0]
        else:
            self.XorY = self.line.get_xdata()[0]

        self.c.mpl_disconnect(self.releaser)
        self.c.mpl_disconnect(self.follower)

def get_data(path,machine):
    print('attempting to load data')
    if machine == 'tinius':
        data = np.loadtxt(path,dtype="float",delimiter=',',skiprows=2)
        strain = data[:,3]/100
        stress = data[:,1]
    elif machine =='gom':
        data = np.loadtxt(path,dtype="float",delimiter=',',skiprows=2)
        strain = data[:,2]/100
        stress = data[:,1]
    else:
        data = np.loadtxt(path,dtype="float",delimiter=',',skiprows=2)
        strain = data[:,4]
        stress = data[:,3]
    
    return strain, stress

def get_boundaries(x,y):
    x_limits = [np.min(x)-(np.max(x))*.05, np.max(x)+(np.max(x))*.1]
    fig = plt.figure()
    ax = fig.add_subplot(111)
    line1 = draggable_lines(ax, "h", 0.5,x_limits)
    line2 = draggable_lines(ax, "h",50, x_limits)
    plt.xlim(x_limits)
    plt.plot(x,y)
    plt.show()
    return min(line1.XorY,line2.XorY), max(line1.XorY,line2.XorY)

def calculate_youngs(x,y,lower_percent,upper_percent): 
    #lower, upper =get_boundaries(x,y)
    lower = np.max(y) * lower_percent
    upper = np.max(y) * upper_percent
    lower_index = np.where(y>lower)[0][0]
    upper_index = np.where(y>upper)[0][0]
    y_trim = y[lower_index:upper_index]
    x_trim = x[lower_index:upper_index]  


    model = LinearRegression(fit_intercept=True).fit(np.reshape(x_trim,(-1,1)),y_trim)

    return model

def calculate_ys(x,y,model,offset):
    # plt.plot(x,y)
    # plt.axline((0,model.intercept_),slope=model.coef_[0],color= 'red')
    # plt.axline((offset,model.intercept_),slope=model.coef_[0],color= 'green')

    offset_intercept=model.intercept_-(model.coef_[0]*offset)

    actual_data_interp_function = scipy.interpolate.interp1d(x,y)

    dist_1 = lambda val: abs(actual_data_interp_function(val) - (offset_intercept + (model.coef_[0]*val)))

    #x=np.arange(0,0.02,0.0001)
    err=dist_1(x)
    lowband=x[err<20]
    lowmpa=actual_data_interp_function(lowband)
    
    #plt.plot(x,y)
    #plt.plot(x,err)
    #plt.plot(lowband,lowmpa)
    #plt.show()



    guess = model.coef_[0] * x[np.where(np.max(y))] + offset

    # interp_x = np.linspace(x[0],x[np.where(np.max(y))],100000)

    # closest_x = scipy.optimize.minimize(dist_1, x[1200], bounds=scipy.optimize.Bounds(lb=np.min(x), ub=np.max(x)/2),options = {'xatol' : 0.000001},method = 'Nelder-Mead').x[0]
    closest_x = scipy.optimize.minimize(dist_1, np.mean(lowband), bounds=scipy.optimize.Bounds(lb=lowband[0], ub=lowband[-1]),options = {'xatol' : 0.000001},method = 'Nelder-Mead').x[0]
    #closest_x = scipy.optimize.minimize(dist_1, x[8], bounds=scipy.optimize.Bounds(lb=np.min(x), ub=np.max(x)/2),method = 'BFGS').x[0]
    #closest_x = scipy.optimize.basinhopping(dist_1, x[0], niter = 100000).x[0]
    closest_y = actual_data_interp_function(closest_x)

    # plt.plot(closest_x,closest_y,'*')
    # plt.show()
   
    return closest_y

def calculate_uts(x,y):
    uts = np.max(y)
    return uts

def calculate_strain_at_break(x,y):
    strain = np.max(x)
    return strain


if __name__=='__main__':
    data_file = '/home/bradenmclain/TaffyData/CallibrationData/Taffy/174PH_1.csv'
    x, y = get_data(data_file)
    model = calculate_youngs(x,y,.3,.6)
    yield_strength_2 = calculate_ys(x,y,model,.03)
    yield_strength_2 = calculate_ys(x,y,model,.02)
    uts = calculate_uts(x,y)
    elongation = calculate_strain_at_break(x,y)
    print(f'Youngs Modulus is {model.coef_[0]} MPa')
    print(f'2% offset yield strength is: {yield_strength_2} MPa')
    print(f'the UTS is: {uts} MPa')
    print(f'the strain at break is: {elongation}%')
    f=open("dataLog.txt",'a')
    f.write(f"File: {data_file}\tYS_2: {yield_strength_2:3.3f} MPa\tUTS: {uts:3.3f} MPa\telongation: {elongation:3.3f}%\t Youngs: {model.coef_[0]:3.3f} MPa\n")
    f.close()
    plt.show()
