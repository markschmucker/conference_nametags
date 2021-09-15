from client506 import create_client
import csv

# The 2021 registration spreadsheet is:
# https://docs.google.com/spreadsheets/d/1rBMSjqOZT2H0pxkwAdTB1dkpZ_Gv1v8YyL7WFRH8aYs/edit#gid=0

# Paste the first five columns of the registration spreadsheet here, after resolving any missing
# cells in a temporary spreadsheet.

# =IF(AND(C2 <> "M", K2 = 1), "error", "ok")
# =IF(AND(C2 = "M", LEN(J2) <10), "error", "ok")

# Be sure to write input.csv as plain *.csv from Excel, not UTF-8 or unicode

gg_users = []
fieldnames = ['email', 'name', 'member', 'city', 'state']
with open('input.csv', mode='r') as f:
    reader = csv.DictReader(f, fieldnames=fieldnames, delimiter=',')
    for row in reader:
        gg_users.append(row)

# Try to find each member in the forum and update the registration info with their
# forum details. They might be a spouse or using a different email; in that case
# just use the info available in the registration sheet.
client = create_client(1)
users = []
for gg_user in gg_users:
    email = gg_user['email']
    forum_user = None
    if gg_user['member'].lower() == 'm':
        forum_user = client.get_username_by_email(email)
    if forum_user:
        username = forum_user['username']
        details = client.user_details(username)
        summary = client.user_summary(username)
        forum_user.update({'details': details})
        forum_user.update({'summary': summary})
        forum_user.update(gg_user)
        users.append(forum_user)
    else:
        print "can't find user ", email
        users.append(gg_user)
    # Faster debugging:
    # if len(users) > 5:
    #     break


def has_badge(user, badge_name):
    try:
        for badge in user['details']['user']['badges']:
            if badge['name'] == badge_name:
                return 1
    except KeyError:
        print 'not a forum user, so does not have badge'
    return 0


def is_patreon(user):
    try:
        for group in user['details']['user']['groups']:
            if group['name'] in ('Patreon', 'Patreons'):
                return 1
    except KeyError:
        print 'not a forum user, so not a patreon'
    return 0


def likes_received(user):
    try:
        return user['summary']['user_summary']['likes_received']
    except KeyError:
        print 'not a forum user, so no likes received'
    return 0


# Update each user with badges and other info from the forum
badge_names = ['Staff', 'Area Leader', 'Blogger', 'Liaison', 'CrowdDD Reviewer']
for u in users:
    for badge in badge_names:
        u[badge] = has_badge(u, badge)
    u['patreon'] = is_patreon(u)
    u['likes_received'] = likes_received(u)


fields = ['email', 'name', 'member', 'city', 'state', 'title', 'created_at', 'post_count', 'likes_received',
          'avatar_template', 'patreon']
fields += badge_names
lines = []
for u in users:
    line = [str(u.get(key, '')) for key in fields]
    lines.append(line)

with file('conference_cards.csv', 'wb') as f:
    writer = csv.writer(f)
    writer.writerow(fields)
    for line in lines:
        if line:
            writer.writerow(line)
