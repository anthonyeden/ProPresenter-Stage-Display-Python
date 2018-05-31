![ProPresenter Stage Display for Python](https://mediarealm.com.au/wp-content/uploads/2017/07/ProPresenter-Stage-Display-Python.png)

# ProPresenter Stage Display for Python
An unofficial Python implementation of the [ProPresenter Stage Display](https://www.renewedvision.com/store.php?item=prostagedisplay).

Currently, this implementation is very basic and designed to implement only three basic features:

* Clock
* Current slide text
* Next slide text

This program has been designed to run on small devices such as the Raspberry Pi.

# How to setup - general instructions

1. Download the [software](https://github.com/anthonyeden/ProPresenter-Stage-Display-Python/archive/master.zip)
2. Install Python2
3. Copy _config-sample.json_ to _config.json_
4. Edit _config.json_ in a text editor and set the IP Address, Port Number, and Password for your ProPresenter Stage Display computer (found in _Preferences > Network_ of your ProPresenter PC).
5. Run _python StageDisplay.py_

# Installation on Raspberry Pi

1. [Download and install Raspbian Desktop](https://www.raspberrypi.org/downloads/raspbian/) on your Raspberry Pi
2. Connect your WiFi or Ethernet
3. Open Terminal and run the following commands:

```
sudo apt-get install python2 git
git clone https://github.com/anthonyeden/ProPresenter-Stage-Display-Python/
echo "@/home/pi/ProPresenter-Stage-Display-Python/start.sh" >> .config/lxsession/LXDE-pi/autostart
cp ProPresenter-Stage-Display-Python/config-sample.json ProPresenter-Stage-Display-Python/config.json
``` 

4. To edit the configuration, run this command:

```
nano ProPresenter-Stage-Display-Python/config.json
```

  Ensure you update the IP Address, Port Number & Password for your ProPresenter computer. On your ProPresenter computer, this can be setup in _Preferences > Network_ of your ProPresenter PC.
  
  Press Ctrl + X to close the Nano text editor.
  
6. The stage display should now load automatically whenever you login to your Raspberry Pi (there is a 10 second delay to give the Pi a chance to connect to the network). To start it manually, run the following commands from the terminal:

```
cd /home/pi/ProPresenter-Stage-Display-Python/
python2 StageDisplay.py
```

# Lower Third Mode (Lyric Subtitles)

You can also use this software to generate Lower Third (or subtitle-style) lyrics from ProPresenter. Now you can have one ProPresenter operator effortelssly generate lyrics for both the main screen and a broadcast/internet feed.

To enable this mode, set 'LowerThirdMode' to true in config.json and restart the application.

After you've enabled this change, the following options may be useful:

    "FontSizeCurrent": 35,
    "FontName": "Arial",
    "FontUppercase": false,
    "MergeLines": false,
    "MergeLinesMin": 4,
    "MergeLinesJoinChar": ","

Here's a summary of these options and how you might be able to use them:

* FontSizeCurrent: This is fairly self-explanatory
* FontName: Set this to the name of a font installed on your system
* FontUppercase: This will force all text to be converted to uppercase
* MergeLines: Enable this to force every 2nd line to join with the previous line. This is useful if you have lots of lines on-screen, but don't want to display them all as separate lines in Lower Third Mode
* MergeLinesMin: Slides with fewer than this number of lines won't be collapsed
* MergeLinesJoinChar: This character will be inserted between the two lines that are joined. Best to use a semi-colon or comma.

# Disabling the Screensaver on a Raspberry Pi

If you run this application on a Raspberry Pi, you're going to need to disable the screensaver. There's a couple of ways to do this, depending on your version of Raspbian:

## Method 1

1. Install XScreensaver, by using the following terminal command:

```
sudo apt-get install xscreensaver
```

2. Open the menu in the top-left corner of your desktop.
3. Go to Preference > Screensaver.
4. Select "Disable Screensaver"
5. Reboot your Pi for the changes to work


## Method 2

```
sudo nano /etc/lightdm/lightdm.conf
```

Find (Ctrl + W):

```
#xserver-command=X
```

Change it to:

```
xserver-command=X -s 0 dpms
```

## Method 3

Add these lines to /etc/xdg/lxsession/LXDE-pi/autostart:

```
@xset s noblank 
@xset s off 
@xset -dpms
```

# Known Issues

There are some known issues, although this application is being used reliably week-in, week-out on a Raspberry Pi so it should be good for common usage scenarios. Please see the [Issues](https://github.com/anthonyeden/ProPresenter-Stage-Display-Python/issues) page for an up to date list of these. Feel free to add your own as you come across them.

# Contributing

If you wish to contribute to the development of this little script, please feel free to create a [Pull Request](https://github.com/anthonyeden/ProPresenter-Stage-Display-Python/pulls).

If you run into any trouble, please create an [Issue](https://github.com/anthonyeden/ProPresenter-Stage-Display-Python/issues).
