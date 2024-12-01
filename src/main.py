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
import logging

from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import ToolNode

from agent.state import State
from agent.nodes import create_chatbot_node
from agent.graph_config import configure_graph
import getpass
import os


def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")


logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)


def parse_args() -> argparse.Namespace:

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
    parser.add_argument(
        "--list-devices", action="store_true", help="List output audio devices indices."
    )
    parser.add_argument("--output-device", type=int, help="Output device to use.")
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
    if args.list_devices:
        riva.client.audio_io.list_output_devices()
        return
    if args.output_device or args.play_audio:
        import riva.client.audio_io
    return args


def stream_graph_updates(graph, user_input: str):
    config = {"configurable": {"thread_id": "1"}}
    for chunk in graph.stream(
        {"messages": [user_input]}, config, stream_mode="updates"
    ):
        for node, values in chunk.items():
            response = values["messages"][0].content  # Store the content of AIMessage
            return response  # Return the response as a string
    return ""  # Return an empty string if no response is found


def run_perceptra(graph: any):
    """Wrapper function for the main speech processing logic"""
    while True:
        try:
            args = parse_args()

            # Initialize services
            asr_service = ASRService(args)
            tts_service = TTSService(args)

            logging.info("Recording for 5 seconds...")
            transcript = asr_service.record_and_transcribe(duration=5)

            if transcript:
                logging.info(f"Transcript: {transcript}")

                response = stream_graph_updates(graph, transcript)  # Capture the output

                tts_service.synthesize_speech(response)

        except KeyboardInterrupt:
            logging.info("\nRecording stopped by user")
            return
        except Exception as e:
            logging.error(f"Error in speech processing: {e}")
            time.sleep(1)


def main():
    # Set the env variables
    _set_env("ANTHROPIC_API_KEY")
    _set_env("TAVILY_API_KEY")
    # Build and instantiate the graph
    search_tool = TavilySearchResults(max_results=1)
    tools = [search_tool]

    tool_node = ToolNode(tools=[search_tool])

    graph = configure_graph(
        state_class=State, chatbot_node=create_chatbot_node, tool_node=tool_node
    )
    # Create and start the speech processing thread
    speech_thread = threading.Thread(target=run_perceptra(graph=graph), daemon=True)
    speech_thread.start()

    try:
        # Keep the main thread running
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        logging.info("\nExiting program...")


if __name__ == "__main__":
    main()
