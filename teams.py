# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http.request import Request
import json
import re

class OfficialSpider(CrawlSpider):
    name = 'official'
    start_urls = []

    def __init__(self, category=None):
        self.done = []
        self.done_server = []
        self.working_server = []
        self.servers = {}

    def start_requests(self):
        with open('games.json') as data_file:
            games = json.load(data_file)
            for game in games:
                yield Request(game['winner']['url'], self.parse)
                yield Request(game['loser']['url'], self.parse)

    def parse(self, response):
        players = []
        team = {}
        team['players'] = players

        team['id'] = response.url.split('/')[-1][:+4]

        if team['id'] in self.done:
            yield
        else:
            self.done.append(team['id'])

        team['name'] = re.sub('-', ' ', response.url.split('/')[-1][+5:])
        team['server'] = team['name'][:-2]

        composition = []

        for div in response.css('.ak-panel-content .ak-list-element .ak-content'):
            name = div.css('.ak-title a strong::text').extract_first()
            classe = div.css('.ak-text::text').extract_first()
            classe = classe[:-11]

            if classe not in composition:
                composition.append(classe)

            player = {}
            player['name'] = name
            player['classe'] = classe
            team['players'].append(player)

        team['composition'] = composition

        if team['server'] not in self.servers:
            server = {}
            server['name'] = team['server']
            server['teams'] = [team]
            self.servers[server['name']] = server
        else:
            self.servers[team['server']]['teams'].append(team)
            if len(self.servers[team['server']]['teams']) == 4:
                server = self.servers[team['server']]
                self.done_servers.append(team['server'])
                self.working_servers.remove(team['server'])
                del self.servers[team['server']]
                yield server
        print(len(self.servers))
