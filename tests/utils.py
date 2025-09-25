class MockedTranslator:
    @staticmethod
    async def translate(text: list[str], *_: any) -> list[str]:
        return text
