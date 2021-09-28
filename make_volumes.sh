#! /bin/bash

VOLUMES_DIR=$(grep VOLUMES_DIR .env | xargs)
IFS='=' read -ra VOLUMES_DIR <<< "$VOLUMES_DIR"
VOLUMES_DIR=${VOLUMES_DIR[1]}
VOLUMES_DIR="$HOME/$VOLUMES_DIR"
echo $VOLUMES_DIR

if [ -d $VOLUMES_DIR ]
then
    echo "VOLUMES_DIR already exist"
else
    mkdir -p $VOLUMES_DIR
    mkdir -p "$VOLUMES_DIR/pg-data"
    mkdir -p "$VOLUMES_DIR/redis-data"
    mkdir -p "$VOLUMES_DIR/redis-config"
    cp redis.conf "$VOLUMES_DIR/redis-config/redis.conf"
    echo "VOLUMES_DIR created"
fi
