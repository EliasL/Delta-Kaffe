import wx
import threading
import sys, os
import urllib.request
import subprocess
import datetime


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    print(relative_path, base_path)
    return os.path.join(base_path, relative_path)

def ask(parent=None, message=''):
    dlg = wx.TextEntryDialog(parent, message)
    dlg.ShowModal()
    result = dlg.GetValue()
    dlg.Destroy()
    return result

def coffeeAnim():
    """Launches 'command' windowless and waits until finished"""
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    subprocess.Popen("python anim.py", startupinfo=startupinfo).wait()


class MyForm(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "DKaffe", size=(220, 90))
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap(resource_path("icon.ico"), wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)

        #Init variables
        self.timeUntilCheck = 0
        self.anim = threading.Thread(target=coffeeAnim)
        self.lastCoffee = self.getCoffeeTime()
        self.timeBetweenCheck = int(ask(self, "Sekund mellom kaffesjekk: "))

        # Add a panel so it looks the correct on all platforms
        panel = wx.Panel(self)
        self.timeLeftText = wx.StaticText(panel, -1, "Tid til kaffesjekk: 0", (50, 10))        
        self.timeSinceText = wx.StaticText(panel, -1, "Tid siden sist kaffe: 0", (50, 30))

        self.timer = wx.Timer(self) 
        self.Bind(wx.EVT_TIMER, self.updateTimer, self.timer)
        self.timer.Start(1000) 

            

    def getCoffeeTime(self):
        coffeeString = str(urllib.request.urlopen('http://pi.deltahouse.no/coffee.txt').read())
        return datetime.datetime.strptime(coffeeString, "b'1\\n%d. %B %Y %H:%M:%S'")

    def timeSinceLastCofee(self):
        t = (datetime.datetime.now() - self.lastCoffee)
        return t - datetime.timedelta(microseconds=t.microseconds)

    def updateTimer(self, event):
        self.timeUntilCheck -= 1
        if self.timeUntilCheck < 0:
            self.timeUntilCheck = self.timeBetweenCheck-1
            self.checkCoffee()
        self.timeLeftText.LabelText = f"Tid til kaffesjekk: {self.timeUntilCheck}"
        self.timeSinceText.LabelText = f"Tid siden sist kaffe: {self.timeSinceLastCofee()}"
        

    def checkCoffee(self):
        nowCoffee = self.getCoffeeTime()
        if self.lastCoffee != nowCoffee:
            self.lastCoffee = nowCoffee
            if not self.anim.isAlive():
                self.anim = threading.Thread(target=coffeeAnim, args=())
                self.anim.start()
        
        
# Run the program
if __name__ == '__main__':
    app = wx.App(False)
    frame = MyForm()
    frame.Show()
    app.MainLoop()
