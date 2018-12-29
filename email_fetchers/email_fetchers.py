from email_fetchers import GMailFetcher

FETCHER_CLASSES = [
    GMailFetcher,
]

EMAIL_FETCHERS = {}
for fetcher in FETCHER_CLASSES:
    EMAIL_FETCHERS[fetcher.NAME] = fetcher
