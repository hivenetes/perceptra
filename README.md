# Conversational AI with NIMs on GPU Droplets

This guide provides steps for setting up an end-to-end Conversational AI pipeline using NVIDIA NIMs on DigitalOcean GPU droplets, including client setup instructions.

## Prerequisites

Ensure you have the following:

- **DigitalOcean CLI** - [doctl](https://docs.digitalocean.com/reference/doctl/how-to/install/)
- **NGC API Key**: Generate one from [NVIDIA NGC](https://org.ngc.nvidia.com/setup/api-key) and install the [ngc-cli](https://org.ngc.nvidia.com/setup/installers/cli)
- **Anthropic API Key**: Generate one from [Anthropic](https://docs.anthropic.com/en/api/getting-started)

## NVIDIA Triton/RIVA Server Setup

1. **Create a GPU Droplet:**

   Use `doctl` to spin up a GPU Droplet, replacing `<region>` and `<ssh-key-fingerprint>` with appropriate values:

   ```bash
   doctl compute droplet create ab-ai-ctk --region <tor1/ams3> --image gpu-h100x1-base --size gpu-h100x1-80gb --ssh-keys <ssh-key-fingerprint>
   ```

2. **Run the NIM Services:**

   ```bash
   ## inital-setup
   ssh -i ~/.ssh/ai paperspace@<ip-address>
   docker login nvcr.io

   Username: $oauthtoken
   Password: <ngc_api_key>   

   # Note: This cache directory is to where models are downloaded inside the container. If this volume is not mounted, the container does a fresh download of the model every time the container starts

   mkdir ~/nim-cache
   export NIM_CACHE_PATH=~/nim-cache
   sudo chmod -R 777 $NIM_CACHE_PATH

   ## Run the services
   ./scripts/deploy.sh
   # ssh into the machine and run the docker-compose command
   ssh -i ~/.ssh/ai paperspace@<ip-address>
   # spin up the nim services (asr and tts)
   docker-compose --env-file .env up
   ```

## Running the S2S Client

1. **Run the Speech2Speech Client:**

Install the following dependencies on your client machine:

```bash
pip3.13 install -r requirements.txt
```

Use the following command to transcribe audio from your microphone:

```bash
# Run this command to get the list audio devices
python3.13 scripts/transcribe_mic.py --list-device && python3.13 scripts/talk.py --list-device
```

```bash
python3.13 src/main.py --asr-server <public-ip>:50051 --tts-server <public-ip>:50052 --language-code en-US --input-device 0 --output-device 1 --stream
```

Replace `<public-ip>` with the public IP of your GPU Droplet.

![Perceptra Image](perceptra.png)
