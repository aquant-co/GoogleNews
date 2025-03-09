import logging
import re
from urllib.parse import quote
from urllib.request import Request, urlopen

import dateparser
from bs4 import BeautifulSoup
from dateutil.parser import parse

from .models import Result


class GoogleNews:
    __slots__ = (
        "_lang",
        "_user_agent",

        "_search_key",
        "_topic",
        "_topic_section",

        "_period",
        "_start",
        "_end",

        "_results",
        "_total_count",

        "_exception"
    )

    _lang: str
    _user_agent: str

    _search_key: str | None
    _topic: str | None
    _topic_section: str | None

    _period: str | None
    _start: str | None
    _end: str | None

    _results: list[Result]
    _total_count: int

    _exception: bool

    def __init__(
        self,
        lang: str = "en",
        period: str = "",
        start: str = "",
        end: str = "",
    ):
        self._lang = lang
        self._user_agent = "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:64.0) Gecko/20100101 Firefox/64.0"

        self._search_key = None
        self._topic = None
        self._topic_section = None

        self._period = period
        self._start = start
        self._end = end

        self._results = []
        self._total_count = 0

        self._exception = False

    @property
    def _headers(self):
        headers = {"User-Agent": self._user_agent}

        if "-" in self._lang:
            lang, region = self._lang.split("-")
            headers["Accept-Language"] = f"{lang}-{region},{lang};q=0.9"

        return headers

    def get_version(self):
        from importlib.metadata import version
        return version("GoogleNews")

    def set_user_agent(self, user_agent: str):
        self._user_agent = user_agent

    def enable_exception(self, enable: bool = True):
        self._exception = enable

    def set_lang(self, lang: str):
        self._lang = lang

    def set_period(self, period: str):
        self._period = period

    def set_time_range(self, start: str, end: str):
        self._start = start
        self._end = end

    def set_topic(self, topic: str):
        self._topic = topic

    def set_topic_section(self, topic_section: str):
        self._topic_section = topic_section

    def search(self, search_key: str):
        """
        Searches for a term in google.com in the news section and retrieves the first page into __results.
        Parameters:
        key = the search term
        """
        self._search_key = quote(search_key)
        self.get_page()

    def remove_after_last_fullstop(self, s: str):
        # Find the last occurrence of the full stop
        last_period_index = s.rfind('.')
        # Slice the string up to the last full stop
        return s[:last_period_index+1] if last_period_index != -1 else s

    def page_at(self, page: int = 1):
        """
        Retrieves a specific page from google.com in the news sections into __results.
        Parameter:
        page = number of the page to be retrieved
        """
        results: list[Result] = []
        try:
            if self._start != "" and self._end != "":
                url = "https://www.google.com/search?q={}&lr=lang_{}&biw=1920&bih=976&source=lnt&&tbs=lr:lang_1{},cdr:1,cd_min:{},cd_max:{},sbd:1&tbm=nws&start={}".format(self._search_key,self._lang,self._lang,self._start,self._end,(10 * (page - 1)))
            elif self._period != "":
                url = "https://www.google.com/search?q={}&lr=lang_{}&biw=1920&bih=976&source=lnt&&tbs=lr:lang_1{},qdr:{},,sbd:1&tbm=nws&start={}".format(self._search_key,self._lang,self._lang,self._period,(10 * (page - 1)))
            else:
                url = "https://www.google.com/search?q={}&lr=lang_{}&biw=1920&bih=976&source=lnt&&tbs=lr:lang_1{},sbd:1&tbm=nws&start={}".format(self._search_key,self._lang,self._lang,(10 * (page - 1)))
        except AttributeError as error:
            raise AttributeError("You need to run a search() before using get_page().") from error

        try:
            result = self._build_response(url)
            for item in result:
                title = ""
                title_el = item.find("h3")
                if title_el:
                    title = title_el.get_text().replace("\n", "")

                try:
                    link = item.get("href").replace('/url?esrc=s&q=&rct=j&sa=U&url=','')
                except Exception:
                    link = ''
                try:
                    media = item.find('div').find('div').find('div').find_next_sibling('div').text
                except Exception:
                    media = ''
                try:
                    tmp_date = item.find('div').find_next_sibling('div').find('span').text
                except Exception:
                    tmp_date = ''
                try:
                    desc = self.remove_after_last_fullstop(item.find('div').find_next_sibling('div').find('div').find_next_sibling('div').find('div').find('div').find('div').text).replace('\n','')
                except Exception:
                    desc = ''
                try:
                    img = item.find("img").get("src")
                except Exception:
                    img = ''

                results.append({
                    'title': title,
                    'media': media,
                    'date': tmp_date.strip(),
                    'datetime': dateparser.parse(tmp_date),
                    'desc': desc,
                    'link': link,
                    'img': img
                })
        except Exception as e_parser:
            print(e_parser)
            if self._exception:
                raise

        return results

    def get_page(self, page: int = 1):
        """
        Retrieves a specific page from google.com in the news sections into __results.
        Parameter:
        page = number of the page to be retrieved
        """
        try:
            if self._start != "" and self._end != "":
                url = "https://www.google.com/search?q={}&lr=lang_{}&biw=1920&bih=976&source=lnt&&tbs=lr:lang_1{},cdr:1,cd_min:{},cd_max:{},sbd:1&tbm=nws&start={}".format(self._search_key,self._lang,self._lang,self._start,self._end,(10 * (page - 1)))
            elif self._period != "":
                url = "https://www.google.com/search?q={}&lr=lang_{}&biw=1920&bih=976&source=lnt&&tbs=lr:lang_1{},qdr:{},,sbd:1&tbm=nws&start={}".format(self._search_key,self._lang,self._lang,self._period,(10 * (page - 1)))
            else:
                url = "https://www.google.com/search?q={}&lr=lang_{}&biw=1920&bih=976&source=lnt&&tbs=lr:lang_1{},sbd:1&tbm=nws&start={}".format(self._search_key,self._lang,self._lang,(10 * (page - 1)))
        except AttributeError as error:
            raise AttributeError("You need to run a search() before using get_page().") from error

        try:
            result = self._build_response(url)
            for item in result:
                try:
                    text = item.find("h3").text.replace("\n","")
                except Exception:
                    text = ''
                try:
                    link = item.get("href").replace('/url?esrc=s&q=&rct=j&sa=U&url=','')
                except Exception:
                    link = ''
                try:
                    media = item.find('div').find('div').find('div').find_next_sibling('div').text
                except Exception:
                    media = ''
                try:
                    tmp_date = item.find('div').find_next_sibling('div').find('span').text
                except Exception:
                    tmp_date = ''
                try:
                    desc = self.remove_after_last_fullstop(item.find('div').find_next_sibling('div').find('div').find_next_sibling('div').find('div').find('div').find('div').text).replace('\n','')
                except Exception:
                    desc = ''
                try:
                    tmp_img = item.find("img").get("src")
                except Exception:
                    tmp_img = ''

                self._results.append({
                    'title': text,
                    'media': media,
                    'date': tmp_date.strip(),
                    'datetime': dateparser.parse(tmp_date),
                    'desc': desc,
                    'link': link,
                    'img': tmp_img
                })
        except Exception as e_parser:
            print(e_parser)
            if self._exception:
                raise

    def get_news(self, key: str = "", deamplify: bool = False):
        if self._period != "":
            key += f"when:{self._period}"

        key = quote(key)

        if self._start and self._end:
            start = f'{self._start[-4:]}-{self._start[:2]}-{self._start[3:5]}'
            end = f'{self._end[-4:]}-{self._end[:2]}-{self._end[3:5]}'

            url = f"https://news.google.com/search?q={key}+before:{end}+after:{start}&hl={self._lang}"
        else:
            url = f"https://news.google.com/search?q={key}&hl={self._lang}"

        if self._topic:
            url = f"https://news.google.com/topics/{self._topic}"

            if self._topic_section:
                url += f"/sections/{self._topic_section}"

        try:
            request = Request(url, headers=self._headers)
            with urlopen(request) as response:
                page = response.read()

            soup = BeautifulSoup(page, "html.parser")
            articles = soup.select('article')
            for article in articles:
                try:
                    # title
                    try:
                        title=article.findAll('div')[2].findAll('a')[0].text
                    except:
                        try:
                            title=article.findAll('a')[1].text
                        except:
                            title=None
                    # description
                    try:
                        desc=None
                    except:
                        desc=None
                    # date
                    try:
                        date = article.find("time").text
                        # date,datetime_tmp = lexial_date_parser(date)
                    except:
                        date = None
                    # datetime
                    try:
                        datetime_chars=article.find('time').get('datetime')
                        datetime_obj = parse(datetime_chars).replace(tzinfo=None)
                    except:
                        datetime_obj=None
                    # link
                    if deamplify:
                        try:
                            link = 'https://news.google.com/' + article.find('div').find("a").get("href")[2:]
                        except Exception as deamp_e:
                            print(deamp_e)
                            link = article.find("article").get("jslog").split('2:')[1].split(';')[0]
                    else:
                        try:
                            link = 'https://news.google.com/' + article.find('div').find("a").get("href")[2:]
                        except Exception as deamp_e:
                            print(deamp_e)
                            link = None
                    if link.startswith('https://www.youtube.com/watch?v='):
                        desc = 'video'
                    # image
                    try:
                        img = 'https://news.google.com'+article.find("figure").find("img").get("src")
                    except:
                        img = None
                    # site
                    try:
                        site=article.find("time").parent.find("a").text
                    except:
                        site=None
                    try:
                        media=article.find("div").findAll("div")[1].find("div").find("div").find("div").text
                    except:
                        try:
                            media=article.findAll("div")[1].find("div").find("div").find("div").text
                        except:
                            media=None
                    # reporter
                    try:
                        reporter = article.findAll('span')[2].text
                    except:
                        reporter = None
                    # collection
                    self._results.append({'title':title,
                                        'desc':desc,
                                        'date':date,
                                        'datetime': dateparser.parse(date),
                                        'link':link,
                                        'img':img,
                                        'media':media,
                                        'site':site,
                                        'reporter':reporter})
                except Exception as e_article:
                    print(e_article)
        except Exception as e_parser:
            print(e_parser)
            if self._exception:
                raise

    def total_count(self):
        return self._total_count

    def results(self, sort: bool = False):
        """
        Returns the __results.
        New feature: include datatime and sort the articles in decreasing order
        """

        if sort:
            self._results.sort(key=lambda r: r["datetime"], reverse=True)

        return self._results

    def get_texts(self):
        """ Returns only the __texts of the __results. """

        return [result["title"] for result in self._results]

    def get_links(self):
        """ Returns only the __links of the __results. """

        return [result["link"] for result in self._results]

    def clear(self):
        self._results = []
        self._total_count = 0

    def _build_response(self, url: str):
        request = Request(
            url.replace("search?", f"search?hl={self._lang}&gl={self._lang}&"),
            headers=self._headers
        )
        with urlopen(request) as response:
            page = response.read()

        soup = BeautifulSoup(page, "html.parser")
        stats = soup.find_all("div", id="result-stats")
        if stats:
            stats = re.search(r"[\d,]+", stats[0].text)
            self._total_count = int(stats.group(0).replace(',', '') if stats else 0)
        else:
            #TODO might want to add output for user to know no data was found
            self._total_count = 0
            logging.debug('Total count is not available when sort by date')

        result = soup.find_all("a", attrs={'data-ved': True})
        return result
