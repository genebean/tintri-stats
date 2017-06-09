# Tintri Graphite OpenShift

This repo contains a modified version of tintri_graphite.py from
[github.com/eric-becker/tintri_graphite][tg-url]
and tintri_1_1.py from [github.com/Tintri/tintri-rest-api][t1-url].

This is a simple app that runs in OpenShift using the
[Python 2.7 template][p27]. It connects to a specified Tintri vmstore, gathers
metrics, and sends them to a specified Graphite server.

## Usage

If running from OpenShift you will need to set 6 environment variables:

* APP_FILE         = tintri_graphite.py
* vmstore_fqdn     = _the fqdn of your Tintri's admin interface_ 
* vmstore_username = _a read-only account on your Tintri_
* vmstore_password = _the password for the read-only account_
* graphite_fqdn    = _the fqdn of your Graphite server_
* graphite_port    = 2003 _(adjust if needed)_

If running interactively, you can also pass the last 5 of these as command line
arguments like so:

```bash
python tintri_graphite.py vmstore_fqdn vmstore_username vmstore_password graphite_fqdn graphite_port
```


[p27]: https://github.com/sclorg/s2i-python-container
[tg-url]: https://github.com/eric-becker/tintri_graphite/
[t1-url]: https://github.com/Tintri/tintri-rest-api/blob/master/examples/python/
