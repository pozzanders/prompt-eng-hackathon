from schema import GuardRailResponse
from chatbot import ProfanityClassifierBot
class InputGuardRail_example1:
    def __init__(self):
        pass

    def check(self, text: str) -> GuardRailResponse:
        if "asshole" in text:
            return GuardRailResponse(
                triggered=True,
                new_text=text.replace("asshole", "nice person"),
                exclude=False,
                reason="Found profanity in the text."
            )
        else:
            return GuardRailResponse(
                triggered=False,
                new_text="",
                exclude=False,
                reason=""
            )


class InputGuardRail_example2:
    def __init__(self):
        self.classifier = ProfanityClassifierBot()

    def check(self, text: str) -> GuardRailResponse:
        classification = self.classifier.classify(text)
        if classification.result: # Triggered
            return GuardRailResponse(
                triggered=True,
                new_text="Your message has been blocked.",
                exclude=True,
                reason="Found profanity in the text."
            )

        return GuardRailResponse(
            triggered=False,
            new_text="",
            exclude=False,
            reason=""
        )

class OutputGuardRail_example1:
    def __init__(self):
        pass

    def check(self, text: str) -> GuardRailResponse:
        # For now, guardrail not triggered
        if "Zanders" in text:
            return GuardRailResponse(
                triggered=True,
                new_text=text.replace("Zanders", "[Redacted]"),
                exclude=False,
                reason="Found 'Zanders' in the text."
            )
        return GuardRailResponse(
            triggered=False,
            new_text="",
            exclude=False,
            reason=""
        )
