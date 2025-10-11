from .anki_client import AnkiClient

class AnkiService:
    def __init__(self, host='http://localhost:8765'):
        self.client = AnkiClient(host)

    def upload_flashcards(self, deck_name, model_name, flashcards, tags=None, options=None):
        """
        批量上传flashcards到指定牌桌。
        flashcards: list of dict, 每个dict为fields字段
        """
        notes = [
            {
                'deckName': deck_name,
                'modelName': model_name,
                'fields': fields,
                'tags': tags or [],
                'options': options or {},
            }
            for fields in flashcards
        ]
        return self.client.add_notes(notes)

    def get_decks(self):
        return self.client.get_deck_names()

    def get_models(self):
        return self.client.get_model_names() 