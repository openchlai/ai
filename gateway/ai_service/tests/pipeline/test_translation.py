import pytest
from unittest.mock import patch, Mock
import torch
from core.pipeline.translation import translate


class TestTranslation:
    """Test text translation pipeline"""

    @patch('core.pipeline.translation.AutoModelForSeq2SeqLM.from_pretrained')
    @patch('core.pipeline.translation.AutoTokenizer.from_pretrained')
    @patch('torch.cuda.is_available')
    def test_translate_success_gpu(self, mock_cuda, mock_tokenizer_class, mock_model_class):
        """Test successful translation on GPU"""
        # Mock CUDA availability
        mock_cuda.return_value = True
        
        # Mock tokenizer
        mock_tokenizer = Mock()
        mock_tokenizer.src_lang = "eng_Latn"
        mock_tokenizer.lang_code_to_id = {"eng_Latn": 256047, "spa_Latn": 256003}
        
        # Mock tokenizer call
        mock_inputs = {
            'input_ids': torch.tensor([[1, 2, 3, 4]]),
            'attention_mask': torch.tensor([[1, 1, 1, 1]])
        }
        mock_tokenizer.return_value = Mock()
        mock_tokenizer.return_value.to.return_value = mock_inputs
        
        # Mock tokenizer decode
        mock_tokenizer.batch_decode.return_value = ["Hola, ¿cómo estás?"]
        
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer
        
        # Mock model
        mock_model = Mock()
        mock_generated = torch.tensor([[5, 6, 7, 8]])
        mock_model.generate.return_value = mock_generated
        mock_model.to.return_value = mock_model
        
        mock_model_class.from_pretrained.return_value = mock_model
        
        input_text = "Hello, how are you?"
        result = translate(input_text, target_lang="spa_Latn")
        
        # Verify model and tokenizer were loaded
        mock_tokenizer_class.from_pretrained.assert_called_once_with("facebook/nllb-200-1.3B")
        mock_model_class.from_pretrained.assert_called_once_with(
            "facebook/nllb-200-1.3B",
            torch_dtype=torch.float16
        )
        
        # Verify model was moved to GPU
        mock_model.to.assert_called_once()
        
        # Verify tokenizer was called correctly
        mock_tokenizer.assert_called_once_with(
            input_text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=1024
        )
        
        # Verify generation was called with correct parameters
        mock_model.generate.assert_called_once()
        call_kwargs = mock_model.generate.call_args[1]
        assert call_kwargs['forced_bos_token_id'] == 256003  # spa_Latn
        assert call_kwargs['max_length'] == 1024
        assert call_kwargs['num_beams'] == 4
        
        assert result == "Hola, ¿cómo estás?"

    @patch('core.pipeline.translation.AutoModelForSeq2SeqLM.from_pretrained')
    @patch('core.pipeline.translation.AutoTokenizer.from_pretrained')
    @patch('torch.cuda.is_available')
    def test_translate_success_cpu(self, mock_cuda, mock_tokenizer_class, mock_model_class):
        """Test successful translation on CPU"""
        # Mock CPU-only environment
        mock_cuda.return_value = False
        
        # Mock tokenizer
        mock_tokenizer = Mock()
        mock_tokenizer.src_lang = "eng_Latn"
        mock_tokenizer.lang_code_to_id = {"eng_Latn": 256047, "fra_Latn": 256057}
        
        mock_inputs = {
            'input_ids': torch.tensor([[1, 2, 3]]),
            'attention_mask': torch.tensor([[1, 1, 1]])
        }
        mock_tokenizer.return_value = Mock()
        mock_tokenizer.return_value.to.return_value = mock_inputs
        mock_tokenizer.batch_decode.return_value = ["Bonjour, comment allez-vous?"]
        
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer
        
        # Mock model
        mock_model = Mock()
        mock_generated = torch.tensor([[4, 5, 6]])
        mock_model.generate.return_value = mock_generated
        mock_model.to.return_value = mock_model
        
        mock_model_class.from_pretrained.return_value = mock_model
        
        input_text = "Hello, how are you?"
        result = translate(input_text, target_lang="fra_Latn")
        
        # Verify model was loaded with float32 for CPU
        mock_model_class.from_pretrained.assert_called_once_with(
            "facebook/nllb-200-1.3B",
            torch_dtype=torch.float32
        )
        
        assert result == "Bonjour, comment allez-vous?"

    @patch('core.pipeline.translation.AutoModelForSeq2SeqLM.from_pretrained')
    @patch('core.pipeline.translation.AutoTokenizer.from_pretrained')
    @patch('torch.cuda.is_available')
    def test_translate_default_target_language(self, mock_cuda, mock_tokenizer_class, mock_model_class):
        """Test translation with default target language"""
        mock_cuda.return_value = False
        
        # Mock tokenizer
        mock_tokenizer = Mock()
        mock_tokenizer.src_lang = "eng_Latn"
        mock_tokenizer.lang_code_to_id = {"eng_Latn": 256047}
        
        mock_inputs = {
            'input_ids': torch.tensor([[1, 2]]),
            'attention_mask': torch.tensor([[1, 1]])
        }
        mock_tokenizer.return_value = Mock()
        mock_tokenizer.return_value.to.return_value = mock_inputs
        mock_tokenizer.batch_decode.return_value = ["Translated text"]
        
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer
        
        # Mock model
        mock_model = Mock()
        mock_model.generate.return_value = torch.tensor([[3, 4]])
        mock_model.to.return_value = mock_model
        
        mock_model_class.from_pretrained.return_value = mock_model
        
        # Call without specifying target_lang (should use default "eng_Latn")
        result = translate("Test text")
        
        # Verify default target language was used
        call_kwargs = mock_model.generate.call_args[1]
        assert 'forced_bos_token_id' in call_kwargs
        
        assert result == "Translated text"

    @patch('core.pipeline.translation.AutoModelForSeq2SeqLM.from_pretrained')
    @patch('core.pipeline.translation.AutoTokenizer.from_pretrained')
    @patch('torch.cuda.is_available')
    def test_translate_long_text_truncation(self, mock_cuda, mock_tokenizer_class, mock_model_class):
        """Test translation with text that exceeds max_length"""
        mock_cuda.return_value = False
        
        # Mock tokenizer
        mock_tokenizer = Mock()
        mock_tokenizer.src_lang = "eng_Latn"
        mock_tokenizer.lang_code_to_id = {"eng_Latn": 256047}
        
        mock_inputs = {
            'input_ids': torch.tensor([[1] * 1024]),  # Max length
            'attention_mask': torch.tensor([[1] * 1024])
        }
        mock_tokenizer.return_value = Mock()
        mock_tokenizer.return_value.to.return_value = mock_inputs
        mock_tokenizer.batch_decode.return_value = ["Truncated translation"]
        
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer
        
        # Mock model
        mock_model = Mock()
        mock_model.generate.return_value = torch.tensor([[2] * 100])
        mock_model.to.return_value = mock_model
        
        mock_model_class.from_pretrained.return_value = mock_model
        
        # Very long text that should be truncated
        long_text = "This is a very long text. " * 200  # Much longer than max_length
        result = translate(long_text)
        
        # Verify tokenizer was called with truncation=True
        mock_tokenizer.assert_called_once()
        call_args, call_kwargs = mock_tokenizer.call_args
        assert call_kwargs['truncation'] is True
        assert call_kwargs['max_length'] == 1024
        
        assert result == "Truncated translation"

    @patch('core.pipeline.translation.AutoModelForSeq2SeqLM.from_pretrained')
    @patch('core.pipeline.translation.AutoTokenizer.from_pretrained')
    def test_translate_empty_text(self, mock_tokenizer_class, mock_model_class):
        """Test translation of empty text"""
        # Mock tokenizer
        mock_tokenizer = Mock()
        mock_tokenizer.src_lang = "eng_Latn"
        mock_tokenizer.lang_code_to_id = {"eng_Latn": 256047}
        
        mock_inputs = {
            'input_ids': torch.tensor([[1]]),  # Minimal input
            'attention_mask': torch.tensor([[1]])
        }
        mock_tokenizer.return_value = Mock()
        mock_tokenizer.return_value.to.return_value = mock_inputs
        mock_tokenizer.batch_decode.return_value = [""]
        
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer
        
        # Mock model
        mock_model = Mock()
        mock_model.generate.return_value = torch.tensor([[2]])
        mock_model.to.return_value = mock_model
        
        mock_model_class.from_pretrained.return_value = mock_model
        
        result = translate("")
        
        assert result == ""

    @patch('core.pipeline.translation.AutoModelForSeq2SeqLM.from_pretrained')
    def test_translate_model_loading_failure(self, mock_model_class):
        """Test handling of model loading failure"""
        mock_model_class.from_pretrained.side_effect = Exception("Model loading failed")
        
        with pytest.raises(RuntimeError, match="Translation failed"):
            translate("Test text")

    @patch('core.pipeline.translation.AutoModelForSeq2SeqLM.from_pretrained')
    @patch('core.pipeline.translation.AutoTokenizer.from_pretrained')
    def test_translate_tokenizer_failure(self, mock_tokenizer_class, mock_model_class):
        """Test handling of tokenizer failure"""
        mock_tokenizer_class.from_pretrained.side_effect = Exception("Tokenizer loading failed")
        
        with pytest.raises(RuntimeError, match="Translation failed"):
            translate("Test text")

    @patch('core.pipeline.translation.AutoModelForSeq2SeqLM.from_pretrained')
    @patch('core.pipeline.translation.AutoTokenizer.from_pretrained')
    @patch('torch.cuda.is_available')
    def test_translate_generation_failure(self, mock_cuda, mock_tokenizer_class, mock_model_class):
        """Test handling of model generation failure"""
        mock_cuda.return_value = False
        
        # Mock tokenizer
        mock_tokenizer = Mock()
        mock_tokenizer.src_lang = "eng_Latn"
        mock_tokenizer.lang_code_to_id = {"eng_Latn": 256047}
        
        mock_inputs = {
            'input_ids': torch.tensor([[1, 2]]),
            'attention_mask': torch.tensor([[1, 1]])
        }
        mock_tokenizer.return_value = Mock()
        mock_tokenizer.return_value.to.return_value = mock_inputs
        
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer
        
        # Mock model that fails during generation
        mock_model = Mock()
        mock_model.generate.side_effect = Exception("Generation failed")
        mock_model.to.return_value = mock_model
        
        mock_model_class.from_pretrained.return_value = mock_model
        
        with pytest.raises(RuntimeError, match="Translation failed"):
            translate("Test text")

    @patch('core.pipeline.translation.AutoModelForSeq2SeqLM.from_pretrained')
    @patch('core.pipeline.translation.AutoTokenizer.from_pretrained')
    @patch('torch.cuda.is_available')
    def test_translate_multiple_languages(self, mock_cuda, mock_tokenizer_class, mock_model_class):
        """Test translation to different target languages"""
        mock_cuda.return_value = False
        
        # Test different language pairs
        test_cases = [
            ("Hello", "spa_Latn", "Hola"),
            ("Hello", "fra_Latn", "Bonjour"),
            ("Hello", "deu_Latn", "Hallo"),
            ("Hello", "ita_Latn", "Ciao")
        ]
        
        for input_text, target_lang, expected_output in test_cases:
            # Reset mocks
            mock_tokenizer_class.reset_mock()
            mock_model_class.reset_mock()
            
            # Mock tokenizer
            mock_tokenizer = Mock()
            mock_tokenizer.src_lang = "eng_Latn"
            mock_tokenizer.lang_code_to_id = {"eng_Latn": 256047, target_lang: 256000}
            
            mock_inputs = {
                'input_ids': torch.tensor([[1, 2]]),
                'attention_mask': torch.tensor([[1, 1]])
            }
            mock_tokenizer.return_value = Mock()
            mock_tokenizer.return_value.to.return_value = mock_inputs
            mock_tokenizer.batch_decode.return_value = [expected_output]
            
            mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer
            
            # Mock model
            mock_model = Mock()
            mock_model.generate.return_value = torch.tensor([[3, 4]])
            mock_model.to.return_value = mock_model
            
            mock_model_class.from_pretrained.return_value = mock_model
            
            result = translate(input_text, target_lang=target_lang)
            
            assert result == expected_output

    @patch('core.pipeline.translation.AutoModelForSeq2SeqLM.from_pretrained')
    @patch('core.pipeline.translation.AutoTokenizer.from_pretrained')
    @patch('torch.cuda.is_available')
    def test_translate_special_characters(self, mock_cuda, mock_tokenizer_class, mock_model_class):
        """Test translation of text with special characters"""
        mock_cuda.return_value = False
        
        # Mock tokenizer
        mock_tokenizer = Mock()
        mock_tokenizer.src_lang = "eng_Latn"
        mock_tokenizer.lang_code_to_id = {"eng_Latn": 256047}
        
        mock_inputs = {
            'input_ids': torch.tensor([[1, 2, 3, 4, 5]]),
            'attention_mask': torch.tensor([[1, 1, 1, 1, 1]])
        }
        mock_tokenizer.return_value = Mock()
        mock_tokenizer.return_value.to.return_value = mock_inputs
        mock_tokenizer.batch_decode.return_value = ["¡Hola! ¿Cómo está usted? Correo: test@email.com"]
        
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer
        
        # Mock model
        mock_model = Mock()
        mock_model.generate.return_value = torch.tensor([[6, 7, 8, 9, 10]])
        mock_model.to.return_value = mock_model
        
        mock_model_class.from_pretrained.return_value = mock_model
        
        # Text with special characters, punctuation, and email
        input_text = "Hello! How are you? Email: test@email.com"
        result = translate(input_text, target_lang="spa_Latn")
        
        assert "¡Hola!" in result
        assert "test@email.com" in result