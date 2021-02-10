# GeoSoftII_JobManagement
### Geosoftware II Projekt WiSe 2020/21
---

## Inhaltsverzeichnis
[1. Übersicht](#overview) \
[2. Installation](#install) \
[3. Anwendung](#use) \
  3.1. Zentrale Funktionalität \
  3.2. API Endpunkte \
[4. Anhang](#annex)

\
<a name="overview"><h3>Übersicht</h3></a>
Dieses Projekt ist ein Teil für einen neuen [openEO](https://openeo.org/) Backenddriver der mit [Pangeo Software Stack](https://pangeo.io/) arbeitet.

Ziel ist die Microservices mit Jobs und Batchprozessing zu verknüpfen.
Dabei wird konkret die Funktionen /F040/, /F050/ des Pflichtenheftes umgesetzt.

Außerdem gibt es ein [Docker Repository](https://hub.docker.com/repository/docker/felixgi1516/geosoft2_jobmanagement), welches mit diesem verlinkt ist und über das nach Fertigstellung der Service als Image bezogen werden. Und dann als Container lokal genutzt werden kann.

\
<a name="install"><h3>Installation</h3></a>
Die Installation und AUsführung ist exklusiv im Rahmen des zur verfügung gestellten *[docker-compose.yml](https://github.com/GeoSoftII2020-21/GeoSoftII_Projekt/blob/Docker-compose/docker-compose.yml)* möglich
```docker
docker-compose up
```

\
<a name="use"><h3>Anwendung</h3></a>


#### Zentrale Funktionalität
:bangbang: Funktionalität dokumentieren


#### API Endpunkte
Der Microservice soll über Endpoints aufrufbar sein, leider sind noch keine verfügbar.

- `GET /dataStatus` Nimmt eine request entgegen welche bestätigt das der DataServer bereit ist.
- `POST /takeJob` Nimmt eine request mit einem Job entgegen und queued diese.
\
<a name="annex"><h3>Anhang</h3></a>


#### Verwendete Software
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
