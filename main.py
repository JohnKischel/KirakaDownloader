from Kiraka import Downloader

# Example usage
Downloader().set_downloadpath(r"C:\temp")
links = Downloader.get_links(("https://kinder.wdr.de/radio/kiraka/hoeren/hoerspiele/kinderhoerspiel-podcast-102.html",))
Downloader.get_file_by_link(links,download=False)
