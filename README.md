# GeoSoftII_JobManagement
### Geosoftware II Project WiSe 2020/21
---
## Table of contents
[1. Overview](#overview) \
[2. Installation](#install) \
[3. Scope of functionalities](#functionalities)  \
[4. Examples of use](#use) \
[5. Appendix](#annex) \

\
<a name="overview"><h3>Overview</h3></a>
This project is part of a new [openEO](https://openeo.org/) back-end driver which uses the [Pangeo Software Stack](https://pangeo.io/).

The goal is to link the microservices with jobs and batch processing.
The functions /F040/, /F050/ of the functional specification are implemented.

There also exists a [Docker Repository](https://hub.docker.com/repository/docker/felixgi1516/geosoft2_jobmanagement), which is linked with this one and from which the service can be obtained as an image. And can then be used locally as a container.

\
<a name="install"><h3>Installation</h3></a>
The installation and execution is possible exclusively provided within the framework of the *[docker-compose.yml](https://github.com/GeoSoftII2020-21/GeoSoftII_Projekt/blob/Docker-compose/docker-compose.yml)*.
```docker
docker-compose up
```

\
<a name="functionalities"><h3>Scope of functionalities</h3></a>

#### API endpoints
- `GET /dataStatus` Receives a request confirming that the DataServer is ready.
- `POST /takeJob` Receives a request with a job and queues it.

\
<a name="annex"><h3>Appendix</h3></a>

#### Technologies
Software | Version
------ | ------
Flask | 1.1.2
requests | 2.25.0
flask_cors | 3.0.9
xarray | 0.16.1
dask[complete] | 2.30.0
numpy | 1.19.3
scipy | 1.5.4
netcdf4 | 1.5.4
