from schema import GuardRailResponse

class InputGuardRail:
    def __init__(self):
        """
        Put any initialization code or parameters here.
        For now, we keep it empty.
        """
        pass

    def check(self, text: str) -> GuardRailResponse:
        """
        Your custom guardrail logic that inspects user input.
        Return a GuardRailResponse object.
        """
        # For now, guardrail not triggered
        return GuardRailResponse(triggered=False, new_text="", exclude=False)


class OutputGuardRail:
    def __init__(self):
        """
        Put any initialization code or parameters here.
        For now, we keep it empty.
        """
        pass

    def check(self, text: str) -> GuardRailResponse:
        """
        Your custom guardrail logic that inspects model output.
        Return a GuardRailResponse object.
        """
        # For now, guardrail not triggered
        return GuardRailResponse(triggered=False, new_text="", exclude=False)
