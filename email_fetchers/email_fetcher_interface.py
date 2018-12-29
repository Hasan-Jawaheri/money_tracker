
class EmailFetcherInterface:
    NAME = "<Unknown>"

    @staticmethod
    def fetchEmails(query):
        raise Exception("Unimplemented")
    
    @staticmethod
    def downloadAllAttachments(message_id, storage_folder='attachments'):
        raise Exception("Unimplemented")
