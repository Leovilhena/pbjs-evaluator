# pbjs-evaluator

Script to check JS pbjs.cbTimeout return from web page.

### Instalation

##### Python 3.7 installation:
```sudo apt-get install python3.7```

##### Dependencies installation:
```pip install -r requirements.txt```


### Tor proxies installation:
#### Debian/Ubuntu:
https://www.torproject.org/docs/debian.html.en

```sudo apt install tor```

```sudo systemctl start tor```

or

```sudo service tor start```

#### CentOS/RHEL/Fedora:
```sudo yum install tor```

###### Start the TOR service
```sudo systemctl start tor```

or

```sudo service tor start```

Please check if the Tor service is running with the "status" command for systemctl or service.

If you have a personal firewall that limits your computer's ability to connect to itself, be sure to allow connections 
from the script to Tor (local port 9050). If your firewall blocks outgoing connections, 
punch a hole so it can connect to at least TCP ports 80 and 443, and then see this FAQ entry (https://trac.torproject.org/projects/tor/wiki/doc/TorFAQ#FirewalledClient). 
If your SELinux config is not allowing tor to run correctly, create a file named booleans.local in the directory /etc/selinux/targeted. 
Edit this file in your favorite text editor and insert "allow_ypbind=1". Restart your machine for this change to take effect.

### Tests run:
```pytest -v```


## Built With

* [requests-html](http://html.python-requests.org)

## Authors

* **Leonardo Silva Vilhena** - *Github user* - [Github](https://github.com/Leovilhena)
