import json
import re
import time
from datetime import datetime

import pandas as pd
import requests

from provider.constants import HEADERS, JSON_PATTERN


class Scanner:
    def __init__(self):
        self.headers: dict[str, str] = HEADERS
        self.base_api_url: str = 'https://www.youtube.com/channel/{channel_id}'

    def custom_request(
            self,
            channel_id: str,
            sleep_time: int = 5,
            timeout: int = 5,
            max_attempt_cnt: int = 10,
    ):
        for attempt in range(max_attempt_cnt):
            try:
                response = requests.get(
                    url=self.base_api_url.format(channel_id=channel_id),
                    headers=self.headers,
                    verify=True,
                    timeout=timeout,
                )
                return response.text
            except requests.exceptions.RequestException as e:
                print(f"Attempt {attempt + 1}: Request failed, retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
        return f"Failed to get data after {max_attempt_cnt} attempts."


class Extractor:
    @staticmethod
    def get_json(text: str):
        match = JSON_PATTERN.search(text, re.DOTALL)
        if match:
            return json.loads(match.group('jsonData'))

    @staticmethod
    def extract_channel_info(data: dict):
        channel_name = data['header']['c4TabbedHeaderRenderer']['title']
        channel_description = data['header']['c4TabbedHeaderRenderer']['tagline']['channelTaglineRenderer']['content']
        tabs = data['contents']['twoColumnBrowseResultsRenderer']['tabs'][0]['tabRenderer']['content'][
            'sectionListRenderer']['contents']

        video_titles = []
        for tab in tabs:
            try:
                items = tab['itemSectionRenderer']['contents'][0]['shelfRenderer']['content'][
                    'horizontalListRenderer']['items']
                video_titles.extend(
                    [
                        item['gridVideoRenderer']['title']['simpleText']
                        for item in items
                    ]
                )
            except KeyError:
                continue

        # TODO: оставлю разделитель здесь если захочу данные пересобрать иначе, чтоб понимать где делить
        video_clips_tittles = "---".join(video_titles)
        return channel_name, channel_description, video_clips_tittles


def extract_data(
        target_channels: str,
        train_mode: bool,
        output_file_name: str = 'result.csv',
) -> pd.DataFrame | None:
    res = []
    scanner = Scanner()
    extractor = Extractor()

    for index, row in pd.read_excel(target_channels).iterrows():
        channel_id = row['url'].split('/')[-1]
        try:
            data = extractor.get_json(scanner.custom_request(channel_id))
            if data:
                channel_name, channel_description, video_clips_tittles = extractor.extract_channel_info(data)
                res.append({
                    "название_канала": channel_name,
                    "ссылка_на_канал": row['url'],
                    "описание_канала": channel_description,
                    "Названия_видео_роликов": video_clips_tittles,
                })

                if train_mode:
                    # так как метод универсальный для обучения и инференса
                    res[-1]["метка_класса"] = row['topic']

                print(f"Parsed: {channel_name}")
            else:
                print(f"Failed to get data from: {channel_id=}")
        except Exception as e:
            print(f"Can't parse {channel_id=}: {e}")
            continue

    df_output = pd.DataFrame(res)
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    if train_mode:
        df_output.to_csv(
            f"{output_file_name}_{current_time}.csv",
            sep='|',
            index=False,
            encoding='utf-8',
        )
    else:
        return df_output


if __name__ == '__main__':
    extract_data(
        target_channels='yt_topics_10_500.xlsx',
        output_file_name='result.csv',
        train_mode=True,
    )
