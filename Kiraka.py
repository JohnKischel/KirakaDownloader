import urllib3.request
import re
import os.path
import wget
from bs4 import BeautifulSoup as Soup
from tempfile import gettempdir
from shutil import rmtree
from glob import glob

class Downloader:

    download_path = os.path.join(gettempdir(), "kiraka")
    KIRAKA_SENDUNGEN = 'https://kinder.wdr.de/radio/kiraka/kiraka-on-demand-100.html'
    KIRAKA_HOERSPIELE = 'https://kinder.wdr.de/radio/kiraka/hoeren/hoerspiele/kinderhoerspiel-podcast-102.html'

    def __init__(self):
        if not os.path.exists(self.download_path):
            os.mkdir(self.download_path)
            print(f"Current download path: [{self.download_path}]")

    @classmethod
    def clear_cache(cls):
        rmtree(cls.download_path, ignore_errors=True)

    @classmethod
    def set_downloadpath(cls, download_path):
        cls.download_path = download_path
        print(f"Download path set to: [{download_path}]")

    @staticmethod
    def get_links(websites: tuple = ('https://kinder.wdr.de/radio/kiraka/kiraka-on-demand-100.html',)):
        """
        Link zu den Hörspielen
        https://kinder.wdr.de/radio/kiraka/hoeren/hoerspiele/kinderhoerspiel-podcast-102.html
        Kiraka Sendung
        https://kinder.wdr.de/radio/kiraka/kiraka-on-demand-100.html
        :param websites: Insert a tuple of websites ins this variable. For example (https://wdr.xxx/demand.html,) or
        (https://wdr.xxx/demand.html, https://wdr.yyy/demand.html)
        :return: This function return a list a links as str
        """
        link_container = []
        if not websites or not isinstance(websites, tuple):
            raise ValueError("The variable [websites] was None or was not a tuple.")

        http = urllib3.PoolManager()
        for website in websites:
            try:
                response = str(http.request('GET', website).data)
            except:
                print(f"Could not request [{str(website)}]")
                break

            if response:
                links = re.findall(r'(http://deviceids-medp.wdr.de/ondemand/\S+\.js)', response)
                [link_container.append(link) for link in links]

        return link_container

    @classmethod
    def get_content_from_calendar(cls, day, month, year):

        if not day or not month or not year:
            raise ValueError("Please specify a correct date")

        website = f'https://kinder.wdr.de/radio/kiraka/kalendertag-hoerspiele-100~_mon-{month}{year}_tag-{day}{month}{year}.html'
        http = urllib3.PoolManager()
        try:
            response = http.request('GET', website).data
            print(f'Requested website\t: [{website}]')
        except:
            response = None
            print(f"Could not request [{website}] please check if it is still available.")

        if response is not None:
            page_soup = Soup(response, "html.parser")
            containers = page_soup.find_all("div", {"class": "teaser"})
            contents = []
            if len(containers) != 0:
                for container in containers[:]:
                    if not container.h4.text == 'Diese Seite benötigt JavaScript. Bitte ändern Sie die Konfiguration Ihres Browsers.':
                        contents.append(container.h4.text.replace('Audio:', "").replace('\n', ""))
                        filename = f"Inhalt_vom_{day}-{month}-{year}.txt"
                        out_path = os.path.join(cls.download_path, filename)
                        with open(out_path, 'w+') as file:
                            for content in contents:
                                file.write(f'{content}\n')
                print(f"Saved content to {cls.download_path}")
            else:
                print(f"WARNING:\t\tNo content found.")


    @classmethod
    def get_file_by_link(cls, urls, download=False):
        """
        This function downloads all urls that are passed to it
        :param urls: PAss a downloadable file like x.mp3
        :param download:
        :return:
        """

        for url in urls:
            filename = re.search(r'\w+\.\w{2,3}$', url).group()
            out_path = os.path.join(cls.download_path, filename)
            if not os.path.exists(cls.download_path):
                os.mkdir(cls.download_path)

            if not os.path.exists(out_path):
                if download:
                    wget.download(url, out_path)
                    print(f"Downloading: File [{filename}] to [{out_path}].")
                    try:
                        date = re.search(r'((?P<day>\d{2})(?P<month>\d{2})(?P<year>\d{4}))', filename)
                        Downloader.get_content_from_calendar(date.group('day'), date.group('month'), date.group('year'))
                    except AttributeError:
                        pass
                else:
                    print(f"WHATIF-Downloading:\t [{url[0:30]}...] to [{out_path}] with filename [{filename}].")
            else:
                print(f'Skipped\t\t\t\t: [{url}] cause file [{out_path}] already exists.')

    @classmethod
    def parse_js_file(cls):
        link_container = []
        js_files = glob(os.path.join(cls.download_path, "*.js"))
        for js_file in js_files:
            with open(js_file,"r") as file:
                links = map(lambda url: "http:" + url, re.findall("//\S+?\.mp3", file.read()))
                [link_container.append(link) for link in links if not link_container.__contains__(link)]
        return link_container