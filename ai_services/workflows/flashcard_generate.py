from .base_workflow import AIWorkflow

class FlashcardGenerateWorkflow(AIWorkflow):
    def __init__(self, card_type="basic_card", ai_service=None):
        self.prompt_key = card_type
        super().__init__(ai_service) 