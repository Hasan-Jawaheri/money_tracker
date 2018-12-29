import inspect
import email_fetchers
FETCHER_CLASSES = filter(lambda attr: inspect.isclass(attr) and issubclass(attr, email_fetchers.EmailFetcherInterface) and attr != email_fetchers.EmailFetcherInterface, map(lambda module_attr: getattr(email_fetchers, module_attr), dir(email_fetchers)))

EMAIL_FETCHERS = {}
for fetcher in FETCHER_CLASSES:
    EMAIL_FETCHERS[fetcher.NAME] = fetcher
