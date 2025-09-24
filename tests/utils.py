class MockedTranslator:
    @staticmethod
    async def translate(text: list[str], *_) -> list[str]:
        return text
