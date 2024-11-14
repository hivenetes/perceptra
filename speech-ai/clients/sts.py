import argparse
import wave
import time
from pathlib import Path
import riva.client
from riva.client.argparse_utils import (
    add_asr_config_argparse_parameters,
    add_connection_argparse_parameters,
)
import riva.client.audio_io
import threading
from asr_service import ASRService
from tts_service import TTSService


def parse_args() -> argparse.Namespace:
    # default_device_info = riva.client.audio_io.get_default_input_device_info()
    # default_device_index = None if default_device_info is None else default_device_info['index']

    parser = argparse.ArgumentParser(
        description="End-to-end speech agent with ASR and TTS",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # ASR parameters
    parser.add_argument(
        "--asr-server", default="localhost:50051", help="ASR server endpoint"
    )
    parser.add_argument(
        "--tts-server", default="localhost:50052", help="TTS server endpoint"
    )
    parser.add_argument("--input-device", type=int, help="Input audio device to use")
    parser.add_argument(
        "--sample-rate-hz",
        type=int,
        default=16000,
        help="Sample rate for audio recording",
    )
    parser.add_argument(
        "--file-streaming-chunk",
        type=int,
        default=1600,
        help="Maximum frames per audio chunk",
    )
    parser = add_asr_config_argparse_parameters(parser)

    # TTS parameters
    parser.add_argument("--voice", help="Voice name for TTS")
    parser.add_argument("--output-device", type=int, help="Output device to use.")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default="output.wav",
        help="Output file .wav file to write synthesized audio.",
    )
    parser.add_argument(
        "--stream",
        action="store_true",
        help="If this option is set, then streaming synthesis is applied. Streaming means that audio is yielded "
        "as it gets ready. If `--stream` is not set, then a synthesized audio is returned in 1 response only when "
        "all text is processed.",
    )
    parser.add_argument(
        "--audio_prompt_file",
        type=Path,
        help="An input audio prompt (.wav) file for zero shot model. This is required to do zero shot inferencing.",
    )
    parser.add_argument(
        "--quality",
        type=int,
        help="Number of times decoder should be run on the output audio. A higher number improves quality of the produced output but introduces latencies.",
    )
    parser.add_argument(
        "--custom-dictionary",
        type=str,
        help="A file path to a user dictionary with key-value pairs separated by double spaces.",
    )

    # Common parameters
    parser = add_connection_argparse_parameters(parser)
    args = parser.parse_args()
    if args.output is not None:
        args.output = args.output.expanduser()
    if args.output_device or args.play_audio:
        import riva.client.audio_io
    return args


def run_speech_processing():
    """Wrapper function for the main speech processing logic"""
    while True:
        try:
            args = parse_args()
            
            # Initialize services
            asr_service = ASRService(args)
            tts_service = TTSService(args)

            print("Recording for 3 seconds...")
            transcript = asr_service.record_and_transcribe(duration=3)
            print(f"Final transcription: {transcript}")

            if transcript:
                print("\nGenerating speech from transcription...")
                tts_service.synthesize_speech(transcript)
                
        except KeyboardInterrupt:
            print("\nRecording stopped by user")
            return
        except Exception as e:
            print(f"Error in speech processing: {e}")
            time.sleep(1)

if __name__ == "__main__":
    # Create and start the speech processing thread
    speech_thread = threading.Thread(target=run_speech_processing, daemon=True)
    speech_thread.start()
    
    try:
        # Keep the main thread running
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nExiting program...")
