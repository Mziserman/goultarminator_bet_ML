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
        self.done_servers = []
        self.working_servers = []
        self.last_done_servers = []
        self.last_working_servers = []
        self.done_team = []
        self.servers = {}
        self.iterations = 0

    def start_requests(self):
        with open('games.json') as data_file:
            games = json.load(data_file)
            if self.iterations == 0:
                for game in games:
                    if game['winner']['name'][:-2] not in self.done_servers:
                        if game['winner']['name'] not in self.done_team:
                            yield Request(game['winner']['url'], self.parse)
                    if game['loser']['name'][:-2] not in self.done_servers:
                        if game['loser']['name'] not in self.done_team:
                            yield Request(game['loser']['url'], self.parse)
            else:
                for game in games:
                    if game['winner']['name'][:-2] not in self.done_servers and game['winner']['name'][:-2] in self.last_working_servers:
                        if game['winner']['name'] not in self.done_team:
                            yield Request(game['winner']['url'], self.parse)
                    if game['loser']['name'][:-2] not in self.done_servers and game['loser']['name'][:-2] in self.last_working_servers:
                        if game['loser']['name'] not in self.done_team:
                            yield Request(game['loser']['url'], self.parse)


        if len(self.last_working_servers) - len(self.working_servers) > 0:
            self.iterations += 1
            server = game['winner']['name'][:-2]

            self.last_working_servers = self.working_servers
            self.working_servers = []
            self.last_done_servers = self.done_servers
            self.done_servers = []

            self.start_requests()

        



    def parse(self, response):
        players = []
        team = {}
        team['players'] = players

        team['name'] = re.sub('-', ' ', response.url.split('/')[-1][+5:])
        if team['name'] not in self.done_team:
            self.done_team.append(team['name'])
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
            self.working_servers.append(server['name'])

        else:
            self.servers[team['server']]['teams'].append(team)

            if len(self.servers[team['server']]['teams']) == 4:
                server = self.servers[team['server']]

                self.done_servers.append(team['server'])
                self.working_servers.remove(team['server'])

                for team in self.servers[team['server']]['teams']:
                    self.done_team.remove(team['name'])

                del self.servers[team['server']]
                yield server

        print("Serveur livrés : {} {}".format(len(self.done_servers), self.done_servers))
        print("Serveur non livrés : {} {}".format(len(self.working_servers), self.working_servers))
        print("iteration n° {}".format(self.iterations))
        
