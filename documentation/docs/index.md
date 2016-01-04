# PTXConf documentation

Pen tablet and Touch screen Xinput Configuration tool (PTXConf). 
Configures touch/pen devices to work with extended desktops and multiple screens on Linux.

## Usage
TODO...
## Installation
PTXConf depends on the python gtk2 and the AppIndicator binding. On debian based systems you can install these packages as follows,
```sh
$ sudo apt-get install python-gtk2
$ sudo apt-get install python-appindicator
```
Then install this package,
```sh
$ git clone http://github.com/wenhsinjen/ptxconf.git
$ cd ptxconf
$ sudo python setup.py install
```
After this package has been submitted to PyPI you will be able to do,
```sh
$ sudo pip install ptxconf
```

## API code examples

Some dummy code for testing MD...
```python
from ptxconftools import ConfController
cc = ConfController()
cc.listDevices()
```


