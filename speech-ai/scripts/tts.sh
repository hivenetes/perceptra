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

python3 clients/talk.py --server <public-ip>:50052 \
  --text \
  "Now available for every DigitalOcean user,
  GPU Droplets are powered by NVIDIA H100 GPUs, which are one of the most powerful computers accessible today,
  and feature 640 Tensor Cores and 128 Ray Tracing Cores, facilitating high-speed data processing. 
  GPU Droplets offer on-demand access to these machines, enabling developers, startups, and innovators to train AI models, 
  process large datasets, and handle complex neural networks with ease." \
  --language-code en-US \
  --output-device 1 --stream



  output output.wav