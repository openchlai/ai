"""
SCP-based audio downloader for Asterisk call recordings
Flexible configuration-based approach for different deployment environments
"""
import asyncio
import logging
import os
import tempfile
from typing import Optional, Tuple, Dict, Any

logger = logging.getLogger(__name__)


async def download_audio_via_scp(call_id: str, scp_config: Dict[str, Any] = None) -> Tuple[Optional[bytes], Dict[str, Any]]:
    """
    Download audio file from Asterisk server via SCP with configurable credentials
    
    Args:
        call_id: The unique call ID (e.g., 1755070077.79708)
        scp_config: Optional SCP configuration override
        
    Returns:
        Tuple of (audio_bytes, download_info)
        audio_bytes: The downloaded audio data or None if failed
        download_info: Dictionary with download metadata
    """
    
    # Get SCP configuration (allow override for flexibility)
    if scp_config is None:
        # Load from settings with environment variable fallbacks
        from ..config.settings import settings
        scp_config = {
            "user": settings.scp_user,
            "server": settings.scp_server,
            "password": settings.scp_password,
            "remote_path_template": settings.scp_remote_path_template,
            "timeout_seconds": settings.scp_timeout_seconds
        }
    
    # Format remote path with call_id
    remote_path = scp_config["remote_path_template"].format(call_id=call_id)
    
    download_info = {
        "call_id": call_id,
        "server": scp_config["server"],
        "remote_path": remote_path,
        "method": "scp",
        "success": False,
        "file_size_bytes": 0,
        "file_size_mb": 0.0,
        "error": None,
        "format": "gsm"
    }
    
    logger.info(f"📥 [scp] Starting audio download for call {call_id}")
    logger.info(f"📥 [scp] Remote: {scp_config['user']}@{scp_config['server']}:{remote_path}")
    
    # Create temporary file for download
    with tempfile.NamedTemporaryFile(suffix='.gsm', delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        # Use sshpass + scp for password authentication
        scp_cmd = [
            'sshpass', '-p', scp_config["password"],
            'scp',
            '-o', 'StrictHostKeyChecking=no',
            '-o', 'UserKnownHostsFile=/dev/null',
            '-o', f'ConnectTimeout={scp_config["timeout_seconds"]}',
            '-o', 'ServerAliveInterval=10',
            f"{scp_config['user']}@{scp_config['server']}:{remote_path}",
            temp_path
        ]
        
        logger.debug(f"🔧 [scp] Executing: sshpass -p [PASSWORD] scp [OPTIONS] {scp_config['user']}@{scp_config['server']}:{remote_path} {temp_path}")
        
        # Execute SCP command
        process = await asyncio.create_subprocess_exec(
            *scp_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        # Check if download succeeded (return code 0 means success)
        if process.returncode == 0:
            # Check if file was actually downloaded
            if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                # Successfully downloaded file
                file_size_bytes = os.path.getsize(temp_path)
                
                with open(temp_path, 'rb') as f:
                    audio_bytes = f.read()
                
                download_info.update({
                    "success": True,
                    "file_size_bytes": file_size_bytes,
                    "file_size_mb": round(file_size_bytes / (1024 * 1024), 2)
                })
                
                logger.info(f"✅ [scp] Downloaded {download_info['file_size_mb']:.2f}MB audio file: {call_id}.gsm")
                
                return audio_bytes, download_info
            else:
                # File doesn't exist or is empty
                error_msg = f"Downloaded file is missing or empty (path: {temp_path})"
                download_info["error"] = error_msg
                logger.error(f"❌ [scp] {error_msg}")
                
                # Log SSH warnings as debug if they exist
                if stderr:
                    stderr_text = stderr.decode().strip()
                    if stderr_text:
                        logger.debug(f"🔧 [scp] SSH info: {stderr_text}")
                
                return None, download_info
            
        else:
            # Download failed
            error_msg = f"SCP failed (code {process.returncode})"
            if stderr:
                stderr_text = stderr.decode().strip()
                # Filter out harmless SSH host key warnings
                if "permanently added" not in stderr_text.lower() and "warning" not in stderr_text.lower():
                    error_msg += f": {stderr_text}"
                elif stderr_text:
                    # Log SSH warnings as debug, not error
                    logger.debug(f"🔧 [scp] SSH info: {stderr_text}")
            
            download_info["error"] = error_msg
            logger.error(f"❌ [scp] {error_msg}")
            
            return None, download_info
            
    except FileNotFoundError:
        error_msg = "sshpass not installed - required for password authentication"
        download_info["error"] = error_msg
        logger.error(f"❌ [scp] {error_msg}")
        logger.error(f"❌ [scp] Install with: apt-get install sshpass")
        return None, download_info
        
    except Exception as e:
        error_msg = f"SCP error: {str(e)}"
        download_info["error"] = error_msg
        logger.error(f"❌ [scp] Audio download failed for call {call_id}: {e}")
        return None, download_info
        
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except Exception as e:
                logger.warning(f"⚠️ Failed to cleanup temp file {temp_path}: {e}")


async def convert_gsm_to_wav(gsm_bytes: bytes) -> Optional[bytes]:
    """
    Convert GSM audio data to WAV format for better processing
    
    Args:
        gsm_bytes: Raw GSM audio data
        
    Returns:
        WAV audio bytes or None if conversion fails
    """
    try:
        # Create temporary files for conversion
        with tempfile.NamedTemporaryFile(suffix='.gsm', delete=False) as gsm_temp:
            gsm_temp.write(gsm_bytes)
            gsm_path = gsm_temp.name
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as wav_temp:
            wav_path = wav_temp.name
        
        try:
            # Use ffmpeg to convert GSM to WAV
            convert_cmd = [
                'ffmpeg', '-y',  # Overwrite output file
                '-i', gsm_path,  # Input GSM file
                '-ar', '16000',  # Sample rate 16kHz (standard for Whisper)
                '-ac', '1',      # Mono audio
                '-f', 'wav',     # Output format WAV
                wav_path         # Output file
            ]
            
            logger.debug(f"🔄 [convert] Converting GSM to WAV: ffmpeg -i {gsm_path} -ar 16000 -ac 1 -f wav {wav_path}")
            
            process = await asyncio.create_subprocess_exec(
                *convert_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0 and os.path.exists(wav_path) and os.path.getsize(wav_path) > 0:
                # Read converted WAV file
                with open(wav_path, 'rb') as f:
                    wav_bytes = f.read()
                
                wav_size_mb = len(wav_bytes) / (1024 * 1024)
                gsm_size_mb = len(gsm_bytes) / (1024 * 1024)
                
                logger.info(f"🔄 [convert] GSM→WAV conversion successful: {gsm_size_mb:.2f}MB → {wav_size_mb:.2f}MB")
                
                return wav_bytes
            else:
                error_output = stderr.decode().strip() if stderr else "Unknown error"
                logger.error(f"❌ [convert] FFmpeg conversion failed (code {process.returncode}): {error_output}")
                return None
                
        finally:
            # Cleanup temp files
            for temp_path in [gsm_path, wav_path]:
                if os.path.exists(temp_path):
                    try:
                        os.unlink(temp_path)
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to cleanup {temp_path}: {e}")
                        
    except FileNotFoundError:
        logger.error("❌ [convert] ffmpeg not installed - required for GSM to WAV conversion")
        logger.error("❌ [convert] Install with: apt-get install ffmpeg")
        return None
        
    except Exception as e:
        logger.error(f"❌ [convert] GSM to WAV conversion failed: {e}")
        return None


async def download_and_convert_audio(call_id: str, convert_to_wav: bool = True, 
                                   scp_config: Dict[str, Any] = None) -> Tuple[Optional[bytes], Dict[str, Any]]:
    """
    Complete audio download and conversion pipeline with configurable options
    
    Args:
        call_id: The unique call ID
        convert_to_wav: Whether to convert GSM to WAV (recommended for Whisper)
        scp_config: Optional SCP configuration override
        
    Returns:
        Tuple of (audio_bytes, download_info)
    """
    
    # Download via SCP
    audio_bytes, download_info = await download_audio_via_scp(call_id, scp_config)
    
    if audio_bytes is None:
        return None, download_info
    
    # Convert GSM to WAV if requested
    if convert_to_wav:
        logger.info(f"🔄 [pipeline] Converting {call_id}.gsm to WAV format")
        
        wav_bytes = await convert_gsm_to_wav(audio_bytes)
        
        if wav_bytes is not None:
            # Update download info
            download_info.update({
                "format": "wav_converted_from_gsm",
                "original_size_bytes": download_info["file_size_bytes"],
                "original_size_mb": download_info["file_size_mb"],
                "converted_size_bytes": len(wav_bytes),
                "converted_size_mb": round(len(wav_bytes) / (1024 * 1024), 2),
                "conversion_successful": True
            })
            
            logger.info(f"✅ [pipeline] Audio download and conversion completed for {call_id}")
            return wav_bytes, download_info
        else:
            # Conversion failed, fall back to original GSM
            logger.warning(f"⚠️ [pipeline] WAV conversion failed for {call_id}, using original GSM")
            download_info.update({
                "conversion_attempted": True,
                "conversion_successful": False,
                "format": "gsm_original"
            })
            return audio_bytes, download_info
    else:
        # No conversion requested
        logger.info(f"✅ [pipeline] Audio download completed for {call_id} (GSM format)")
        return audio_bytes, download_info


# Alternative download methods for flexibility
async def download_audio_via_http(call_id: str, http_config: Dict[str, Any]) -> Tuple[Optional[bytes], Dict[str, Any]]:
    """
    Download audio via HTTP API (alternative to SCP)
    """
    # Placeholder for HTTP-based download implementation
    # This would integrate with Asterisk HTTP APIs or other web endpoints
    download_info = {
        "call_id": call_id,
        "method": "http",
        "success": False,
        "error": "HTTP download method not implemented yet"
    }
    logger.warning(f"⚠️ [http] HTTP audio download not implemented for {call_id}")
    return None, download_info


async def download_audio_local(call_id: str, local_config: Dict[str, Any]) -> Tuple[Optional[bytes], Dict[str, Any]]:
    """
    Access audio file from local filesystem (for same-server deployments)
    """
    try:
        # Default local path configuration
        local_path_template = local_config.get("local_path_template", "/var/spool/asterisk/calls/{call_id}.gsm")
        file_path = local_path_template.format(call_id=call_id)
        
        download_info = {
            "call_id": call_id,
            "method": "local",
            "file_path": file_path,
            "success": False,
            "file_size_bytes": 0,
            "file_size_mb": 0.0,
            "error": None,
            "format": "gsm"
        }
        
        logger.info(f"📁 [local] Accessing local audio file: {file_path}")
        
        if os.path.exists(file_path):
            file_size_bytes = os.path.getsize(file_path)
            
            with open(file_path, 'rb') as f:
                audio_bytes = f.read()
            
            download_info.update({
                "success": True,
                "file_size_bytes": file_size_bytes,
                "file_size_mb": round(file_size_bytes / (1024 * 1024), 2)
            })
            
            logger.info(f"✅ [local] Loaded {download_info['file_size_mb']:.2f}MB local audio file: {call_id}")
            return audio_bytes, download_info
        else:
            error_msg = f"Local audio file not found: {file_path}"
            download_info["error"] = error_msg
            logger.error(f"❌ [local] {error_msg}")
            return None, download_info
            
    except Exception as e:
        error_msg = f"Local file access error: {str(e)}"
        download_info["error"] = error_msg
        logger.error(f"❌ [local] {error_msg}")
        return None, download_info


# Unified download function with method selection
async def download_audio_by_method(call_id: str, method: str, config: Dict[str, Any] = None) -> Tuple[Optional[bytes], Dict[str, Any]]:
    """
    Unified audio download function supporting multiple methods
    
    Args:
        call_id: The unique call ID
        method: Download method ("scp", "http", "local", "disabled")
        config: Method-specific configuration
        
    Returns:
        Tuple of (audio_bytes, download_info)
    """
    
    if method.lower() == "scp":
        return await download_audio_via_scp(call_id, config)
    elif method.lower() == "http":
        return await download_audio_via_http(call_id, config or {})
    elif method.lower() == "local":
        return await download_audio_local(call_id, config or {})
    elif method.lower() == "disabled":
        download_info = {
            "call_id": call_id,
            "method": "disabled",
            "success": False,
            "error": "Audio download disabled by configuration"
        }
        logger.info(f"ℹ️ [disabled] Audio download disabled for {call_id}")
        return None, download_info
    else:
        download_info = {
            "call_id": call_id,
            "method": method,
            "success": False,
            "error": f"Unsupported download method: {method}"
        }
        logger.error(f"❌ [unknown] Unsupported audio download method '{method}' for {call_id}")
        return None, download_info


# For backward compatibility and testing
async def test_scp_download(call_id: str = "1755070077.79708", method: str = "scp"):
    """
    Test function to verify audio download works with different methods
    """
    logger.info(f"🧪 [test] Testing {method} download for call {call_id}")
    
    audio_bytes, download_info = await download_audio_by_method(call_id, method)
    
    if audio_bytes:
        logger.info(f"🧪 [test] SUCCESS: Downloaded {download_info.get('file_size_mb', 0):.2f}MB")
        logger.info(f"🧪 [test] Format: {download_info.get('format', 'unknown')}")
        logger.info(f"🧪 [test] Download info: {download_info}")
        return True
    else:
        logger.error(f"🧪 [test] FAILED: {download_info.get('error', 'Unknown error')}")
        return False


if __name__ == "__main__":
    # Run test when script is executed directly
    import asyncio
    logging.basicConfig(level=logging.INFO)
    
    async def main():
        # Test different methods
        await test_scp_download(method="scp")
        await test_scp_download(method="local")
        await test_scp_download(method="disabled")
    
    asyncio.run(main())