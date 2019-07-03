import requests
import json
import os
import re
import html
import base64
from bs4 import BeautifulSoup
import argparse

parser = argparse.ArgumentParser(
    description='Get user targetprocess userstories'
)

parser.add_argument(
    '--url',
    default=os.environ.get('TP_URL')
)

parser.add_argument(
    '--user_email',
    default=os.environ.get('TP_USER_EMAIL')
)

parser.add_argument(
    '--user',
    default=os.environ.get('TP_USER_EMAIL')
)

parser.add_argument(
    '--password',
    default=os.environ.get('TP_USER_PASS')
)

parser.add_argument(
    '--base_dir',
    default='tp_stories'
)

args = parser.parse_args()

tp_url = args.url
base_dir = args.base_dir
user_email = args.user_email
user = args.user
user_pass = args.password

string_to_encode = user + ':' + user_pass
basic_auth = base64.b64encode(string_to_encode.encode()).decode('ascii')

headers = {
  'Content-Type': 'application/json;charset=UTF-8',
  'Authorization': 'Basic ' + basic_auth
}
params = {
  'take': 1000,
  'format': 'json'
}

resource = 'Users'
params['where'] = "Email eq '{0}'".format(user_email)
params['include'] = '[Id]'
Id = requests.get('https://' + tp_url + '/api/v1/' + resource, headers=headers, params=params).json()['Items'][0]['Id']

resource = 'UserStories'
params['where'] = 'AssignedUser.Id eq '+ str(Id)
params['include'] = '[Id, Name, Description, Comments, Attachments]'
request = requests.get('https://' + tp_url + '/api/v1/' + resource, headers=headers, params=params).json()
stories = request['Items']

params = {}
while 'Next' in request:
  request = requests.get(request['Next'], params=params, headers=headers).json()
  for item in request['Items']:
   stories.append(item)

if not os.path.isdir(base_dir):
  os.makedirs(base_dir)

for story in stories:
  story['Name'] = re.sub('/', '_', story['Name'])

  if not os.path.isfile(base_dir + '/' + str(story['Id']) + ' ' + story['Name'] + '.md'):
    print('Create file ' + story['Name'])
    f = open(base_dir + '/' + str(story['Id']) + ' ' + story['Name'] + '.md', 'a+')
    f.write('# ' + story['Name'])

    if story['Description'] is not None:
      story['Description'] = BeautifulSoup(story['Description'], features="html.parser").get_text('\n')
      f.write('\n\n## Description\n' + re.sub('\\n', '\n', story['Description']))

    if story['Attachments']['Items']:
      if not os.path.isdir(base_dir + '/attachments'):
        os.makedirs(base_dir + '/attachments')
      f.write('\n\n### Attachments\n')
      for at in story['Attachments']['Items']:
        params = {'AttachmentID': at['Id']}
        headers = {'Authorization': 'Basic ' + basic_auth}
        atta = requests.get('https://' + tp_url + '/Attachment.aspx', params=params, headers=headers, allow_redirects=True)
        open('tp_stories/attachments/' + str(story['Id']) + '_' + at['Name'], 'wb').write(atta.content)
        f.write('\nAttachment ' + at['Name'])

    if story['Comments']['Items']:
      f.write('\n\n### Comments\n')
      com_ids = [com['Id'] for com in story['Comments']['Items']]
      i = 1
      for com_id in sorted(com_ids, reverse=True):
        resource = 'Comments'
        params = {
          'where': 'Id eq '+ str(com_id),
          'include': '[Description,Owner]',
          'format': 'json',
          'take': 1000,
        }
        headers = {
          'Content-Type': 'application/json;charset=UTF-8',
          'Authorization': 'Basic ' + basic_auth
        }
        comment = requests.get('https://' + tp_url + '/api/v1/' + resource, headers=headers, params=params).json()['Items'][0]
        f.write('\n#### ' + str(i) + ' ' + comment['Owner']['FirstName'] + ' ' + comment['Owner']['LastName'] + '\n')
        comment['Description'] = BeautifulSoup(comment['Description'], features="html.parser").get_text('\n')
        f.write(re.sub('\\n', '\n', comment['Description']))
        f.write('\n\n')
        i += 1

    f.close()

    f=open('tp_stories/'+ str(story['Id']) + ' ' + story['Name'] + '.md', "r")
    inline_ats = re.findall(r'!\[(.*)\]\(https://' + tp_url + '/Attachment.aspx\?AttachmentID=([0-9]+)\)', f.read())
    for inline_at in inline_ats:
      params = {'AttachmentID': inline_at[1]}
      headers = {'Authorization': 'Basic ' + basic_auth}
      atta = requests.get('https://' + tp_url + '/Attachment.aspx', params=params, headers=headers, allow_redirects=True)
      open('tp_stories/attachments/' + str(story['Id']) + '_' + inline_at[1] + '_' + inline_at[0], 'wb').write(atta.content)
    f.close()
