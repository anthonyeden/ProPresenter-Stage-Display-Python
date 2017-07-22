![ProPresenter Stage Display for Python](https://mediarealm.com.au/wp-content/uploads/2017/07/ProPresenter-Stage-Display-Python.png)

# ProPresenter Stage Display for Python
An unofficial Python implementation of the [ProPresenter Stage Display](https://www.renewedvision.com/store.php?item=prostagedisplay).

Currently, this implementation is very basic and designed to implement only three basic features:

* Clock
* Current slide text
* Next slide text

This program has been designed to run on small devices such as the Raspberry Pi.

# How to setup

1. Download the [software](https://github.com/anthonyeden/ProPresenter-Stage-Display-Python/archive/master.zip)
2. Install Python
3. Copy _config-sample.json_ to _config.json_
4. Edit _config.json_ in a text editor and set the IP Address, Port Number, and Password for your ProPresenter Stage Display computer (found in _Preferences > Network_ of your ProPresenter PC).
5. Run _python StageDisplay.py_

# Contributing

If you wish to contribute to the development of this little script, please feel free to create a [Pull Request](https://github.com/anthonyeden/ProPresenter-Stage-Display-Python/pulls).

If you run into any trouble, please create an [Issue](https://github.com/anthonyeden/ProPresenter-Stage-Display-Python/issues).
