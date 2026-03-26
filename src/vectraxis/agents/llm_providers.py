"""LangChain-based LLM provider that satisfies the LLMProvider protocol."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from langchain_core.language_models.chat_models import BaseChatModel


class LangChainLLMProvider:
    """Wraps any LangChain BaseChatModel to satisfy the LLMProvider protocol."""

    def __init__(self, chat_model: BaseChatModel, model_name: str = "") -> None:
        self._chat_model = chat_model
        self._model_name = model_name

    @property
    def model_name(self) -> str:
        return self._model_name

    def generate(self, prompt: str, context: list[str] | None = None) -> str:
        """Generate a response using the LangChain chat model."""
        from langchain_core.messages import HumanMessage, SystemMessage

        messages: list[SystemMessage | HumanMessage] = []
        if context:
            context_text = "\n\n".join(context)
            system_content = (
                f"Use the following context to inform your response:\n\n{context_text}"
            )
            messages.append(SystemMessage(content=system_content))
        messages.append(HumanMessage(content=prompt))

        response = self._chat_model.invoke(messages)
        return str(response.content)
