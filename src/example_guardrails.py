from schema import GuardRailResponse
from chatbot import ProfanityClassifierBot
class InputGuardRail_example1:
    def __init__(self):
        pass

    def check(self, text: str) -> GuardRailResponse:
        if "asshole" in text:
            return GuardRailResponse(
                triggered=True,
                rewritten=text.replace("asshole", "nice person"),
                fallback=None,
                reason="Found profanity in the text."
            )
        else:
            return GuardRailResponse(
                triggered=False,
                rewritten="",
                fallback=None,
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
                rewritten="",
                fallback="Your message has been blocked.",
                reason="Found profanity in the text."
            )

        return GuardRailResponse(
            triggered=False,
            rewritten="",
            fallback=None,
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
                rewritten=text.replace("Zanders", "[Redacted]"),
                fallback=None,
                reason="Found 'Zanders' in the text."
            )
        return GuardRailResponse(
            triggered=False,
            rewritten="",
            fallback=None,
            reason=""
        )
