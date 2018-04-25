from lxml import html, etree
from time import sleep
import requests

class dl_pub_puller(object):

    def __init__(self, venue, year):
        self.venue = venue
        self.year = year
        self.titles = []
        self.deep_titles = []
        self.abstracts = []
        self.deep_abstracts = []

        self.deep_title_idxs = []
        self.deep_abstract_idxs = []

        self.abstract_keywords = ['convolutional', 'cnn', 'convnet', \
            'neural network', 'deep learning', 'rnn', 'gan', \
            'recurrent neural', 'generative adversarial', \
            'autoencoder']
        self.title_keywords = self.abstract_keywords + ['deep', 'neural']

        if venue == "isbi":
            for day in range(1,5): # ISBI is a 4 day event
                url = "https://embs.papercept.net/conferences/conferences/"+\
                    "ISBI" + str(year)[2:] + "/program/ISBI" + str(year)[2:] +\
                    "_ContentListWeb_" + str(day) + ".html"

                page = requests.get(url)
                tree = html.fromstring(page.content)
                self.titles += \
                    tree.xpath('//span[contains(@class, "pTtl")]//a/text()')
                _abstracts = \
                    tree.xpath('//strong[contains(text(), "Abstract")]')
                for _abstracti in _abstracts:
                    self.abstracts.append(etree.tostring(_abstracti))


        elif venue == "spie":
            spie_year_vol = {2014:9033, 2015:9412, 2016:9783, 2017:10132}
            spie_year_id = {2014:2021635, 2015:2057561, 2016:2190950,\
                            2017:2235224}

            for voli in range(9): # SPIE has 9 volumes
                url = "http://spie.org/Publications/Proceedings/Volume/"+\
                    str(spie_year_vol[year]+voli) +\
                    "?&origin_id=x4318&event_id=" + str(spie_year_id[year])

                page = requests.get(url)
                tree = html.fromstring(page.content)

                self.titles += \
                    tree.xpath('//div[contains(@class, "volumePaper")]'+\
                        '//a[contains(@class, "strong")]/text()')
                self.abstracts += \
                    tree.xpath('//div[contains(@class, "volumePaper")]'+\
                        '//div[contains(@class, "theabstract")]/text()')


        elif venue == "miccai":
            ## The following method is faster, but can be used if
            ## searching for titles only
            # miccai_year_num = {2014:[9783319104034,9783319104690,9783319104423],\
            #     2015:[9783319245522,9783319245706,9783319245737],\
            #     2016:[9783319467191,9783319467221,9783319467252]}
            #
            # for parti in range(3): # MICCAI has 3 parts
            #     url = "http://www.springer.com/us/book/" +\
            #         str(miccai_year_num[year][parti])
            #
            #     page = requests.get(url)
            #     tree = html.fromstring(page.content)
            #
            #     self.titles += \
            #         tree.xpath('//div[contains(@class, "main")]//'+\
            #             'p[contains(@class, "title")]/text()')

            ## Springer server where MICCAI proceedings are hosted
            # does not allow multiple HTTP requests at the same time.
            # Therefore it needs to wait from time to time
            miccai_vols = {2014:[['978-3-319-10404-1_',[1,100]],\
                                 ['978-3-319-10470-6_',[1,100]],\
                                 ['978-3-319-10443-0_',[1,53]]],\
                           2015:[['978-3-319-24553-9_',[1,88]],\
                                 ['978-3-319-24571-3_',[1,84]],\
                                 ['978-3-319-24574-4_',[1,91]]],\
                           2016:[['978-3-319-46720-7_',[1,77]],\
                                 ['978-3-319-46723-8_',[1,79]],\
                                 ['978-3-319-46726-9_',[1,72]]],\
                           2017:[['978-3-319-66182-7_',[1,90]],\
                                 ['978-3-319-66185-8_',[1,86]],\
                                 ['978-3-319-66179-7_',[1,79]]]}

            for parti in miccai_vols[year]:
                for chapi in range(parti[1][0],parti[1][1]+1):
                    url = "https://link.springer.com/chapter/10.1007/" +\
                        parti[0] + str(chapi)

                    page = requests.get(url)
                    tree = html.fromstring(page.content)

                    self.titles += \
                        tree.xpath('//title/text()')

                    self.abstracts += \
                        tree.xpath('//section[contains(@class, "Abstract")]'+\
                            '/p[contains(@class, "Para")]/text()')

                    # increase waiting interval when getting max-retrieve-exceed
                    sleep(1)

        self.get_deep_elements(self.titles, self.deep_titles, \
            self.title_keywords, self.deep_title_idxs)
        self.get_deep_elements(self.abstracts, self.deep_abstracts,\
            self.abstract_keywords, self.deep_abstract_idxs)


    def get_deep_elements(self, elements, deep_elements, keywords, idxs):
        for counter, _elementi in enumerate(elements):
            elementi = _elementi.lower()
            if not isinstance(elementi, str):
                elementi = elementi.decode('utf-8')
            for keywordi in keywords:
                if keywordi in elementi:
                    deep_elements.append(elementi)
                    idxs.append(counter)
                    break


def collect_data(venue_name, years):
    venue = []
    for year in years:
        venue.append(dl_pub_puller(venue_name, year))
    return venue


def summary_print(venue_name, venue_classes, years):
    print(venue_name)
    print('year\t #papers\t #DL-papers-by-title\t #DL-percentage-by-title'+\
        '\t' + '#DL-papers-by-abstract\t #DL-percentage-by-abstract')
    #
    abstracts_all = open('abstracts_all.txt', 'w')
    abstracts_dl = open('abstracts_dl.txt', 'w')
    ##
    for counter, venue in enumerate(venue_classes):
        for item in venue.abstracts:
            abstracts_all.write('%s\n' % item)
        for item in venue.deep_abstracts:
            abstracts_dl.write('%s\n' % item)

        print(years[counter], '\t', len(venue.titles), '\t', len(venue.deep_titles),\
            '\t', len(venue.deep_titles)/len(venue.titles), '\t',\
            len(venue.deep_abstracts), '\t',\
            len(venue.deep_abstracts)/len(venue.titles))


if __name__ == "__main__":
    # isbi = collect_data('isbi', list(range(2014,2017+1)))
    # summary_print('isbi', isbi, list(range(2014,2017+1)))

    # spie = collect_data('spie', list(range(2014,2017+1)))
    # summary_print('spie', spie, list(range(2014,2017+1)))

    # miccai = collect_data('miccai', list(range(2014,2016+1)))
    # summary_print('miccai', miccai, list(range(2014,2016+1)))
    miccai = collect_data('miccai', list(range(2017,2017+1)))
    summary_print('miccai', miccai, list(range(2017,2017+1)))
