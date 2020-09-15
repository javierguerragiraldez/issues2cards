'''
Documentation, License etc.

@package issues2cards
'''

import argparse
from datetime import datetime, timedelta, timezone
import dateutil.parser
from github import Github
import requests
import sys
import yaml


def readfile(path: str) -> str:
	with open(path, 'r') as f:
		data = f.read()
	return data


def getconf():
	parser = argparse.ArgumentParser(description="Update Trello board from Github issues.")
# 	parser.add_argument(
# 		'-r', '--repo', action='append', dest='repo', default=[],
# 		help="Github repository to check for new issues.")
	parser.add_argument(
		'-c', '--conf', action='store', dest='conf',
		help="Configuration file.")
# 	parser.add_argument(
# 		'-t', '--gh-token', action='store', dest='gh_token',
# 		help="Github access token.")
# 	parser.add_argument(
# 		'--trello-apikey', action='store', dest='trello_apikey',
# 		help="Trello API key.")
# 	parser.add_argument(
# 		'--trello-apitoken', action='store', dest='trello_apitoken',
# 		help="Trello API Token.")
# 	parser.add_argument(
# 		'-d', '--horizon-days', action='store', dest='horizon_days',
# 		help="Max number of days since last modified an issue to be included.")

	args = parser.parse_args()
	conf = {}
	if args.conf:
		with open(args.conf, 'r') as conffile:
			conf = yaml.safe_load(conffile)

	conf.update({
		'gh-token': readfile('.github_token').strip(),
		'trello-api': {
			'key': readfile('.trello_apikey').strip(),
			'token': readfile('.trello_apitoken').strip(),
		},
	})

# 	conf = {
# 		'gh-token': args.gh_token or conf['gh-token'],
# 		'repos': conf.get('repos', []) + (args.repo),
# 		'horizon_days': args.horizon_days or conf['horizon_days'],
# 		'tr-apikey': args.trello_apikey or conf.get('trello-api', {}).get('key', None),
# 		'tr-apitoken': args.trello_apitoken or conf.get('trello-api', {}).get('token', None),
# 	}
	return conf


def addIssueCard(issue, list_id, conf):
	res = requests.post('https://api.trello.com/1/cards', params={
		'name': f"#{issue.number}: {issue.title}",
		'idList': list_id,

		'key': conf['trello-api']['key'],
		'token': conf['trello-api']['token'],
	})
	card_1 = res.json()

	card_id = card_1['id']
	res = requests.post(f'https://api.trello.com/1/cards/{card_id}/attachments', params={
		'url': issue.html_url,

		'key': conf['trello-api']['key'],
		'token': conf['trello-api']['token'],
	})
	return card_id


conf = getconf()
print("..args:", conf)

g = Github(conf['gh-token'])

print("----- github -----")

user = g.get_user()
print(f"user: {user.name}")

repo = g.get_repo('Kong/kong')
print(f"repo name: {repo.name}")

# labels = repo.get_labels()
# print(f"labels: {labels}")
# sys.stdout.flush()

issues = repo.get_issues(state='open')
print(f"open issues: {issues.totalCount}")
sys.stdout.flush()

if 'horizon_days' in conf:
	horizon = datetime.now() - timedelta(days=conf['horizon_days'])
	recent_issues = [i for i in issues if i.updated_at >= horizon]

else:
	recent_issues = list(issues)

print(f"recent issues: {len(recent_issues)}")
sys.stdout.flush()

no_label_issues = [i for i in recent_issues if not i.labels]
print(f"no-label issues: {len(no_label_issues)}")
sys.stdout.flush()

# boards = requests.get(
# 	'https://api.trello.com/1/members/me/boards',
# 	params={
# 		'fields': 'name,url',
#
# 		'key': conf['trello-api']['key'],
# 		'token': conf['trello-api']['token'],
# 	})
#
# print(f"boards: {boards}: {boards.json()}")

print("----- trello -----")

board_id = conf['board']['id']
list_ids = conf['board']['lists']

cards = requests.get(
	f'https://api.trello.com/1/boards/{board_id}/cards',
	params={
		'attachments': 'true',
		'attachment_fields': 'url',
		'fields': 'dateLastActivity,idList,url',

		'key': conf['trello-api']['key'],
		'token': conf['trello-api']['token'],
	}).json()
print(f"cards: {len(cards)}")
sys.stdout.flush()

cards_by_attachment = {a['url']: c for c in cards for a in c.get('attachments', [])}
print(f"different attachements: {len(cards_by_attachment)}")
sys.stdout.flush()

print("----- crossing -----")

new_issues = [i for i in recent_issues if i.html_url not in cards_by_attachment]
print(f"new issues: {len(new_issues)}")
sys.stdout.flush()

new_activity = []
for i in recent_issues:
	c = cards_by_attachment.get(i.html_url, None)
	if c and c['idList'] == list_ids['waiting']:
		i_updated = i.updated_at.replace(tzinfo=timezone.utc)
		c_updated = dateutil.parser.isoparse(c['dateLastActivity'])
		if i_updated > c_updated:
			new_activity.append((i, c))

print(f"new activity in {len(new_activity)} issues")

# for i in new_issues:
# 	addIssueCard(i, list_ids['new-issues], conf)

# for i, c in new_activity:
# 	moveCard(c, list_ids['activity'])
