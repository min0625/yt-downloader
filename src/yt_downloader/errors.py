class DownloaderError(Exception):
    """Base error for the project."""


class InputError(DownloaderError):
    """Invalid user input or arguments."""


class DownloadError(DownloaderError):
    """Error during the download process."""
