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
    done = []

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

    	if team['id'] in done :
    		yield
    	else:
    		done.append(team['id'])

    	team['name'] = re.sub('-', ' ', response.url.split('/')[-1][+5:])

    	for div in response.css('.ak-panel-content .ak-list-element .ak-content'):
    		name = div.css('.ak-title a strong::text').extract_first()
    		classe = div.css('.ak-text::text').extract_first()
    		classe = classe[:-11]

    		player = {}
    		player['name'] = name
    		player['classe'] = classe
    		team['players'].append(player)
    		
    	yield team
