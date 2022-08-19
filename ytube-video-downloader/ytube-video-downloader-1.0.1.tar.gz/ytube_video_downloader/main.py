import os
import sys
from googleapiclient.discovery import build
import re
from datetime import datetime
import requests
import asyncio
import aiohttp
from fake_useragent import UserAgent


def compare_values(item_value: str, filter_value: str, filter_value_type: str) -> bool:
    if filter_value_type == 'datetime':
        item_value = datetime.strptime(re.findall('\d{4}-\d{2}-\d{2}', item_value)[0], '%Y-%m-%d')
        filter_values = re.findall(r'\d{4}/\d{2}/\d{2}', filter_value)
        if not bool(filter_values):
            print(f'Invalid input data ({filter_value})')
            sys.exit()
        filter_values = [datetime.strptime(value.strip(), '%Y/%m/%d') for value in filter_values]

    elif filter_value_type == 'int':
        item_value = int(item_value)
        filter_values = [int(value) for value in re.findall(r'\d+', filter_value)]

    else:
        print('Wrong parameter: filter_value_type in def compare_values()')
        sys.exit()

    if any(index == filter_value[0] for index in ['-', '+']):
        index = True if filter_value[0] == '+' else False

        if item_value >= filter_values[0]:
            return index
        else:
            return not index

    elif '-' in filter_value:
        if not filter_values[0] <= item_value <= filter_values[1]:
            return False
        else:
            return True

    else:
        print(f'Invalid input data! ({filter_value})')
        sys.exit()


def statistics_filter(item_set: dict, filter_set: dict) -> bool:
    for filter_key, filter_value in filter_set.items():
        try:
            if not compare_values(item_value=item_set[filter_key], filter_value=filter_value, filter_value_type='int'):
                return False
        except KeyError:
            return False

    return True


def snippet_filter(item_set: dict, filter_set: dict) -> bool:
    for filter_key, filter_value in filter_set.items():
        if filter_key == 'publishedAt':
            if not compare_values(item_value=item_set[filter_key], filter_value=filter_value,
                                  filter_value_type='datetime'):
                return False

        else:
            if not any(check_type in filter_value for check_type in ['any:', 'all:']):
                print(f'Invalid input data! ({filter_key})')
                sys.exit()

            functions = {
                'all': all,
                'any': any,
            }

            check_type = filter_value.split(':')[0].casefold().strip()
            filter_values = [value.casefold().strip() for value in filter_value.split(':')[1].split(',')]
            if filter_key == 'tags':
                item_values = [item_value.casefold().strip() for item_value in item_set[filter_key]]
            elif filter_key == 'title':
                item_values = item_set['title'].casefold()
            else:
                print('Wrong filter key in snippet filter')
                sys.exit()

            if not functions[check_type](value in item_values for value in filter_values):
                return False

    return True


def run() -> dict:
    filters = {
        'snippet': {
            'publishedAt': '',
            'tags': '',
            'title': ''
        },

        'statistics': {
            'viewCount': '',
            'likeCount': '',
            'commentCount': '',
        },
    }

    # Get input data
    channel_url = input('Channel url: ')
    for filter_category, filter_set in filters.items():
        for filter_name in filter_set:
            filters[filter_category][filter_name] = input(f'{filter_name}: ')

    # Delete empty keys
    for filter_category, filter_set in list(filters.items()):
        for filter_name, filter_value in list(filter_set.items()):
            if filter_value == '':
                del filters[filter_category][filter_name]

        if not bool(filters[filter_category]):
            del filters[filter_category]

    input_data = {'channel_url': channel_url, 'filters': filters}
    return input_data


def main() -> None:
    input_data = run()
    path = 'yt_videos'
    if not os.path.exists(path):
        os.makedirs(path)
    fake_user_agent = UserAgent()
    headers = {'user-agent': fake_user_agent.random}
    api_key = os.environ.get('YT_API_KEY')
    youtube = build(serviceName='youtube', version='v3', developerKey=api_key)
    filters = input_data['filters']

    response = requests.get(input_data['channel_url'], headers=headers)
    channel_id = re.findall(r'"externalId":".+","keywords"', response.text)[0].split('"')[3]

    # Get playlist ID that contains all videos
    request = youtube.channels().list(
        part='contentDetails',
        id=channel_id,
    )
    response = request.execute()
    uploads_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    # Get video IDs
    video_ids = []
    next_page_token = None
    while True:
        request = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=uploads_id,
            maxResults=50,
            pageToken=next_page_token,

        )
        response = request.execute()

        for item in response['items']:
            for key, value in item.items():
                if key == 'contentDetails':
                    video_ids.append(value['videoId'])

        if 'nextPageToken' not in response.keys():
            del next_page_token
            break

        next_page_token = response['nextPageToken']

    # Get info about videos
    items = []
    for i in range(0, len(video_ids), 50):
        request = youtube.videos().list(
            part=['snippet', 'statistics'],
            id=video_ids[i: i+50],
            maxResults=50
        )
        response = request.execute()

        items.extend(response['items'])

    # Get titles and urls of the filtered videos
    video_titles = []
    video_urls = []
    for item in items:
        for filter_category, filter_set in filters.items():
            if not globals()[f'{filter_category}_filter'](item_set=item[filter_category], filter_set=filter_set):
                break
        else:
            video_titles.append(item['snippet']['title'])
            video_urls.append(f"http://youtube.com/watch?v={item['id']}")

    # Get downloadable urls
    download_urls = []
    for video_title, video_url in zip(list(video_titles), video_urls):
        response = requests.post('https://ssyoutube.com/api/convert', json={'url': video_url})

        if response.status_code != 200:
            video_titles.remove(video_title)
            print(f"Can't download: {video_title}")
            continue

        tmp = ''
        for item in response.json()['url']:
            if item['type'] == 'mp4':
                if item['quality'] == '720':
                    download_urls.append(item['url'])
                    break
                elif item['quality'] == '360':
                    tmp = item['url']
        else:
            if bool(tmp):
                download_urls.append(tmp)
            else:
                video_titles.remove(video_title)
                print(f"Can't download: {video_title}")

    # Download videos
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(download_videos(video_titles, download_urls, path=path))


def get_tasks(session, download_urls: list) -> list:
    tasks = []
    for url in download_urls:
        tasks.append(session.get(url))
    return tasks


async def download_videos(video_titles: list, download_urls: list, path: str):
    async with aiohttp.ClientSession() as session:
        # Make requests
        tasks = get_tasks(session, download_urls)
        responses = await asyncio.gather(*tasks)

        # Save videos
        for video_title, response in zip(video_titles, responses):
            if response.status != 200:
                print(f"Can't download: {video_title}")
                continue

            video_title = re.sub(f'[?,/:"*|<>]', '_', video_title).replace(f'{chr(92)}', '_')
            with open(f'{path}/{video_title}.mp4', 'wb') as f:
                while True:
                    chunk = await response.content.read()
                    if not chunk:
                        break
                    f.write(chunk)

            print(fr'DOWNLOADED: {video_title}')


if __name__ == '__main__':
    main()
