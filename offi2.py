# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

class OfficialSpider(CrawlSpider):
    name = 'official'
    start_urls = ['http://www.dofus.com/fr/mmorpg/communaute/tournois/goultarminator/calendrier?date=2016-08-01#jt_list/']

    def parse(self, response):
        i = 0
        for href in response.css('table.ak-ladder tr td:last-child a::attr(href)'):
            i = i + 1
            print(i)
            full_url = 'http://www.dofus.com{}'.format(href.extract())
            url_object = response.urljoin(full_url)

            yield scrapy.Request(url_object, callback=self.parse_combat_result_page)

    def parse_combat_result_page(self, response):
        winner = ItemLoader(item=Team(), response=response)
        loser = ItemLoader(item=Team(), response=response)

        match = ItemLoader(item=Match(), response=response)

        teams_names = self.get_teams_names(response)
        teams_links = self.get_teams_links(response)
        winner_name = self.get_winner_name(response)
        loser_name = self.get_loser_name(teams_names, winner_name)

    def get_teams_names(self, response):
        return list(team.extract() for team in response.css('table.ak-ladder tbody tr td:first-child a::text'))

    def get_teams_links(self, response):
        return list(team.extract() for team in response.css('table.ak-ladder tbody tr td:first-child a::attr(href)'))


    def get_winner_name(self, response):
        return response.css('table.ak-ladder tbody tr td:last-child a::text').extract_first()

    def get_loser_name(self, teams, winner):
        if teams[0] == winner:
            return teams[1]
        return teams[0]

    def get_id(self, response):
        return response.url.split("/")[-1]