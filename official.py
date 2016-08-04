# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class OfficialSpider(CrawlSpider):
    name = 'official'
    start_urls = [
        'http://www.dofus.com/fr/mmorpg/communaute/tournois/goultarminator/calendrier?date=2016-08-01#jt_list/',
        'http://www.dofus.com/fr/mmorpg/communaute/tournois/goultarminator/calendrier?date=2016-08-03#jt_list/',
        'http://www.dofus.com/fr/mmorpg/communaute/tournois/goultarminator/calendrier?date=2016-08-04#jt_list/',
    ]

    def parse(self, response):
        for href in response.css('table.ak-ladder tr td:last-child a::attr(href)'):
            url_object = response.urljoin(self.make_url(href.extract()))

            yield scrapy.Request(url_object, callback=self.parse_combat_result_page)

    def parse_combat_result_page(self, response):
        teams = self.get_teams(response)

        yield {
            'id': self.get_id(response),
            'winner': teams['winner'],
            'loser': teams['loser'],
        }

    def get_teams(self, response):
        teams = {}
        winner_name = self.get_winner_name(response)


        for td in response.css('table.ak-ladder tbody tr td:first-child'):
            names = td.css('a::text').extract()
            urls = td.css('a::attr(href)').extract()
            
            winner = {}
            loser = {}
            for i in [0,1]:
                if names[i] == winner_name:
                    winner['name'] = names[i]
                    winner['url'] = self.make_url(urls[i])
                else:
                    loser['name'] = names[i]
                    loser['url'] = self.make_url(urls[i])

                teams['winner'] = winner
                teams['loser'] = loser
        return teams 

    def get_winner_name(self, response):
        return response.css('table.ak-ladder tbody tr td:last-child a::text').extract_first()

    def get_id(self, response):
        return response.url.split("/")[-1]

    def make_url(self, url):
        return 'http://www.dofus.com{}'.format(url)



