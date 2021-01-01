#!/bin/bash
stat -c %g /var/run/docker.sock > $1/dockergid