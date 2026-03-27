"""
MiniMax MCP Server

⚠️ IMPORTANT: This server connects to Minimax API endpoints which may involve costs.
Any tool that makes an API call is clearly marked with a cost warning. Please follow these guidelines:

1. Only use these tools when users specifically ask for them
2. For audio generation tools, be mindful that text length affects the cost
3. Voice cloning features are charged upon first use after cloning

Note: Tools without cost warnings are free to use as they only read existing data.
"""

import os
import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent
from minimax_mcp.utils import (
    build_output_path,
    build_output_file,
    process_input_file,
    play,
)

from minimax_mcp.const import *
from minimax_mcp.exceptions import MinimaxAPIError, MinimaxRequestError
from minimax_mcp.client import MinimaxAPIClient

load_dotenv()
api_key = os.getenv(ENV_MINIMAX_API_KEY)
base_path = os.getenv(ENV_MINIMAX_MCP_BASE_PATH) or "~/Desktop"
api_host = os.getenv(ENV_MINIMAX_API_HOST)
resource_mode = os.getenv(ENV_RESOURCE_MODE) or RESOURCE_MODE_URL
fastmcp_log_level = os.getenv(ENV_FASTMCP_LOG_LEVEL) or "WARNING"

if not api_key:
    raise ValueError("MINIMAX_API_KEY environment variable is required")
if not api_host:
    raise ValueError("MINIMAX_API_HOST environment variable is required")

mcp = FastMCP("Minimax", log_level=fastmcp_log_level)
api_client = MinimaxAPIClient(api_key, api_host)


@mcp.tool(
    description="""Convert text to audio with a given voice and save the output audio file to a given directory.
    Directory is optional, if not provided, the output file will be saved to $HOME/Desktop.
    Voice id is optional, if not provided, the default voice will be used.

    COST WARNING: This tool makes an API call to Minimax which may incur costs. Only use when explicitly requested by the user.

    Args:
        text (str): The text to convert to speech.
        voice_id (str, optional): The id of the voice to use. For example, "male-qn-qingse"/"audiobook_female_1"/"cute_boy"/"Charming_Lady"...
        model (string, optional): The model to use.
        speed (float, optional): Speed of the generated audio. Controls the speed of the generated speech. Values range from 0.5 to 2.0, with 1.0 being the default speed. 
        vol (float, optional): Volume of the generated audio. Controls the volume of the generated speech. Values range from 0 to 10, with 1 being the default volume.
        pitch (int, optional): Pitch of the generated audio. Controls the speed of the generated speech. Values range from -12 to 12, with 0 being the default speed.
        emotion (str, optional): Emotion of the generated audio. Controls the emotion of the generated speech. Values range ["happy", "sad", "angry", "fearful", "disgusted", "surprised", "neutral"], with "happy" being the default emotion.
        sample_rate (int, optional): Sample rate of the generated audio. Controls the sample rate of the generated speech. Values range [8000,16000,22050,24000,32000,44100] with 32000 being the default sample rate.
        bitrate (int, optional): Bitrate of the generated audio. Controls the bitrate of the generated speech. Values range [32000,64000,128000,256000] with 128000 being the default bitrate.
        channel (int, optional): Channel of the generated audio. Controls the channel of the generated speech. Values range [1, 2] with 1 being the default channel.
        format (str, optional): Format of the generated audio. Controls the format of the generated speech. Values range ["pcm", "mp3","flac"] with "mp3" being the default format.
        language_boost (str, optional): Language boost of the generated audio. Controls the language boost of the generated speech. Values range ['Chinese', 'Chinese,Yue', 'English', 'Arabic', 'Russian', 'Spanish', 'French', 'Portuguese', 'German', 'Turkish', 'Dutch', 'Ukrainian', 'Vietnamese', 'Indonesian', 'Japanese', 'Italian', 'Korean', 'Thai', 'Polish', 'Romanian', 'Greek', 'Czech', 'Finnish', 'Hindi', 'auto'] with "auto" being the default language boost.
        output_directory (str): The directory to save the audio to.

    Returns:
        Text content with the path to the output file and name of the voice used.
    """
)
def text_to_audio(
    text: str,
    output_directory: str = None,
    voice_id: str = DEFAULT_VOICE_ID,
    model: str = DEFAULT_SPEECH_MODEL,
    speed: float = DEFAULT_SPEED,
    vol: float = DEFAULT_VOLUME,
    pitch: int = DEFAULT_PITCH,
    emotion: str = DEFAULT_EMOTION,
    sample_rate: int = DEFAULT_SAMPLE_RATE,
    bitrate: int = DEFAULT_BITRATE,
    channel: int = DEFAULT_CHANNEL,
    format: str = DEFAULT_FORMAT,
    language_boost: str = DEFAULT_LANGUAGE_BOOST,
):
    if not text:
        raise MinimaxRequestError("Text is required.")

    payload = {
        "model": model,
        "text": text,
        "voice_setting": {
            "voice_id": voice_id,
            "speed": speed,
            "vol": vol,
            "pitch": pitch,
            "emotion": emotion,
        },
        "audio_setting": {
            "sample_rate": sample_rate,
            "bitrate": bitrate,
            "format": format,
            "channel": channel,
        },
        "language_boost": language_boost,
    }
    if resource_mode == RESOURCE_MODE_URL:
        payload["output_format"] = "url"
    try:
        response_data = api_client.post("/v1/t2a_v2", json=payload)
        audio_data = response_data.get("data", {}).get("audio", "")

        if not audio_data:
            raise MinimaxRequestError(f"Failed to get audio data from response")
        if resource_mode == RESOURCE_MODE_URL:
            return TextContent(type="text", text=f"Success. Audio URL: {audio_data}")
        # hex->bytes
        audio_bytes = bytes.fromhex(audio_data)

        # save audio to file
        output_path = build_output_path(output_directory, base_path)
        output_file_name = build_output_file("t2a", text, output_path, format)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path / output_file_name, "wb") as f:
            f.write(audio_bytes)

        return TextContent(
            type="text",
            text=f"Success. File saved as: {output_path / output_file_name}. Voice used: {voice_id}",
        )

    except MinimaxAPIError as e:
        return TextContent(type="text", text=f"Failed to generate audio: {str(e)}")


@mcp.tool(
    description="""List all voices available.

    Args:
        voice_type (str, optional): The type of voices to list. Values range ["all", "system", "voice_cloning"], with "all" being the default.
    Returns:
        Text content with the list of voices.
    """
)
def list_voices(voice_type: str = "all"):
    try:
        response_data = api_client.post(
            "/v1/get_voice", json={"voice_type": voice_type}
        )

        system_voices = response_data.get("system_voice", []) or []
        voice_cloning_voices = response_data.get("voice_cloning", []) or []
        system_voice_list = []
        voice_cloning_voice_list = []

        for voice in system_voices:
            system_voice_list.append(
                f"Name: {voice.get('voice_name')}, ID: {voice.get('voice_id')}"
            )
        for voice in voice_cloning_voices:
            voice_cloning_voice_list.append(
                f"Name: {voice.get('voice_name')}, ID: {voice.get('voice_id')}"
            )

        return TextContent(
            type="text",
            text=f"Success. System Voices: {system_voice_list}, Voice Cloning Voices: {voice_cloning_voice_list}",
        )

    except MinimaxAPIError as e:
        return TextContent(type="text", text=f"Failed to list voices: {str(e)}")


@mcp.tool(
    description="""Clone a voice using provided audio files. The new voice will be charged upon first use.

    COST WARNING: This tool makes an API call to Minimax which may incur costs. Only use when explicitly requested by the user.

     Args:
        voice_id (str): The id of the voice to use.
        file (str): The path to the audio file to clone or a URL to the audio file.
        text (str, optional): The text to use for the demo audio.
        is_url (bool, optional): Whether the file is a URL. Defaults to False.
        output_directory (str): The directory to save the demo audio to.
    Returns:
        Text content with the voice id of the cloned voice.
    """
)
def voice_clone(
    voice_id: str,
    file: str,
    text: str,
    output_directory: str = None,
    is_url: bool = False,
) -> TextContent:
    try:
        # step1: upload file
        if is_url:
            # download file from url
            response = requests.get(file, stream=True)
            response.raise_for_status()
            files = {"file": ("audio_file.mp3", response.raw, "audio/mpeg")}
            data = {"purpose": "voice_clone"}
            response_data = api_client.post("/v1/files/upload", files=files, data=data)
        else:
            # open and upload file
            if not os.path.exists(file):
                raise MinimaxRequestError(f"Local file does not exist: {file}")
            with open(file, "rb") as f:
                files = {"file": f}
                data = {"purpose": "voice_clone"}
                response_data = api_client.post(
                    "/v1/files/upload", files=files, data=data
                )

        file_id = response_data.get("file", {}).get("file_id")
        if not file_id:
            raise MinimaxRequestError(f"Failed to get file_id from upload response")

        # step2: clone voice
        payload = {
            "file_id": file_id,
            "voice_id": voice_id,
        }
        if text:
            payload["text"] = text
            payload["model"] = DEFAULT_SPEECH_MODEL

        response_data = api_client.post("/v1/voice_clone", json=payload)

        if not response_data.get("demo_audio"):
            return TextContent(
                type="text", text=f"Voice cloned successfully: Voice ID: {voice_id}"
            )
        if resource_mode == RESOURCE_MODE_URL:
            return TextContent(
                type="text",
                text=f"Success. Demo audio URL: {response_data.get('demo_audio')}",
            )
        # step3: download demo audio
        output_path = build_output_path(output_directory, base_path)
        output_file_name = build_output_file("voice_clone", text, output_path, "wav")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path / output_file_name, "wb") as f:
            f.write(requests.get(response_data.get("demo_audio")).content)

        return TextContent(
            type="text",
            text=f"Voice cloned successfully: Voice ID: {voice_id}, demo audio saved as: {output_path / output_file_name}",
        )

    except MinimaxAPIError as e:
        return TextContent(type="text", text=f"Failed to clone voice: {str(e)}")
    except (IOError, requests.RequestException) as e:
        return TextContent(type="text", text=f"Failed to handle files: {str(e)}")


@mcp.tool(
    description="""Play an audio file. Supports WAV and MP3 formats. Not supports video.

     Args:
        input_file_path (str): The path to the audio file to play.
        is_url (bool, optional): Whether the audio file is a URL.
    Returns:
        Text content with the path to the audio file.
    """
)
def play_audio(input_file_path: str, is_url: bool = False) -> TextContent:
    if is_url:
        play(requests.get(input_file_path).content)
        return TextContent(
            type="text", text=f"Successfully played audio file: {input_file_path}"
        )
    else:
        file_path = process_input_file(input_file_path)
        play(open(file_path, "rb").read())
        return TextContent(
            type="text", text=f"Successfully played audio file: {file_path}"
        )


@mcp.tool(
    description="""Generate a voice based on description prompts.

    COST WARNING: This tool makes an API call to Minimax which may incur costs. Only use when explicitly requested by the user.

     Args:
        prompt (str): The prompt to generate the voice from.
        preview_text (str): The text to preview the voice.
        voice_id (str, optional): The id of the voice to use. For example, "male-qn-qingse"/"audiobook_female_1"/"cute_boy"/"Charming_Lady"...
        output_directory (str, optional): The directory to save the voice to.
    Returns:
        Text content with the path to the output voice file.
    """
)
def voice_design(
    prompt: str,
    preview_text: str,
    voice_id: str = None,
    output_directory: str = None,
):
    try:
        if not prompt:
            raise MinimaxRequestError("prompt is required")
        if not preview_text:
            raise MinimaxRequestError("preview_text is required")

        # Build request payload
        payload = {"prompt": prompt, "preview_text": preview_text}

        # Add voice_id if provided
        if voice_id:
            payload["voice_id"] = voice_id

        # Call voice design API
        response_data = api_client.post("/v1/voice_design", json=payload)

        # Get the response data
        generated_voice_id = response_data.get("voice_id", "")
        trial_audio_hex = response_data.get("trial_audio", "")

        if not generated_voice_id:
            raise MinimaxRequestError("No voice generated")
        if resource_mode == RESOURCE_MODE_URL:
            return TextContent(
                type="text",
                text=f"Success. Voice ID generated: {generated_voice_id}, Trial Audio: {trial_audio_hex}",
            )

        # hex->bytes
        audio_bytes = bytes.fromhex(trial_audio_hex)

        # save audio to file
        output_path = build_output_path(output_directory, base_path)
        output_file_name = build_output_file(
            "voice_design", preview_text, output_path, "mp3"
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path / output_file_name, "wb") as f:
            f.write(audio_bytes)

        return TextContent(
            type="text",
            text=f"Success. File saved as: {output_path / output_file_name}. Voice ID generated: {generated_voice_id}",
        )

    except MinimaxAPIError as e:
        return TextContent(type="text", text=f"Failed to design voice: {str(e)}")


def main():
    print("Starting Minimax MCP server")
    """Run the Minimax MCP server"""
    mcp.run()


if __name__ == "__main__":
    main()
