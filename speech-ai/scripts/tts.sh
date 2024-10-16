pip3 install nvidia-riva-client
pip3 install PyAudio

export CONTAINER_NAME=fastpitch-hifigan-tts
docker run -it --rm --name=$CONTAINER_NAME \
  --runtime=nvidia \
  --gpus '"device=0"' \
  --shm-size=8GB \
  -e NGC_API_KEY=$NGC_API_KEY \
  -e NIM_MANIFEST_PROFILE=3c8ee3ee-477f-11ef-aa12-1b4e6406fad5 \
  -e NIM_HTTP_API_PORT=9001 \
  -e NIM_GRPC_API_PORT=50052 \
  -p 9001:9001 \
  -p 50052:50052 \
  nvcr.io/nim/nvidia/fastpitch-hifigan-tts:1.0.0

  python3 clients/talk.py --server 184.105.190.88:50052 --text "Hello, this is a speech synthesizer." --language-code en-US --output output.wav
  python3 clients/talk.py --server 184.105.190.88:50052 --text "Hello, this is a speech synthesizer." --language-code en-US --output-device 2 --stream