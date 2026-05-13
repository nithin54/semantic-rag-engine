from app.dataset import TECHNICAL_DOCUMENTS


class DocumentLoader:
    def __init__(self, documents=None):
        self.documents = documents or TECHNICAL_DOCUMENTS

    def load(self):
        return self.documents

    def texts(self):
        return [document["text"] for document in self.documents]

    def count(self):
        return len(self.documents)
