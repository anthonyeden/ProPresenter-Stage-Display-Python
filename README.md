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

1. [Download and install NOOBS](https://www.raspberrypi.org/downloads/noobs/) with a desktop on your Raspberry Pi
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

# Known Issues

There are a number of known issues. Please see the [Issues](https://github.com/anthonyeden/ProPresenter-Stage-Display-Python/issues) page for an up to date list of these. Feel free to add your own as you come across them.

# Contributing

If you wish to contribute to the development of this little script, please feel free to create a [Pull Request](https://github.com/anthonyeden/ProPresenter-Stage-Display-Python/pulls).

If you run into any trouble, please create an [Issue](https://github.com/anthonyeden/ProPresenter-Stage-Display-Python/issues).
