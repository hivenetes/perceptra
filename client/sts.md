# Speech-to-Speech

```bash
python3 sts.py --asr-server 184.105.190.88:50051 --tts-server 184.105.190.88:50052 --language-code en-US --input-device 1 --output-device 2 --output output.wav --stream
```

mkdir ~/nim-cache
export NIM_CACHE_PATH=~/nim-cache
sudo chmod -R 777 $NIM_CACHE_PATH

export CONTAINER_NAME=parakeet-ctc-1.1b-asr

docker run -it --rm --name=$CONTAINER_NAME \
   --runtime=nvidia \
   --gpus '"device=0"' \
   --shm-size=8GB \
   -e NGC_CLI_API_KEY=$NGC_CLI_API_KEY \
   -e NIM_MANIFEST_PROFILE=9136dd64-4777-11ef-9f27-37cfd56fa6ee \
   -e NIM_HTTP_API_PORT=9000 \
   -e NIM_GRPC_API_PORT=50051 \
   -v $NIM_CACHE_PATH:/opt/nim/.cache \
   -p 9000:9000 \
   -p 50051:50051 \
   nvcr.io/nim/nvidia/parakeet-ctc-1.1b-asr:1.0.0

export CONTAINER_NAME=fastpitch-hifigan-tts

docker run -it --rm --name=$CONTAINER_NAME \
  --runtime=nvidia \
  --gpus '"device=0"' \
  --shm-size=8GB \
  -e NGC_CLI_API_KEY=$NGC_CLI_API_KEY \
  -e NIM_MANIFEST_PROFILE=3c8ee3ee-477f-11ef-aa12-1b4e6406fad5 \
  -e NIM_HTTP_API_PORT=9001 \
  -e NIM_GRPC_API_PORT=50052 \
  -v $NIM_CACHE_PATH:/opt/nim/.cache \
  -p 9001:9001 \
  -p 50052:50052 \
  nvcr.io/nim/nvidia/fastpitch-hifigan-tts:1.0.0
