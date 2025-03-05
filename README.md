
# Conversational AI with NIMs on GPU Droplets

This guide provides steps for setting up an end-to-end Conversational AI pipeline using NVIDIA NIMs on DigitalOcean GPU droplets, including client setup instructions.

## Prerequisites

Ensure you have the following:

- **DigitalOcean CLI** - [doctl](https://docs.digitalocean.com/reference/doctl/how-to/install/)
- **NGC API Key**: Generate one from [NVIDIA NGC](https://org.ngc.nvidia.com/setup/api-key)
- **Anthropic API Key**: Generate one from [Anthropic](https://docs.anthropic.com/en/api/getting-started)

## NVIDIA Triton/RIVA Server Setup

1. **Create a GPU Droplet:**

   Use `doctl` to spin up a GPU Droplet, replacing `<region>` and `<ssh-key-fingerprint>` with appropriate values:

   ```bash
   doctl compute droplet create ab-ai-ctk --region <tor1/ams3> --image gpu-h100x1-base --size gpu-h100x1-80gb --ssh-keys <ssh-key-fingerprint>
   ```

2. **Run the NIM Services:**

   ```bash
   cd server
   # rename .env.example to .env and add the values in the .env file
   mv .env.example .env
   # spin up the nim services (asr and tts)
   docker-compose --env-file .env up
   ```

## Running the S2S Client

1. **Run the Speech2Speech Client:**

Install the following dependencies on your client machine:

```bash
pip3 install -r requirements.txt
```

Use the following command to transcribe audio from your microphone:

```bash
python3.12 sts.py --asr-server <public-ip>:50051 --tts-server <public-ip>:50052 --language-code en-US --input-device 0 --output-device 1 --stream
```

Replace `<public-ip>` with the public IP of your GPU Droplet.
