from dataclasses import dataclass

from openai import AsyncOpenAI


@dataclass(frozen=True)
class ModerationResult:
    flagged: bool
    categories: list[str]


async def check_moderation(message: str, client: AsyncOpenAI) -> ModerationResult:
    """Run the message through OpenAI's moderation endpoint."""
    response = await client.moderations.create(input=message)
    result = response.results[0]
    flagged_categories = [
        category
        for category, is_flagged in result.categories.model_dump().items()
        if is_flagged
    ]
    return ModerationResult(flagged=result.flagged, categories=flagged_categories)
