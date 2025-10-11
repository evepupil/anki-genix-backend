import requests

class AnkiClient:
    def __init__(self, host='http://localhost:8765'):
        self.host = host

    def request(self, action, params=None):
        """
        向AnkiConnect发送请求。
        """
        payload = {
            'action': action,
            'version': 6,
            'params': params or {}
        }
        response = requests.post(self.host, json=payload)
        response.raise_for_status()
        result = response.json()
        if result.get('error'):
            raise Exception(f"AnkiConnect error: {result['error']}")
        return result.get('result')

    def add_note(self, deck_name, model_name, fields, tags=None, options=None):
        """
        上传单个Anki牌。
        """
        note = {
            'deckName': deck_name,
            'modelName': model_name,
            'fields': fields,
            'tags': tags or [],
            'options': options or {},
        }
        return self.request('addNote', {'note': note})

    def add_notes(self, notes):
        """
        批量上传Anki牌。
        notes: list of note dicts (结构同 add_note 的 note)
        """
        return self.request('addNotes', {'notes': notes})

    def get_deck_names(self):
        return self.request('deckNames')

    def get_model_names(self):
        return self.request('modelNames') 