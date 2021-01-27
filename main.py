from Kiraka import Downloader

# Set the download path where all files are stored
Downloader().set_downloadpath(r"\\192.168.0.200\home\004_Music\WDR5")

# Get all js files cause they contain the link to the mp3.
links = Downloader.get_links((Downloader.KIRAKA_SENDUNGEN,))
Downloader.get_file_by_link(links, download=True)

# Parse all js files and extract the link to download all mp3 files
links = Downloader.parse_js_file()
Downloader.get_file_by_link(links, download=True)
