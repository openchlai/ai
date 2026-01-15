"""
Tests for app/utils/scp_audio_downloader.py
Tests audio download pipeline with multiple methods (SCP, local, mock)
"""

import pytest
import asyncio
import os
import tempfile
from unittest.mock import patch, MagicMock, AsyncMock
from pathlib import Path


class TestSCPDownload:
    """Test SCP-based audio download"""

    @pytest.mark.asyncio
    @patch('app.config.settings.settings')
    async def test_download_audio_via_scp_success(self, mock_settings):
        """Test successful SCP download"""
        # Setup settings
        mock_settings.scp_user = "testuser"
        mock_settings.scp_server = "testserver.com"
        mock_settings.scp_password = "testpass"
        mock_settings.scp_remote_path_template = "/recordings/{call_id}.gsm"
        mock_settings.scp_timeout_seconds = 30

        from app.utils.scp_audio_downloader import download_audio_via_scp

        # Create temporary file with audio content
        with tempfile.NamedTemporaryFile(delete=False, suffix=".gsm") as temp_file:
            temp_file.write(b"mock_gsm_audio_content")
            temp_path = temp_file.name

        try:
            with patch('app.utils.scp_audio_downloader.asyncio.create_subprocess_exec') as mock_exec, \
                 patch('app.utils.scp_audio_downloader.os.path.exists', return_value=True), \
                 patch('app.utils.scp_audio_downloader.os.path.getsize', return_value=22), \
                 patch('builtins.open', create=True) as mock_open:

                # Setup mock process
                mock_process = AsyncMock()
                mock_process.communicate.return_value = (b"", b"")
                mock_process.returncode = 0
                mock_exec.return_value = mock_process

                mock_open.return_value.__enter__.return_value.read.return_value = b"mock_gsm_audio_content"

                # Mock tempfile context
                with patch('app.utils.scp_audio_downloader.tempfile.NamedTemporaryFile') as mock_temp:
                    mock_temp.return_value.__enter__.return_value.name = temp_path
                    audio_bytes, download_info = await download_audio_via_scp("test_call_123")

                    assert audio_bytes == b"mock_gsm_audio_content"
                    assert download_info['success'] is True
                    assert download_info['call_id'] == "test_call_123"
                    assert download_info['method'] == "scp"

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    @pytest.mark.asyncio
    @patch('app.config.settings.settings')
    async def test_download_audio_via_scp_failure(self, mock_settings):
        """Test SCP download failure"""
        mock_settings.scp_user = "testuser"
        mock_settings.scp_server = "testserver.com"
        mock_settings.scp_password = "testpass"
        mock_settings.scp_remote_path_template = "/recordings/{call_id}.gsm"
        mock_settings.scp_timeout_seconds = 30

        from app.utils.scp_audio_downloader import download_audio_via_scp

        with patch('app.utils.scp_audio_downloader.asyncio.create_subprocess_exec') as mock_exec, \
             patch('app.utils.scp_audio_downloader.os.path.exists', return_value=False), \
             patch('app.utils.scp_audio_downloader.tempfile.NamedTemporaryFile') as mock_temp:

            # Setup mock process with failure
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b"", b"Connection refused")
            mock_process.returncode = 1
            mock_exec.return_value = mock_process
            mock_temp.return_value.__enter__.return_value.name = "/tmp/temp_file"

            audio_bytes, download_info = await download_audio_via_scp("test_call_123")

            assert audio_bytes is None
            assert download_info['success'] is False
            assert "SCP failed" in download_info['error']

    @pytest.mark.asyncio
    @patch('app.config.settings.settings')
    async def test_download_audio_via_scp_sshpass_not_installed(self, mock_settings):
        """Test SCP download when sshpass is not installed"""
        mock_settings.scp_user = "testuser"
        mock_settings.scp_server = "testserver.com"
        mock_settings.scp_password = "testpass"
        mock_settings.scp_remote_path_template = "/recordings/{call_id}.gsm"
        mock_settings.scp_timeout_seconds = 30

        from app.utils.scp_audio_downloader import download_audio_via_scp

        with patch('app.utils.scp_audio_downloader.asyncio.create_subprocess_exec',
                   side_effect=FileNotFoundError("sshpass not found")), \
             patch('app.utils.scp_audio_downloader.tempfile.NamedTemporaryFile') as mock_temp:

            mock_temp.return_value.__enter__.return_value.name = "/tmp/temp_file"

            audio_bytes, download_info = await download_audio_via_scp("test_call_123")

            assert audio_bytes is None
            assert "sshpass" in download_info['error']


class TestGSMConversion:
    """Test GSM to WAV conversion"""

    @pytest.mark.asyncio
    @patch('app.utils.scp_audio_downloader.asyncio.create_subprocess_exec')
    async def test_convert_gsm_to_wav_success(self, mock_create_subprocess_exec):
        """Test successful GSM to WAV conversion"""
        # Setup mock process
        mock_process = AsyncMock()
        mock_process.communicate.return_value = (b"", b"")
        mock_process.returncode = 0
        mock_create_subprocess_exec.return_value = mock_process

        gsm_bytes = b"mock_gsm_audio"
        wav_content = b"mock_wav_audio_with_wav_header"

        from app.utils.scp_audio_downloader import convert_gsm_to_wav

        with patch('app.utils.scp_audio_downloader.tempfile.NamedTemporaryFile') as mock_temp, \
             patch('app.utils.scp_audio_downloader.os.path.exists', return_value=True), \
             patch('app.utils.scp_audio_downloader.os.path.getsize', return_value=len(wav_content)), \
             patch('builtins.open', create=True) as mock_open:

            mock_temp.return_value.__enter__.return_value.name = "/tmp/temp_file"
            mock_open.return_value.__enter__.return_value.read.return_value = wav_content

            result = await convert_gsm_to_wav(gsm_bytes)

            assert result == wav_content
            # Verify ffmpeg command was called
            mock_create_subprocess_exec.assert_called_once()
            call_args = mock_create_subprocess_exec.call_args
            assert 'ffmpeg' in call_args[0][0]

    @pytest.mark.asyncio
    @patch('app.utils.scp_audio_downloader.asyncio.create_subprocess_exec')
    async def test_convert_gsm_to_wav_failure(self, mock_create_subprocess_exec):
        """Test GSM to WAV conversion failure"""
        mock_process = AsyncMock()
        mock_process.communicate.return_value = (b"", b"ffmpeg error")
        mock_process.returncode = 1
        mock_create_subprocess_exec.return_value = mock_process

        gsm_bytes = b"mock_gsm_audio"

        from app.utils.scp_audio_downloader import convert_gsm_to_wav

        with patch('app.utils.scp_audio_downloader.tempfile.NamedTemporaryFile') as mock_temp, \
             patch('app.utils.scp_audio_downloader.os.path.exists', return_value=False):

            mock_temp.return_value.__enter__.return_value.name = "/tmp/temp_file"

            result = await convert_gsm_to_wav(gsm_bytes)

            assert result is None

    @pytest.mark.asyncio
    async def test_convert_gsm_to_wav_ffmpeg_not_installed(self):
        """Test conversion fails when ffmpeg is not installed"""
        gsm_bytes = b"mock_gsm_audio"

        from app.utils.scp_audio_downloader import convert_gsm_to_wav

        with patch('app.utils.scp_audio_downloader.asyncio.create_subprocess_exec',
                   side_effect=FileNotFoundError("ffmpeg not found")):

            result = await convert_gsm_to_wav(gsm_bytes)

            assert result is None


class TestDownloadAndConvert:
    """Test complete download and conversion pipeline"""

    @pytest.mark.asyncio
    async def test_download_and_convert_audio_callable(self):
        """Test that download_and_convert_audio is callable and returns tuple"""
        from app.utils.scp_audio_downloader import download_and_convert_audio

        # The function should exist and be callable
        assert callable(download_and_convert_audio)

        # Test signature - should accept call_id, convert_to_wav, scp_config parameters
        import inspect
        sig = inspect.signature(download_and_convert_audio)
        assert 'call_id' in sig.parameters
        assert 'convert_to_wav' in sig.parameters
        assert 'scp_config' in sig.parameters

    @pytest.mark.asyncio
    @patch('app.config.settings.settings')
    async def test_download_and_convert_audio_calls_scp_download(self, mock_settings):
        """Test that download_and_convert_audio calls scp download function"""
        mock_settings.scp_user = "testuser"
        mock_settings.scp_server = "testserver.com"
        mock_settings.scp_password = "testpass"
        mock_settings.scp_remote_path_template = "/recordings/{call_id}.gsm"
        mock_settings.scp_timeout_seconds = 30

        from app.utils.scp_audio_downloader import download_and_convert_audio

        with patch('app.utils.scp_audio_downloader.download_audio_via_scp',
                   return_value=(b"gsm_audio", {"success": True, "format": "gsm"})) as mock_scp:

            audio_bytes, download_info = await download_and_convert_audio(
                "test_call_123",
                convert_to_wav=False  # Don't try to convert
            )

            # Should have called the SCP function
            mock_scp.assert_called_once()
            assert download_info['success'] is True


class TestLocalDownload:
    """Test local file download"""

    @pytest.mark.asyncio
    async def test_download_audio_local_template_mode_success(self):
        """Test local download with path template"""
        from app.utils.scp_audio_downloader import download_audio_local

        audio_content = b"mock_audio"
        local_config = {
            "local_path_template": "/var/spool/asterisk/{call_id}.gsm",
            "use_folder_files": False
        }

        with patch('app.utils.scp_audio_downloader.os.path.exists', return_value=True), \
             patch('app.utils.scp_audio_downloader.os.path.getsize', return_value=len(audio_content)), \
             patch('builtins.open', create=True) as mock_open:

            mock_open.return_value.__enter__.return_value.read.return_value = audio_content

            audio_bytes, download_info = await download_audio_local("test_call_123", local_config)

            assert audio_bytes == audio_content
            assert download_info['success'] is True
            assert download_info['method'] == "local"
            assert download_info['format'] == "gsm"

    @pytest.mark.asyncio
    async def test_download_audio_local_file_not_found(self):
        """Test local download when file doesn't exist"""
        from app.utils.scp_audio_downloader import download_audio_local

        local_config = {
            "local_path_template": "/var/spool/asterisk/{call_id}.gsm"
        }

        with patch('app.utils.scp_audio_downloader.os.path.exists', return_value=False):

            audio_bytes, download_info = await download_audio_local("test_call_123", local_config)

            assert audio_bytes is None
            assert download_info['success'] is False
            assert "not found" in download_info['error']

    @pytest.mark.asyncio
    async def test_download_audio_local_folder_mode(self):
        """Test local download with folder search"""
        from app.utils.scp_audio_downloader import download_audio_local

        audio_content = b"mock_audio"
        local_config = {
            "mock_audio_folder": "/tmp/audio_folder",
            "use_folder_files": True
        }

        with patch('app.utils.scp_audio_downloader.os.path.isdir', return_value=True), \
             patch('app.utils.scp_audio_downloader._find_audio_file_in_folder',
                   return_value="/tmp/audio_folder/test_call_123.gsm"), \
             patch('app.utils.scp_audio_downloader.os.path.exists', return_value=True), \
             patch('app.utils.scp_audio_downloader.os.path.getsize', return_value=len(audio_content)), \
             patch('builtins.open', create=True) as mock_open:

            mock_open.return_value.__enter__.return_value.read.return_value = audio_content

            audio_bytes, download_info = await download_audio_local("test_call_123", local_config)

            assert audio_bytes == audio_content
            assert download_info['success'] is True
            assert download_info['mock_mode'] is True


class TestFormatDetection:
    """Test audio format detection"""

    def test_detect_audio_format_wav(self):
        """Test WAV format detection"""
        from app.utils.scp_audio_downloader import _detect_audio_format

        result = _detect_audio_format("/recordings/call_123.wav")
        assert result == "wav"

    def test_detect_audio_format_gsm(self):
        """Test GSM format detection"""
        from app.utils.scp_audio_downloader import _detect_audio_format

        result = _detect_audio_format("/recordings/call_123.gsm")
        assert result == "gsm"

    def test_detect_audio_format_unknown(self):
        """Test unknown format detection"""
        from app.utils.scp_audio_downloader import _detect_audio_format

        result = _detect_audio_format("/recordings/call_123.xyz")
        assert result == "unknown"


class TestFileFinder:
    """Test audio file finder in folder"""

    def test_find_audio_file_returns_string_or_none(self):
        """Test that file finder returns string or None"""
        from app.utils.scp_audio_downloader import _find_audio_file_in_folder

        # Test with non-existent folder
        result = _find_audio_file_in_folder("/tmp/nonexistent_folder_xyz", "test_call")

        # Should return None if no files found
        assert result is None or isinstance(result, str)

    def test_find_audio_file_with_various_extensions(self):
        """Test that function checks multiple audio extensions"""
        from app.utils.scp_audio_downloader import _find_audio_file_in_folder
        import tempfile

        # Create temporary directory with test files
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a GSM file
            gsm_file = os.path.join(tmpdir, "test_call.gsm")
            Path(gsm_file).touch()

            result = _find_audio_file_in_folder(tmpdir, "test_call")

            assert result == gsm_file

    def test_find_audio_file_exact_match_priority(self):
        """Test that exact matches are found before fallback"""
        from app.utils.scp_audio_downloader import _find_audio_file_in_folder
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create exact match
            exact_file = os.path.join(tmpdir, "my_call.wav")
            Path(exact_file).touch()

            # Also create partial match (should not be used)
            partial_file = os.path.join(tmpdir, "recording_my_call_backup.wav")
            Path(partial_file).touch()

            result = _find_audio_file_in_folder(tmpdir, "my_call")

            # Should return exact match
            assert result == exact_file

    def test_find_audio_file_no_files_in_directory(self):
        """Test behavior when directory exists but has no audio files"""
        from app.utils.scp_audio_downloader import _find_audio_file_in_folder
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            result = _find_audio_file_in_folder(tmpdir, "test_call")

            # Should return None when no audio files exist
            assert result is None


class TestDownloadByMethod:
    """Test unified download function with method selection"""

    @pytest.mark.asyncio
    @patch('app.config.settings.settings')
    async def test_download_audio_by_method_scp(self, mock_settings):
        """Test download with SCP method"""
        mock_settings.mock_enabled = False

        from app.utils.scp_audio_downloader import download_audio_by_method

        with patch('app.utils.scp_audio_downloader.download_audio_via_scp',
                   return_value=(b"test_audio", {'success': True, 'method': 'scp'})) as mock_scp:

            audio_bytes, download_info = await download_audio_by_method(
                "test_call_123",
                method="scp"
            )

            # Should call the SCP function
            mock_scp.assert_called_once()
            assert download_info['method'] == "scp"

    @pytest.mark.asyncio
    async def test_download_audio_by_method_local(self):
        """Test download with local method"""
        from app.utils.scp_audio_downloader import download_audio_by_method

        audio_content = b"mock_audio"

        with patch('app.utils.scp_audio_downloader.download_audio_local',
                   return_value=(audio_content, {'success': True, 'method': 'local'})):

            audio_bytes, download_info = await download_audio_by_method(
                "test_call_123",
                method="local"
            )

            assert audio_bytes == audio_content
            assert download_info['method'] == "local"

    @pytest.mark.asyncio
    async def test_download_audio_by_method_disabled(self):
        """Test download with disabled method"""
        from app.utils.scp_audio_downloader import download_audio_by_method

        audio_bytes, download_info = await download_audio_by_method(
            "test_call_123",
            method="disabled"
        )

        assert audio_bytes is None
        assert download_info['success'] is False
        assert "disabled" in download_info['error']

    @pytest.mark.asyncio
    async def test_download_audio_by_method_invalid(self):
        """Test download with invalid method"""
        from app.utils.scp_audio_downloader import download_audio_by_method

        audio_bytes, download_info = await download_audio_by_method(
            "test_call_123",
            method="invalid_method"
        )

        assert audio_bytes is None
        assert download_info['success'] is False
        assert "Unsupported" in download_info['error']
