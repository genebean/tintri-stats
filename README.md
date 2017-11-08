# Tintri Stats

[![](https://images.microbadger.com/badges/version/genebean/tintri-stats.svg)](https://microbadger.com/images/genebean/tintri-stats "Get your own version badge on microbadger.com")
[![](https://images.microbadger.com/badges/commit/genebean/tintri-stats.svg)](https://microbadger.com/images/genebean/tintri-stats "Get your own commit badge on microbadger.com")
[![](https://images.microbadger.com/badges/image/genebean/tintri-stats.svg)](https://microbadger.com/images/genebean/tintri-stats "Get your own image badge on microbadger.com")

This is a simple app that runs either in a Docker container or
in OpenShift using the [Python 2.7 template][p27]. The docker container is
published as [genebean/tintri-stats](https://hub.docker.com/r/genebean/tintri-stats/)
It connects to a specified Tintri VMstore, gathers metrics, and sends them to a
specified Graphite server. Optionally, you could also point this at a
Tintri Global Center instance. To collect metrics from multiple VMstores you
will need to run multiple instances of this app.

![screenshot of the provided dashboard](screenshot-tintri_grafana_dashboard.png)

## Usage

There are five parameters used by the `tintri_graphite.py` application:

- vmstore_fqdn     = _the fqdn of your Tintri's admin interface_
- vmstore_username = _a read-only account on your Tintri_
- vmstore_password = _the password for the read-only account_
- graphite_fqdn    = _the fqdn of your Graphite server_
- graphite_port    = 2003 _(adjust if needed)_


### Docker

To run in docker you will need to pass in the parameters listed above like so:

```bash
$ read -s vmstore_password
# type / paste your password (it won't be displayed)
$ docker run \
  --name stats-4-tintri-admin-opdx-prod-1 \
  genebean/tintri-stats \
  python tintri_graphite.py tintri-array1.example.com stats_user $vmstore_password graphite.example.com 2003
```


### OpenShift

If running from OpenShift you will need to set the parameters above as
environment variables along with a sixth one:

- APP_FILE         = tintri_graphite.py


### Interactive / Command Line

If running interactively, you can also pass the last 5 of these as command line
arguments like so:

```bash
read -s vmstore_password
# type / paste your password (it won't be displayed)
python tintri_graphite.py vmstore_fqdn vmstore_username $vmstore_password graphite_fqdn graphite_port
```


## Prior work

This repo contains a modified version of tintri_graphite.py from
[github.com/eric-becker/tintri_graphite][tg-url]
and tintri_1_1.py from [github.com/Tintri/tintri-rest-api][t1-url].


[p27]: https://github.com/sclorg/s2i-python-container
[tg-url]: https://github.com/eric-becker/tintri_graphite/
[t1-url]: https://github.com/Tintri/tintri-rest-api/blob/master/examples/python/
