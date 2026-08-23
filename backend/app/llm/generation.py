import time
from dataclasses import dataclass

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI


@dataclass
class GenerationResult:
    text: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: float
    truncated: bool = False


class GroundedGenerator:
    """Generic 'answer this question using only the given context' LLM
    call, shared by the Knowledge Agent's RAG and web-search paths."""

    def __init__(
        self,
        model: str,
        api_key: str,
        temperature: float = 0.3,
        max_tokens: int | None = None,
    ):
        self.model = model
        self._llm = ChatOpenAI(
            model=model, api_key=api_key, temperature=temperature, max_tokens=max_tokens
        )

    async def generate(self, system_prompt: str, question: str, context: str) -> GenerationResult:
        start = time.perf_counter()
        ai_message = await self._llm.ainvoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Contexto:\n{context}\n\nPergunta do usuário: {question}"),
            ]
        )
        latency_ms = (time.perf_counter() - start) * 1000
        usage = getattr(ai_message, "usage_metadata", None) or {}
        metadata = getattr(ai_message, "response_metadata", None) or {}
        return GenerationResult(
            text=ai_message.content,
            model=self.model,
            prompt_tokens=usage.get("input_tokens", 0),
            completion_tokens=usage.get("output_tokens", 0),
            latency_ms=latency_ms,
            truncated=metadata.get("finish_reason") == "length",
        )
