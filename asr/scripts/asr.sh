# For nvidia runtime 
# Install Nvidia Docker package
sudo apt install -y nvidia-docker2

# Reload daemon and restart Docker
sudo systemctl daemon-reload
sudo systemctl restart docker

# For more details: https://build.nvidia.com/nvidia/parakeet-ctc-1_1b-asr/docker

docker login nvcr.io
Username: $oauthtoken
Password: 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

export NGC_API_KEY=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

export CONTAINER_NAME=parakeet-ctc-1.1b-asr
docker run -it --rm --name=$CONTAINER_NAME \
  --runtime=nvidia \
  --gpus '"device=0"' \
  --shm-size=8GB \
  -e NGC_API_KEY=$NGC_API_KEY \
  -e NIM_MANIFEST_PROFILE=9136dd64-4777-11ef-9f27-37cfd56fa6ee \
  -e NIM_HTTP_API_PORT=9000 \
  -e NIM_GRPC_API_PORT=50051 \
  -p 9000:9000 \
  -p 50051:50051 \
  nvcr.io/nim/nvidia/parakeet-ctc-1.1b-asr:1.0.0


pip install nvidia-riva-client
pip install pyadio


# Example grpc port
python3 transcribe_file.py --server 159.203.29.194:50051 --input-file sports.wav --language-code en-US

python3 transcribe_mic.py --server 159.203.29.194:50051 --input-device 1 --language-code en-US
