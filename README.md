# dashboard

A customizable data visualization tool with automatically generated dashboards based on the discovered schema of an InfluxDB instance running on the same device.

Dashboard is built to visualize your data with the minimum of effort, and can be used as part of your own projects or in combination with InfluxDB and [connector](https://github.com/balenablocks/connector) to quickly build a data capture and analysis tool.

## Features

- Automatically connects to an InfluxDB container named `influxdb` running on port 8086 on the same device
- Discovers database schema and generates dashboards
- Adds basic data visualization to dashboards based on field type
- Periodically checks database schema looking for new fields and adds what it finds
- Does not continue to add fields or dashboards after they have been deleted by the user

## Usage

#### docker-compose file

To use this image, create a container in your `docker-compose.yml` file as shown below:

```yaml
version: "2.1"

volumes:
  dashboard-data:

services:
  dashboard:
    image: balenablocks/dashboard
    restart: always
    volumes:
      - "dashboard-data:/data"
    ports:
      - "80"
```

You can set your `docker-compose.yml` to build a `Dockerfile` file and use the dashboard block as the base image.
_docker-compose.yml:_

```yaml
version: "2"

volumes:
  dashboard-data:

services:
  dashboard:
    build: ./
    restart: always
    volumes:
      - "dashboard-data:/data"
    ports:
      - "80"
```

_Dockerfile_

```dockerfile
FROM balenablocks/dashboard
```

## Accessing

By default the dashboard runs an HTTP server on port `80`, which will be accessible externally to the device.

## Configuration

To change the port used to access the dashboard you can map the port like so, in the example of 8080:

```
    ports:
        - '8080:80'
```

You can also change the port used by the server by specifying the `BB_DASHBOARD_PORT` environment variable, noting that the `docker-compose.yml` must also be updated to reflect the change.

## Provisioning

Dashboards can be provisioned automatically by placing the JSON description of them in the `provisioning/dashboards` folder, see [balenaSense](https://github.com/balenalabs/balena-sense) for an example of this.
