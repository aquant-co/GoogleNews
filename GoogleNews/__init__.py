### MODULES
import copy
import datetime
import logging
import re
from urllib.parse import quote
from urllib.request import Request, urlopen

import dateparser
from bs4 import BeautifulSoup, ResultSet
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta


### METHODS

def lexical_date_parser(date_to_check: str | None):
    if date_to_check=='':
        return ('',None)
    datetime_tmp=None
    date_tmp=copy.copy(date_to_check)
    try:
        date_tmp = date_tmp[date_tmp.rfind('..')+2:]
        datetime_tmp=dateparser.parse(date_tmp)
    except:
        date_tmp = None
        datetime_tmp = None

    if datetime_tmp==None:
        date_tmp=date_to_check
    else:
        datetime_tmp=datetime_tmp.replace(tzinfo=None)

    if date_tmp[0]==' ':
        date_tmp=date_tmp[1:]
    return date_tmp,datetime_tmp


def define_date(date: str):
    months = {'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Sept':9,'Oct':10,'Nov':11,'Dec':12, '01':1, '02':2, '03':3, '04':4, '05':5, '06':6, '07':7, '08':8, '09':9, '10':10, '11':11, '12':12}
    try:
        if ' ago' in date.lower():
            q = int(date.split()[-3])
            if 'minutes' in date.lower() or 'mins' in date.lower():
                return datetime.datetime.now() + relativedelta(minutes=-q)
            elif 'hour' in date.lower():
                return datetime.datetime.now() + relativedelta(hours=-q)
            elif 'day' in date.lower():
                return datetime.datetime.now() + relativedelta(days=-q)
            elif 'week' in date.lower():
                return datetime.datetime.now() + relativedelta(days=-7*q)
            elif 'month' in date.lower():
                return datetime.datetime.now() + relativedelta(months=-q)
        elif 'yesterday' in date.lower():
            return datetime.datetime.now() + relativedelta(days=-1)
        else:
            date_list = date.replace('/',' ').split(' ')
            if len(date_list) == 2:
                date_list.append(datetime.datetime.now().year)
            elif len(date_list) == 3:
                if date_list[0] == '':
                    date_list[0] = '1'
            return datetime.datetime(day=int(date_list[0]), month=months[date_list[1]], year=int(date_list[2]))
    except:
        return float('nan')


### CLASSEs

class GoogleNews:

    def __init__(
        self,
        lang: str = "en",
        period: str = "",
        start: str = "",
        end: str = "",
        region: str | None = None
    ):
        self.__results = []
        self.__totalcount = 0
        self.user_agent = 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:64.0) Gecko/20100101 Firefox/64.0'
        self.__lang = lang

        self.headers = {"User-Agent": self.user_agent}
        if region:
            self.headers["Accept-Language"] = f"{lang}-{region},{lang};q=0.9"

        self.__period = period
        self.__start = start
        self.__end = end
        self.__exception = False
        self.__version = '1.6.15'
        self.__topic = None
        self.__section = None

    def getVersion(self):
        return self.__version

    def enableException(self, enable: bool = True):
        self.__exception = enable

    def set_lang(self, lang: str):
        self.__lang = lang

    def set_period(self, period: str):
        self.__period = period

    def set_time_range(self, start: str, end: str):
        self.__start = start
        self.__end = end

    def set_topic(self, topic: str):
        self.__topic = topic

    def set_section(self, section: str):
        self.__section = section

    def search(self, key: str):
        """
        Searches for a term in google.com in the news section and retrieves the first page into __results.
        Parameters:
        key = the search term
        """
        self.__key = quote(key)
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
        results = []
        try:
            if self.__start != "" and self.__end != "":
                self.url = "https://www.google.com/search?q={}&lr=lang_{}&biw=1920&bih=976&source=lnt&&tbs=lr:lang_1{},cdr:1,cd_min:{},cd_max:{},sbd:1&tbm=nws&start={}".format(self.__key,self.__lang,self.__lang,self.__start,self.__end,(10 * (page - 1)))
            elif self.__period != "":
                self.url = "https://www.google.com/search?q={}&lr=lang_{}&biw=1920&bih=976&source=lnt&&tbs=lr:lang_1{},qdr:{},,sbd:1&tbm=nws&start={}".format(self.__key,self.__lang,self.__lang,self.__period,(10 * (page - 1)))
            else:
                self.url = "https://www.google.com/search?q={}&lr=lang_{}&biw=1920&bih=976&source=lnt&&tbs=lr:lang_1{},sbd:1&tbm=nws&start={}".format(self.__key,self.__lang,self.__lang,(10 * (page - 1)))
        except AttributeError as error:
            raise AttributeError("You need to run a search() before using get_page().") from error

        try:
            result = self._build_response()
            for item in result:
                try:
                    tmp_text = item.find("h3").text.replace("\n","")
                except Exception:
                    tmp_text = ''
                try:
                    tmp_link = item.get("href").replace('/url?esrc=s&q=&rct=j&sa=U&url=','')
                except Exception:
                    tmp_link = ''
                try:
                    tmp_media = item.find('div').find('div').find('div').find_next_sibling('div').text
                except Exception:
                    tmp_media = ''
                try:
                    tmp_date = item.find('div').find_next_sibling('div').find('span').text
                    tmp_date,tmp_datetime=lexical_date_parser(tmp_date)
                except Exception:
                    tmp_date = ''
                    tmp_datetime=None
                try:
                    tmp_desc = self.remove_after_last_fullstop(item.find('div').find_next_sibling('div').find('div').find_next_sibling('div').find('div').find('div').find('div').text).replace('\n','')
                except Exception:
                    tmp_desc = ''
                try:
                    tmp_img = item.find("img").get("src")
                except Exception:
                    tmp_img = ''
                results.append({'title': tmp_text, 'media': tmp_media,'date': tmp_date,'datetime':define_date(tmp_date),'desc': tmp_desc, 'link': tmp_link,'img': tmp_img})
        except Exception as e_parser:
            print(e_parser)
            if self.__exception:
                raise Exception(e_parser)
            else:
                pass
        return results

    def get_page(self, page: int = 1):
        """
        Retrieves a specific page from google.com in the news sections into __results.
        Parameter:
        page = number of the page to be retrieved
        """
        try:
            if self.__start != "" and self.__end != "":
                self.url = "https://www.google.com/search?q={}&lr=lang_{}&biw=1920&bih=976&source=lnt&&tbs=lr:lang_1{},cdr:1,cd_min:{},cd_max:{},sbd:1&tbm=nws&start={}".format(self.__key,self.__lang,self.__lang,self.__start,self.__end,(10 * (page - 1)))
            elif self.__period != "":
                self.url = "https://www.google.com/search?q={}&lr=lang_{}&biw=1920&bih=976&source=lnt&&tbs=lr:lang_1{},qdr:{},,sbd:1&tbm=nws&start={}".format(self.__key,self.__lang,self.__lang,self.__period,(10 * (page - 1)))
            else:
                self.url = "https://www.google.com/search?q={}&lr=lang_{}&biw=1920&bih=976&source=lnt&&tbs=lr:lang_1{},sbd:1&tbm=nws&start={}".format(self.__key,self.__lang,self.__lang,(10 * (page - 1)))
        except AttributeError:
            raise AttributeError("You need to run a search() before using get_page().")
        try:
            result = self._build_response()
            for item in result:
                try:
                    tmp_text = item.find("h3").text.replace("\n","")
                except Exception:
                    tmp_text = ''
                try:
                    tmp_link = item.get("href").replace('/url?esrc=s&q=&rct=j&sa=U&url=','')
                except Exception:
                    tmp_link = ''
                try:
                    tmp_media = item.find('div').find('div').find('div').find_next_sibling('div').text
                except Exception:
                    tmp_media = ''
                try:
                    tmp_date = item.find('div').find_next_sibling('div').find('span').text
                    tmp_date,tmp_datetime=lexical_date_parser(tmp_date)
                except Exception:
                    tmp_date = ''
                    tmp_datetime=None
                try:
                    tmp_desc = self.remove_after_last_fullstop(item.find('div').find_next_sibling('div').find('div').find_next_sibling('div').find('div').find('div').find('div').text).replace('\n','')
                except Exception:
                    tmp_desc = ''
                try:
                    tmp_img = item.find("img").get("src")
                except Exception:
                    tmp_img = ''
                self.__results.append({'title': tmp_text, 'media': tmp_media,'date': tmp_date,'datetime':define_date(tmp_date),'desc': tmp_desc, 'link': tmp_link,'img': tmp_img})
        except Exception as e_parser:
            print(e_parser)
            if self.__exception:
                raise Exception(e_parser)
            else:
                pass

    def get_news(self, key: str = "", deamplify: bool = False):
        if key != '':
            if self.__period != "":
                key += f" when:{self.__period}"
        else:
            if self.__period != "":
                key += f"when:{self.__period}"
        key = quote(key)
        start = f'{self.__start[-4:]}-{self.__start[:2]}-{self.__start[3:5]}'
        end = f'{self.__end[-4:]}-{self.__end[:2]}-{self.__end[3:5]}'

        if self.__start == '' or self.__end == '':
            self.url = 'https://news.google.com/search?q={}&hl={}'.format(
                key, self.__lang.lower())
        else:
            self.url = 'https://news.google.com/search?q={}+before:{}+after:{}&hl={}'.format(
                key, end, start, self.__lang.lower())

        if self.__topic:
            self.url = 'https://news.google.com/topics/{}'.format(
                self.__topic)

            if self.__section:
                self.url = 'https://news.google.com/topics/{}/sections/{}'.format(
                self.__topic, self.__section)


        try:
            request = Request(self.url, headers=self.headers)
            with urlopen(request) as response:
                page = response.read()

            self.content = BeautifulSoup(page, "html.parser")
            articles = self.content.select('article')
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
                    self.__results.append({'title':title,
                                        'desc':desc,
                                        'date':date,
                                        'datetime':define_date(date),
                                        'link':link,
                                        'img':img,
                                        'media':media,
                                        'site':site,
                                        'reporter':reporter})
                except Exception as e_article:
                    print(e_article)
        except Exception as e_parser:
            print(e_parser)
            if self.__exception:
                raise Exception(e_parser)
            else:
                pass

    def total_count(self):
        return self.__totalcount

    def results(self, sort: bool = False):
        """Returns the __results.
        New feature: include datatime and sort the articles in decreasing order"""
        results=self.__results
        if sort:
            try:
                results.sort(key = lambda x:x['datetime'],reverse=True)
            except Exception as e_sort:
                print(e_sort)
                if self.__exception:
                    raise Exception(e_sort)
                else:
                    pass
                results=self.__results
        return results

    def get_texts(self):
        """ Returns only the __texts of the __results. """

        return [result["title"] for result in self.__results]

    def get_links(self):
        """ Returns only the __links of the __results. """

        return [result["link"] for result in self.__results]

    def clear(self):
        self.__results = []
        self.__totalcount = 0

    def _build_response(self):
        request = Request(
            self.url.replace("search?", f"search?hl={self.__lang}&gl={self.__lang}&"),
            headers=self.headers
        )
        with urlopen(request) as response:
            page = response.read()

        self.content = BeautifulSoup(page, "html.parser")
        stats = self.content.find_all("div", id="result-stats")
        if stats and isinstance(stats, ResultSet):
            stats = re.search(r'[\d,]+', stats[0].text)
            self.__totalcount = int(stats.group().replace(',', ''))
        else:
            #TODO might want to add output for user to know no data was found
            self.__totalcount = None
            logging.debug('Total count is not available when sort by date')

        result = self.content.find_all("a", attrs={'data-ved': True})
        return result
