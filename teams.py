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
        self.servers = {}
        self.done_teams = []

    def start_requests(self):
        with open('teams.json') as data_file:
            servers = json.load(data_file)
            for server in servers:
                print(server)
                for team in server['teams']:
                    self.done_teams.append(team['name'])
                # print(self.done_teams)

        with open('games.json') as data_file:
            games = json.load(data_file)
            for game in games:
                print(game['winner']['name'])
                print(game['winner']['name'])
                print(game['winner']['name'])
                print(game['winner']['name'])
                print(game['winner']['name'])
                print(game['winner']['name'])
                print(game['winner']['name'])
                print(self.done_teams)
                if game['winner']['name'].lower() not in self.done_teams:
                    yield Request(game['winner']['url'], self.parse)
                if game['loser']['name'].lower() not in self.done_teams:
                    yield Request(game['loser']['url'], self.parse)

    def parse(self, response):
        servers = self.create_servers(response)
        yield servers
        
    def create_servers(self, response):
        team = {}

        team['name'] = re.sub('-', ' ', response.url.split('/')[-1][+5:])
        team['server'] = team['name'][:-2]

        self.get_players_and_composition(response, team)
        
        if team['server'] not in self.servers:
            self.create_server(team)

        else:
            return self.append_team(team)

    def create_server(self, team):
        server = {
            'name': team['server'],
            'teams': [
                team
            ]
        }
        self.servers[server['name']] = server

    def append_team(self, team):
        server_teams = self.servers[team['server']]['teams']
        if team not in server_teams:
            server_teams.append(team)

        if len(server_teams) == 4:
            return self.return_server(team)

    def return_server(self, team):
        server = self.servers[team['server']]
        for team in server['teams']:
            self.done_teams.append(team['name'])
        del self.servers[team['server']]
        for team in server['teams']:
            self.done_teams.append(team['name'])
        return server

    def get_players_and_composition(self, response, team):
        team['composition'] = []
        team['players'] = []
        for div in response.css('.ak-panel-content .ak-list-element .ak-content'):
            name = div.css('.ak-title a strong::text').extract_first()
            classe = div.css('.ak-text::text').extract_first()[:-11]

            if classe not in team['composition']:
                team['composition'].append(classe)

            player = {}
            player['name'] = name
            player['classe'] = classe
            team['players'].append(player)

        return team

