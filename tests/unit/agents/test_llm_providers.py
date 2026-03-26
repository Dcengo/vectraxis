"""Tests for LangChainLLMProvider."""

from unittest.mock import MagicMock

from vectraxis.agents.base import LLMProvider
from vectraxis.agents.llm_providers import LangChainLLMProvider


class TestLangChainLLMProvider:
    """Tests for the LangChainLLMProvider wrapper."""

    def test_satisfies_llm_provider_protocol(self):
        mock_model = MagicMock()
        provider = LangChainLLMProvider(chat_model=mock_model)
        assert isinstance(provider, LLMProvider)

    def test_generate_calls_invoke(self):
        mock_model = MagicMock()
        mock_model.invoke.return_value = MagicMock(content="Hello from LLM")
        provider = LangChainLLMProvider(chat_model=mock_model, model_name="test-model")

        result = provider.generate("Tell me a joke")
        assert result == "Hello from LLM"
        mock_model.invoke.assert_called_once()

    def test_generate_with_context(self):
        mock_model = MagicMock()
        mock_model.invoke.return_value = MagicMock(content="Contextual answer")
        provider = LangChainLLMProvider(chat_model=mock_model)

        result = provider.generate("Question?", context=["fact1", "fact2"])
        assert result == "Contextual answer"
        # Should have system message + human message
        call_args = mock_model.invoke.call_args[0][0]
        assert len(call_args) == 2

    def test_generate_without_context(self):
        mock_model = MagicMock()
        mock_model.invoke.return_value = MagicMock(content="Answer")
        provider = LangChainLLMProvider(chat_model=mock_model)

        provider.generate("Question?")
        call_args = mock_model.invoke.call_args[0][0]
        # Only human message, no system message
        assert len(call_args) == 1

    def test_model_name_property(self):
        mock_model = MagicMock()
        provider = LangChainLLMProvider(chat_model=mock_model, model_name="gpt-4o")
        assert provider.model_name == "gpt-4o"

    def test_model_name_default_empty(self):
        mock_model = MagicMock()
        provider = LangChainLLMProvider(chat_model=mock_model)
        assert provider.model_name == ""
