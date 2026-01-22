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

    @pytest.mark.asyncio
    async def test_download_audio_by_method_http(self):
        """Test download with HTTP method"""
        from app.utils.scp_audio_downloader import download_audio_by_method

        with patch('app.utils.scp_audio_downloader.download_audio_via_http',
                   return_value=(None, {'success': False, 'method': 'http', 'error': 'Not implemented'})):

            audio_bytes, download_info = await download_audio_by_method(
                "test_call_123",
                method="http"
            )

            assert download_info['method'] == "http"

    @pytest.mark.asyncio
    @patch('app.config.settings.settings')
    async def test_download_audio_by_method_mock(self, mock_settings):
        """Test download with mock method"""
        mock_settings.mock_enabled = True
        mock_settings.mock_audio_folder = "/tmp/mock_audio"
        mock_settings.mock_use_folder_files = True

        from app.utils.scp_audio_downloader import download_audio_by_method

        with patch('app.utils.scp_audio_downloader.download_audio_for_mock',
                   return_value=(b"mock_audio", {'success': True, 'method': 'mock'})):

            audio_bytes, download_info = await download_audio_by_method(
                "test_call_123",
                method="mock"
            )

            assert download_info['method'] == "mock"

    @pytest.mark.asyncio
    @patch('app.config.settings.settings')
    async def test_download_audio_by_method_scp_with_mock_override(self, mock_settings):
        """Test that SCP method uses mock when mock_enabled and mock_skip_scp_download"""
        mock_settings.mock_enabled = True
        mock_settings.mock_skip_scp_download = True
        mock_settings.mock_audio_folder = "/tmp/mock_audio"
        mock_settings.mock_use_folder_files = True

        from app.utils.scp_audio_downloader import download_audio_by_method

        with patch('app.utils.scp_audio_downloader.download_audio_for_mock',
                   return_value=(b"mock_audio", {'success': True, 'method': 'mock'})) as mock_fn:

            audio_bytes, download_info = await download_audio_by_method(
                "test_call_123",
                method="scp"
            )

            # Should have called mock download instead of SCP
            mock_fn.assert_called_once()


class TestHTTPDownload:
    """Test HTTP-based audio download"""

    @pytest.mark.asyncio
    async def test_download_audio_via_http_not_implemented(self):
        """Test HTTP download returns not implemented error"""
        from app.utils.scp_audio_downloader import download_audio_via_http

        audio_bytes, download_info = await download_audio_via_http(
            "test_call_123",
            {"base_url": "http://example.com"}
        )

        assert audio_bytes is None
        assert download_info['success'] is False
        assert download_info['method'] == "http"
        assert "not implemented" in download_info['error']


class TestMockDownload:
    """Test mock audio download"""

    @pytest.mark.asyncio
    @patch('app.config.settings.settings')
    async def test_download_audio_for_mock_disabled(self, mock_settings):
        """Test mock download when mock mode is disabled"""
        mock_settings.mock_enabled = False

        from app.utils.scp_audio_downloader import download_audio_for_mock

        audio_bytes, download_info = await download_audio_for_mock("test_call_123")

        assert audio_bytes is None
        assert download_info['success'] is False
        assert "not enabled" in download_info['error']

    @pytest.mark.asyncio
    @patch('app.config.settings.settings')
    async def test_download_audio_for_mock_enabled(self, mock_settings):
        """Test mock download when mock mode is enabled"""
        mock_settings.mock_enabled = True
        mock_settings.mock_audio_folder = "/tmp/mock_audio"
        mock_settings.mock_use_folder_files = True

        from app.utils.scp_audio_downloader import download_audio_for_mock

        with patch('app.utils.scp_audio_downloader.download_audio_local',
                   return_value=(b"mock_audio", {'success': True, 'method': 'local'})):

            audio_bytes, download_info = await download_audio_for_mock("test_call_123")

            assert audio_bytes == b"mock_audio"
            assert download_info['method'] == "mock"


class TestTestSCPDownload:
    """Test the test_scp_download function"""

    @pytest.mark.asyncio
    async def test_test_scp_download_success(self):
        """Test the test_scp_download function with success"""
        from app.utils.scp_audio_downloader import test_scp_download

        with patch('app.utils.scp_audio_downloader.download_audio_by_method',
                   return_value=(b"test_audio", {'success': True, 'file_size_mb': 1.5, 'format': 'wav'})):

            result = await test_scp_download("test_call", method="scp")

            assert result is True

    @pytest.mark.asyncio
    async def test_test_scp_download_failure(self):
        """Test the test_scp_download function with failure"""
        from app.utils.scp_audio_downloader import test_scp_download

        with patch('app.utils.scp_audio_downloader.download_audio_by_method',
                   return_value=(None, {'success': False, 'error': 'Connection failed'})):

            result = await test_scp_download("test_call", method="scp")

            assert result is False


class TestDownloadAndConvertPipeline:
    """Additional tests for download and convert pipeline"""

    @pytest.mark.asyncio
    async def test_download_and_convert_with_conversion_success(self):
        """Test download and convert with successful WAV conversion"""
        from app.utils.scp_audio_downloader import download_and_convert_audio

        gsm_bytes = b"mock_gsm_audio"
        wav_bytes = b"mock_wav_audio_converted"

        with patch('app.utils.scp_audio_downloader.download_audio_via_scp',
                   return_value=(gsm_bytes, {'success': True, 'format': 'gsm', 'file_size_bytes': 100, 'file_size_mb': 0.1})), \
             patch('app.utils.scp_audio_downloader.convert_gsm_to_wav',
                   return_value=wav_bytes):

            audio_bytes, download_info = await download_and_convert_audio(
                "test_call_123",
                convert_to_wav=True
            )

            assert audio_bytes == wav_bytes
            assert download_info['conversion_successful'] is True

    @pytest.mark.asyncio
    async def test_download_and_convert_with_conversion_failure(self):
        """Test download and convert when WAV conversion fails"""
        from app.utils.scp_audio_downloader import download_and_convert_audio

        gsm_bytes = b"mock_gsm_audio"

        with patch('app.utils.scp_audio_downloader.download_audio_via_scp',
                   return_value=(gsm_bytes, {'success': True, 'format': 'gsm', 'file_size_bytes': 100, 'file_size_mb': 0.1})), \
             patch('app.utils.scp_audio_downloader.convert_gsm_to_wav',
                   return_value=None):

            audio_bytes, download_info = await download_and_convert_audio(
                "test_call_123",
                convert_to_wav=True
            )

            # Should return original GSM bytes when conversion fails
            assert audio_bytes == gsm_bytes
            assert download_info['conversion_successful'] is False
            assert download_info['format'] == "gsm_original"

    @pytest.mark.asyncio
    async def test_download_and_convert_download_failure(self):
        """Test download and convert when download fails"""
        from app.utils.scp_audio_downloader import download_and_convert_audio

        with patch('app.utils.scp_audio_downloader.download_audio_via_scp',
                   return_value=(None, {'success': False, 'error': 'Connection refused'})):

            audio_bytes, download_info = await download_and_convert_audio(
                "test_call_123",
                convert_to_wav=True
            )

            assert audio_bytes is None
            assert download_info['success'] is False


class TestSCPDownloadEdgeCases:
    """Edge cases for SCP download"""

    @pytest.mark.asyncio
    @patch('app.config.settings.settings')
    async def test_download_audio_via_scp_with_custom_config(self, mock_settings):
        """Test SCP download with custom config override"""
        from app.utils.scp_audio_downloader import download_audio_via_scp

        custom_config = {
            "user": "custom_user",
            "server": "custom_server.com",
            "password": "custom_pass",
            "remote_path_template": "/custom/path/{call_id}.wav",
            "timeout_seconds": 60
        }

        with patch('app.utils.scp_audio_downloader.asyncio.create_subprocess_exec') as mock_exec, \
             patch('app.utils.scp_audio_downloader.tempfile.NamedTemporaryFile') as mock_temp, \
             patch('app.utils.scp_audio_downloader.os.path.exists', return_value=False):

            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b"", b"")
            mock_process.returncode = 1
            mock_exec.return_value = mock_process
            mock_temp.return_value.__enter__.return_value.name = "/tmp/temp_file"

            audio_bytes, download_info = await download_audio_via_scp("test_call_123", custom_config)

            assert download_info['server'] == "custom_server.com"

    @pytest.mark.asyncio
    @patch('app.config.settings.settings')
    async def test_download_audio_via_scp_empty_file(self, mock_settings):
        """Test SCP download when file is empty"""
        mock_settings.scp_user = "testuser"
        mock_settings.scp_server = "testserver.com"
        mock_settings.scp_password = "testpass"
        mock_settings.scp_remote_path_template = "/recordings/{call_id}.gsm"
        mock_settings.scp_timeout_seconds = 30

        from app.utils.scp_audio_downloader import download_audio_via_scp

        with patch('app.utils.scp_audio_downloader.asyncio.create_subprocess_exec') as mock_exec, \
             patch('app.utils.scp_audio_downloader.os.path.exists', return_value=True), \
             patch('app.utils.scp_audio_downloader.os.path.getsize', return_value=0), \
             patch('app.utils.scp_audio_downloader.tempfile.NamedTemporaryFile') as mock_temp:

            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b"", b"")
            mock_process.returncode = 0
            mock_exec.return_value = mock_process
            mock_temp.return_value.__enter__.return_value.name = "/tmp/temp_file"

            audio_bytes, download_info = await download_audio_via_scp("test_call_123")

            assert audio_bytes is None
            assert download_info['success'] is False
            assert "empty" in download_info['error']

    @pytest.mark.asyncio
    @patch('app.config.settings.settings')
    async def test_download_audio_via_scp_general_exception(self, mock_settings):
        """Test SCP download with general exception"""
        mock_settings.scp_user = "testuser"
        mock_settings.scp_server = "testserver.com"
        mock_settings.scp_password = "testpass"
        mock_settings.scp_remote_path_template = "/recordings/{call_id}.gsm"
        mock_settings.scp_timeout_seconds = 30

        from app.utils.scp_audio_downloader import download_audio_via_scp

        with patch('app.utils.scp_audio_downloader.asyncio.create_subprocess_exec',
                   side_effect=Exception("Unexpected error")), \
             patch('app.utils.scp_audio_downloader.tempfile.NamedTemporaryFile') as mock_temp:

            mock_temp.return_value.__enter__.return_value.name = "/tmp/temp_file"

            audio_bytes, download_info = await download_audio_via_scp("test_call_123")

            assert audio_bytes is None
            assert "SCP error" in download_info['error']


class TestFormatDetectionExtended:
    """Extended format detection tests"""

    def test_detect_audio_format_wav16(self):
        """Test wav16 format detection"""
        from app.utils.scp_audio_downloader import _detect_audio_format

        result = _detect_audio_format("/recordings/call_123.wav16")
        assert result == "wav16"

    def test_detect_audio_format_mp3(self):
        """Test MP3 format detection"""
        from app.utils.scp_audio_downloader import _detect_audio_format

        result = _detect_audio_format("/recordings/call_123.mp3")
        assert result == "mp3"

    def test_detect_audio_format_ogg(self):
        """Test OGG format detection"""
        from app.utils.scp_audio_downloader import _detect_audio_format

        result = _detect_audio_format("/recordings/call_123.ogg")
        assert result == "ogg"

    def test_detect_audio_format_flac(self):
        """Test FLAC format detection"""
        from app.utils.scp_audio_downloader import _detect_audio_format

        result = _detect_audio_format("/recordings/call_123.flac")
        assert result == "flac"


class TestLocalDownloadExtended:
    """Extended local download tests"""

    @pytest.mark.asyncio
    async def test_download_audio_local_exception_handling(self):
        """Test local download exception handling"""
        from app.utils.scp_audio_downloader import download_audio_local

        local_config = {
            "local_path_template": "/var/spool/asterisk/{call_id}.gsm"
        }

        with patch('app.utils.scp_audio_downloader.os.path.exists', side_effect=Exception("Permission denied")):

            audio_bytes, download_info = await download_audio_local("test_call_123", local_config)

            assert audio_bytes is None
            assert download_info['success'] is False
            assert "error" in download_info['error'].lower()

    @pytest.mark.asyncio
    async def test_download_audio_local_folder_no_files(self):
        """Test local download folder mode when no files match"""
        from app.utils.scp_audio_downloader import download_audio_local

        local_config = {
            "mock_audio_folder": "/tmp/audio_folder",
            "use_folder_files": True
        }

        with patch('app.utils.scp_audio_downloader.os.path.isdir', return_value=True), \
             patch('app.utils.scp_audio_downloader._find_audio_file_in_folder', return_value=None):

            audio_bytes, download_info = await download_audio_local("test_call_123", local_config)

            assert audio_bytes is None
            assert download_info['success'] is False
