# IoT Troubleshooting

## Device Logs

- Check all the IoT edge modules are still running
  - `iotedge list`
- Check the logs of all edge modules and output to a file
  - `docker ps`
  - `docker logs container-id > module-name.LOGS`
  - We use the docker container logs because the `iotedge logs` seem to get purged after a day or two, and you don't get the full output.
- Check that the RTSP stream is still up and healthy
  - If using a real camera, can you navigate to the RTSP endpoint and see the camera stream?
- You can do a deeper check on the state of the modules with to check if something else might be broken or if the module restarted
  at any point
  - `docker ps`
  - `docker inspect container-id`
- Check the CPU usage
  - Built-in to Ubuntu `top`
  - Or, setup [Jetson Stats](https://github.com/rbonghi/jetson_stats) for your device to view CPU, GPU and RAM status
- You can check the state of IoT Edge using the following command. This helps do a scan of potential issues, including
  checking cert expirations and things to do when going into production.
  - `iotedge check`
- If all else fails, restart IoT Edge
  - `sudo systemctl restart iotedge`

> You may need to run all docker commands using `sudo`

## Documentation

- [Microsoft documentation on troubleshooting IoT Edge](https://docs.microsoft.com/azure/iot-edge/troubleshoot?view=iotedge-2018-06).
- [Common issues and resolutions](https://docs.microsoft.com/azure/iot-edge/troubleshoot-common-errors?view=iotedge-2018-06)
