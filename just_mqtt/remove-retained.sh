#!/bin/sh
mosquitto_sub -h 192.168.0.82 -t '#' --remove-retained --retained-only
