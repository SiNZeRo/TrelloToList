import argparse
import json
import os
import sys

import pandas as pd


def main(args):

    data = json.load(open(args['source_json']))

    item_ts = {}
    for action in data['actions']:
        act_data = action['data']
        if (act_data.get('checkItem')):
            item_ts[act_data['checkItem']['id']] = action['date']
        if (act_data.get('checklist')):
            item_ts[act_data['checklist']['id']] = action['date']
        if (act_data.get('card')):
            item_ts[act_data['card']['id']] = action['date']
    # print (item_ts)

    records = []
    for x in data['cards']:
        # print (x['dateLastActivity'], x['name'])
        card_date = item_ts[x['id']]
        for cid in x['idChecklists']:
            match_check_list = [
                c for c in data['checklists'] if c['id'] == cid][0]
            for item in match_check_list['checkItems']:
                item_date = item_ts.get(item['id'], card_date)
                records.append({
                    'date': item_date,
                    'progress': '\u2713' if item['state'] == 'complete' else ' ',
                    'item_name': item['name'],
                    'card_name': x['name'],
                    # 'id': item['id'],
                })
        if len(x['idChecklists']) == 0:
            if x['closed']:
                continue
            records.append({
                'date': card_date,
                'progress': ' ',
                'item_name': x['name'],
                'card_name': 'CARD',
                # 'id': x['id']
            })

    df = pd.DataFrame(records).sort_values(
        'date', ascending=False).set_index('date')
    if args.get('out') is None:
        args['out'] = args['source_json'] + ".csv"
    df.to_csv(args['out'], sep='|')


if __name__ == "__main__" and sys.argv[0].find('ipykernel_launcher.py') < 0:
    parser = argparse.ArgumentParser()
    parser.add_argument('source_json', help='path to json')
    parser.add_argument('--out', help='path to output csv')
    parser.add_argument('--echo', action='store_true', help='echo now')
    args = parser.parse_args()
    main(vars(args))
    if args.echo:
        os.system('cat %s | column -s\'|\' -t ' % args.out)
else:
    from collections import namedtuple
    args = {
        'source_json': '/home/tian/trello.json',
        'out': None,
    }
    main(args)
