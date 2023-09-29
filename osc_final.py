from pyfirmata2 import Arduino
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Cursor, Slider, Button, CheckButtons, RadioButtons
from mpldatacursor import datacursor


# Creates a scrolling data display
class RealtimePlotWindow:

    def __init__(self):

        # create a plot window
        self.fig, self.ax = plt.subplots()
        plt.subplots_adjust(left=0.15, bottom=0.25)
        plt.grid(True)
        plt.title(label="Oscilloscope", fontsize=20, color="green")
        plt.ylabel('Voltage')
        plt.figtext(.03, 0.93, 'Volts/div')
        datacursor()

        # adjust radio buttons
        rax = plt.axes([0.01, 0.01, 0.12, 0.20], facecolor ='white')
        self.radio = RadioButtons(rax, ['V (p-p)', 'Freq Ch 0', 'Freq Ch 1'], [False, False, False], activecolor='r')


        # plotbuffer
        self.plotbuffer = np.zeros(500)
        self.plotbuffer1 = np.zeros(500)

        # create  empty lines
        self.line, = self.ax.plot(self.plotbuffer, linewidth=0.75)
        self.line1, = self.ax.plot(self.plotbuffer1, linewidth=0.75)

        # axis
        self.ax.set_ylim(-5, 5)

        # ringbuffer which accumluates the samples
        # It's emptied every time when the plot window below
        # does a repaint
        self.ringbuffer = []
        self.ringbuffer1 = []

        # start the animation
        self.ani = animation.FuncAnimation(self.fig, self.update, interval=1)

    # updates the plot
    def update(self, data):

        # add new data to the buffer
        self.plotbuffer = np.append(self.plotbuffer, self.ringbuffer)
        self.plotbuffer1 = np.append(self.plotbuffer1, self.ringbuffer1)

        self.v_max = np.max(self.plotbuffer)
        self.v_min = np.min(self.plotbuffer)
        self.v1_max = np.max(self.plotbuffer1)
        self.v1_min = np.min(self.plotbuffer1)

        #radio buttons
        def color(labels):
            if (labels == 'V (p-p)'):
                if (self.line.get_visible() == True and self.line1.get_visible() == False):
                    print("Ch0 >>>>> V(p-p)= ", np.round((self.v_max - self.v_min),2))
                elif (self.line1.get_visible() == True and self.line.get_visible() == False):
                    print("Ch1 >>>>> V(p-p)= ", np.round((self.v1_max - self.v1_min),2))
                else:
                    print("Ch0 >>>>> V(p-p)= ", np.round((self.v_max - self.v_min),2), "     Ch1 >>>>> V(p-p)= ", np.round((self.v1_max - self.v1_min),2))

            elif (labels == 'Freq Ch 0'):
                print(self.plotbuffer[10:40])
            else:        
                print(self.plotbuffer1[10:40])
        
        self.radio.on_clicked(color)



        # only keep the 500 newest ones and discard the old ones
        self.plotbuffer = self.plotbuffer[-500:]
        self.ringbuffer = []

        # only keep the 500 newest ones and discard the old ones
        self.plotbuffer1 = self.plotbuffer1[-500:]
        self.ringbuffer1 = []        
        

        # set the new 500 points of channel 0 and 1
        self.line.set_ydata(self.plotbuffer)
        self.line1.set_ydata(self.plotbuffer1)
        return self.line,self.line1

    # appends data to the ringbuffer
    def addData(self, v):
        self.ringbuffer.append(v)

    # appends data to the ringbuffer1
    def addData1(self, v):
        self.ringbuffer1.append(v)

    def rad_button(self):
        print(self.plotbuffer[10:40])



# Create an instance of an animated scrolling window
realtimePlotWindow = RealtimePlotWindow()

# Creating axes for channel offset sliders
axch0 = plt.axes([0.25, 0.15, 0.45, 0.03], facecolor='lightgoldenrodyellow')
off_ch0 = Slider(axch0, 'Offset Channel 0', -5.0, 5.0, 0)

axch1 = plt.axes([0.25, 0.1, 0.45, 0.03], facecolor='lightgoldenrodyellow')
off_ch1 = Slider(axch1, 'Offset Channel 1', -5.0, 5.0, 0)

#Creating volts/div sliders
vax_ch0 = plt.axes([0.03, 0.25, 0.0125, 0.63], facecolor='lightgoldenrodyellow')
volt_ch0 = Slider(vax_ch0, 'Ch 0', 0, 10, 1, orientation = "vertical")

vax_ch1 = plt.axes([0.06, 0.25, 0.0125, 0.63], facecolor='lightgoldenrodyellow')
volt_ch1 = Slider(vax_ch1, 'Ch 1', 0, 10, 1, orientation = "vertical")

# Creating time/div sliders
#time_up = plt.axes([0.25, 0.05, 0.45, 0.03], facecolor='lightgoldenrodyellow')
#time_div = Slider(time_up, 'Time/div', 1, 100, 1)



def update_slider(val):
    ch0 = off_ch0.val
    ch1 = off_ch1.val
    vamp0 = volt_ch0.val
    vamp1 = volt_ch1.val
    def callBack(data):
        realtimePlotWindow.addData(5*vamp0*data+ch0)
    board.analog[0].register_callback(callBack)
    def callBack1(data):
        realtimePlotWindow.addData1(5*vamp1*data+ch1)
    board.analog[1].register_callback(callBack1)

 
# Call update function when slider value is changed
off_ch0.on_changed(update_slider)
off_ch1.on_changed(update_slider)
volt_ch0.on_changed(update_slider)
volt_ch1.on_changed(update_slider)


# sampling rate: 1000Hz
samplingRate = 1000

# called for every new sample which has arrived from the Arduino
def callBack(data):
    # send the sample to the plotwindow
    realtimePlotWindow.addData(5*data)

def callBack1(data):
    # send the sample to the plotwindow
    realtimePlotWindow.addData1(5*data)



#Checkbox Widget
lines = [realtimePlotWindow.line, realtimePlotWindow.line1]
labels = ["Channel 0", "Channel 1"]

label = [True, True] 
 
def func(label):
    index = labels.index(label)
    lines[index].set_visible(not lines[index].get_visible())
    realtimePlotWindow.fig.canvas.draw()
 
ax_check = plt.axes([0.8, 0.001, 0.15, 0.17])
plot_button = CheckButtons(ax_check, labels, label)
plot_button.on_clicked(func)

for r in plot_button.rectangles:
    r.set_facecolor("blue") 
    r.set_edgecolor("k")
    r.set_alpha(0.2) 

[ll.set_color("white") for l in plot_button.lines for ll in l]
[ll.set_linewidth(3) for l in plot_button.lines for ll in l]
for i, c in enumerate(["b", "r"]):
    plot_button.labels[i].set_color(c)
    plot_button.labels[i].set_alpha(0.7)




# Get the Ardunio board.
board = Arduino('COM3')

# Set the sampling rate in the Arduino
# This should not be less than 1ms
board.samplingOn(sample_interval=1)

# Register the callback which adds the data to the animated plot
board.analog[0].register_callback(callBack)
board.analog[1].register_callback(callBack1)

# Enable the callback
board.analog[0].enable_reporting()
board.analog[1].enable_reporting()


# show the plot and start the animation
plt.show()

# needs to be called to close the serial port
board.exit()

print("Terminated")