from datetime import datetime
import re
import requests

from pony.orm import db_session, ObjectNotFound
from bs4 import BeautifulSoup
from dateutil import parser

from ..libs.logging import logger
from ..libs.utils import exception
from ..libs.constants import (
    CHANGELOG_URL,
    UPDATE_KEYWORDS,
    DELIMITER,
    DATE_SPLITTER,
    MONTHS
)
from ..core.models.patchnotes import Patchnotes


def process_specific_language(language: str):
    logger.info(f"Processing language: <{language}>")
    result = requests.get(
        CHANGELOG_URL,
        cookies={'Steam_Language': language}
    )
    if result.status_code != 200:
        logger.warning(
            'Patch logs page responded with unexpected ' +
            f'status code: {result.status_code}'
        )

    soup = BeautifulSoup(
        result.text,
        features='html.parser'
    )
    patch_logs = soup.find_all(
        'div',
        class_='workshopAnnouncement'
    )
    lang_specific_patch_notes = process_parsed_content(patch_logs, language)
    logger.info("Finished processing patch notes")
    return lang_specific_patch_notes


def process_parsed_content(patch_logs: list, language: str):
    current_date = datetime.utcnow()
    patch_notes = {}
    year = current_date.year
    for i, patch_log in enumerate(patch_logs):
        date_lines = patch_log.div.get_text().strip().replace(
            UPDATE_KEYWORDS[language], ''
        ).split(DELIMITER[language])
        date_lines = [line.strip() for line in date_lines]
        if ',' in date_lines[0]:
            date, year = date_lines[0].split(', ')
            date_lines[0] = date
        if '.' in date_lines[0]:
            date, year = date_lines[0].split('. ')
            date_lines[0] = date
        if '年' in date_lines[0]:
            year, date = date_lines[0].split('年')
            date_lines[0] = date

        month_descriptor, day = date_lines[0].split(DATE_SPLITTER[language])
        if language == 'schinese':
            day = re.findall(r'\d+', day)[0]
            month_descriptor = re.findall(r'\d+', month_descriptor)[0]
            if '下午' in date_lines[1]:
                date_lines[1] = date_lines[1][2:] + 'pm'
            if '上午' in date_lines[1]:
                date_lines[1] = date_lines[1][2:] + 'am'
        if language == 'russian':
            month_descriptor, day = day, month_descriptor
        patch_time = parser.parse(date_lines[1])
        content_line = patch_log.p.get_text(separator="\n").strip()

        date = datetime(
            year=int(year),
            month=MONTHS[language][month_descriptor],
            day=int(day),
            hour=patch_time.hour,
            minute=patch_time.minute,
            tzinfo=None
        )

        patch_notes[str(date)] = [date, content_line]

    return patch_notes


@exception(logger)
def process_patch_notes():
    patch_notes = {}
    for lang in ('english', 'russian', 'schinese'):
        patch_notes[lang] = process_specific_language(lang)
    with db_session:
        for i, val in enumerate(patch_notes['english'].items()):
            date_str, content = val
            russian_loc = (
                patch_notes['russian'][date_str][1] if (
                    date_str in patch_notes['russian']
                ) else None
            )
            chinese_loc = (
                patch_notes['schinese'][date_str][1] if (
                    date_str in patch_notes['schinese']
                ) else None
            )
            record = Patchnotes.get(date=content[0])
            if record:
                record.content_english = content[1]
                record.content_russian = russian_loc
                record.content_chinese = chinese_loc
                continue

            try:
                record = Patchnotes[i]
                record.date = content[0]
                record.content_english = content[1]
            except ObjectNotFound:
                record = Patchnotes(
                    date=content[0],
                    content_english=content[1],
                )
                record.content_russian = russian_loc
                record.content_chinese = chinese_loc
