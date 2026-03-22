# Cam archive system

Periodical archive from online camera, with building daily timelapse movie and providing WebUI for archives.

## basic requirements

* daemon like script for retrieving and store images from specified URI periodically
* daily batch to build timelapse movies
* Web UI to view archived images and videos

## system design

* three blocks: daemon to archive periodically, daily batch for timelapse, Web UI
* share single configuration file (json) over three blocks, no database but just file based listing
* [configuration file skelton](common/config.json.skel)
  * interval: interval (sec) for archiving image from camera, the same value for every targets
  * keepimage: after timelapse built from archived images, how many days images are kept in storage
  * targets: hash of targets, hash name is treated as internal ID (for Web API, storage directory name, etc.)
    * url: target URL to archive
    * user, pass: if both exist, this set is used for BASIC auth
    * ext: extension to be attached for saved image (e.g. jpg, png)
  * storage: root directory for data storage
* storage organization
  * `<root>/<ID>/`: root for each target
  * `<root>/<ID>/movie/YYYYMMDD.mp4`: built timelapse movies
  * `<root>/<ID>/image/YYYYMMDD/YYYYMMDDHHMMSS.jpg`: archived images
* calc start time of image archiving, use seconds in the day and pick next time when mod(interval) is 0
  * if 86400s (1d) mod(interval) is not 0, just use above at start date, will not start from 00:00:00 at second day

