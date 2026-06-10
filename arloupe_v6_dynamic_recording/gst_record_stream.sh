#!/usr/bin/env bash
set -euo pipefail

# arLoupe: record and stream at the same time.
# This file only contains the GStreamer pipeline.

SESSION_ID="${SESSION_ID:-$(date +"%Y%m%d_%H%M%S")}" 
DEVICE_ID="${DEVICE_ID:-arloupe01}"
SEGMENT_DIR="${SEGMENT_DIR:-/home/user/arloupe_data/recordings/$(date +"%Y-%m-%d")}"

VIDEO_DEVICE="${VIDEO_DEVICE:-/dev/video0}"
WIDTH="${WIDTH:-1920}"
HEIGHT="${HEIGHT:-1080}"
FPS="${FPS:-60}"

MEDIA_SERVER_IP="${MEDIA_SERVER_IP:-20.41.113.226}"
SRT_PORT="${SRT_PORT:-8890}"
STREAM_PATH="${STREAM_PATH:-arloupe}"
SRT_LATENCY="${SRT_LATENCY:-30000}"
SRT_TLPKTDROP="${SRT_TLPKTDROP:-1}"
SRT_SNDDROPDELAY="${SRT_SNDDROPDELAY:-0}"
SRT_PKT_SIZE="${SRT_PKT_SIZE:-1316}"

BITRATE_KBPS="${BITRATE_KBPS:-12000}"
KEY_INT_MAX="${KEY_INT_MAX:-60}"
SEGMENT_NANOSECONDS="${SEGMENT_NANOSECONDS:-300000000000}"

PRE_ENCODE_QUEUE_BUFFERS="${PRE_ENCODE_QUEUE_BUFFERS:-10}"
RECORD_QUEUE_BUFFERS="${RECORD_QUEUE_BUFFERS:-180}"
STREAM_QUEUE_BUFFERS="${STREAM_QUEUE_BUFFERS:-2}"
PRE_ENCODE_QUEUE_LEAKY="${PRE_ENCODE_QUEUE_LEAKY:-1}"

RECORD_CONTINUOUS="${RECORD_CONTINUOUS:-1}"
RECORD_NUM_BUFFERS="${RECORD_NUM_BUFFERS:-}"

mkdir -p "${SEGMENT_DIR}"

if [[ "${PRE_ENCODE_QUEUE_LEAKY}" == "1" ]]; then
  PRE_ENCODE_QUEUE_LEAKY_ARG="leaky=downstream"
else
  PRE_ENCODE_QUEUE_LEAKY_ARG=""
fi

echo "[INFO] SESSION_ID=${SESSION_ID}"
echo "[INFO] DEVICE_ID=${DEVICE_ID}"
echo "[INFO] SEGMENT_DIR=${SEGMENT_DIR}"
echo "[INFO] SEGMENT_NANOSECONDS=${SEGMENT_NANOSECONDS}"
echo "[INFO] RECORD_CONTINUOUS=${RECORD_CONTINUOUS}"
echo "[INFO] RECORD_NUM_BUFFERS=${RECORD_NUM_BUFFERS}"
echo "[INFO] BITRATE_KBPS=${BITRATE_KBPS}"
echo "[INFO] SRT latency=${SRT_LATENCY}"
echo "[INFO] Start GStreamer record + stream pipeline"
echo

# Use a bash array so num-buffers can be added only when needed.
if [[ "${RECORD_CONTINUOUS}" == "1" ]]; then
  V4L2SRC_ARGS=(device="${VIDEO_DEVICE}" io-mode=mmap do-timestamp=true)
else
  V4L2SRC_ARGS=(device="${VIDEO_DEVICE}" io-mode=mmap do-timestamp=true num-buffers="${RECORD_NUM_BUFFERS}")
fi

gst-launch-1.0 -e -v \
  v4l2src "${V4L2SRC_ARGS[@]}" ! \
  "video/x-raw,format=UYVY,width=${WIDTH},height=${HEIGHT},framerate=${FPS}/1" ! \
  queue max-size-buffers="${PRE_ENCODE_QUEUE_BUFFERS}" max-size-time=0 max-size-bytes=0 ${PRE_ENCODE_QUEUE_LEAKY_ARG} ! \
  videoconvert ! \
  "video/x-raw,format=I420,width=${WIDTH},height=${HEIGHT},framerate=${FPS}/1" ! \
  queue max-size-buffers="${PRE_ENCODE_QUEUE_BUFFERS}" max-size-time=0 max-size-bytes=0 ${PRE_ENCODE_QUEUE_LEAKY_ARG} ! \
  x264enc bitrate="${BITRATE_KBPS}" speed-preset=ultrafast tune=zerolatency key-int-max="${KEY_INT_MAX}" bframes=0 byte-stream=true sliced-threads=true threads=4 vbv-buf-capacity=100 ! \
  h264parse config-interval=-1 ! \
  "video/x-h264,stream-format=byte-stream,alignment=au,framerate=${FPS}/1" ! \
  tee name=t \
  \
  t. ! queue max-size-buffers="${RECORD_QUEUE_BUFFERS}" max-size-time=0 max-size-bytes=0 ! \
  h264parse ! \
  splitmuxsink \
    location="${SEGMENT_DIR}/${SESSION_ID}_${DEVICE_ID}_seg%05d.mp4.tmp" \
    max-size-time="${SEGMENT_NANOSECONDS}" \
    async-finalize=true \
    send-keyframe-requests=true \
    muxer-factory=mp4mux \
  \
  t. ! queue max-size-buffers="${STREAM_QUEUE_BUFFERS}" max-size-time=0 max-size-bytes=0 leaky=downstream ! \
  h264parse ! \
  mpegtsmux alignment=7 ! \
  queue max-size-buffers="${STREAM_QUEUE_BUFFERS}" max-size-time=0 max-size-bytes=0 leaky=downstream ! \
  srtsink uri="srt://${MEDIA_SERVER_IP}:${SRT_PORT}?mode=caller&streamid=publish:${STREAM_PATH}&transtype=live&latency=${SRT_LATENCY}&tlpktdrop=${SRT_TLPKTDROP}&snddropdelay=${SRT_SNDDROPDELAY}&pkt_size=${SRT_PKT_SIZE}" sync=false async=false
