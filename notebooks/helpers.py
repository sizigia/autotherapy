import json
import os
import pickle
import re
import unicodedata as ud
from datetime import datetime

import cv2
import emoji
import numpy as numpy
import pymongo
import pytesseract
from dotenv import load_dotenv


def extract_hashtags(text, account):
    """
    Arguments:


    Returns:
        string of terms
        number of unique hashtags found
    """
    list_ = re.findall('(?<=#)\w+', text)
    set_ = set([e.lower() for e in list_ if (e.lower() != account)])
    str_ = ' '.join(set_)

    return str_, len(set_)


def restore_spaced_title(text):
    """

    """

    text = text.replace('\n', ' ')

    spaced_titles = re.findall('(([A-Z]\s+){2,}[A-Z])', text)
    titles = {title[0]: title[0].replace(' ', '') for title in spaced_titles}

    for k in titles.keys():
        text = text.replace(k, titles[k])

    return text


def extract_text(text_path):
    """

    """

    with open(text_path, 'r') as file:
        str_ = ''.join(file.readlines())
        return str_


def extract_from_json(json_file):
    """
    json_file : path to json file
    """

    _json = json.load(open(json_file, 'r'))['node']

    vals = {}

    vals['account'] = _json['owner']['username']
    vals['post_id'] = _json['shortcode']
    vals['likes'] = _json['edge_media_preview_like']['count']
    vals['comments'] = _json['edge_media_to_comment']['count']
    vals['date'] = datetime.fromtimestamp(_json['taken_at_timestamp'])

    return vals


def account_info(json_file):
    """

    """

    _json = json.load(open(json_file, 'r'))['node']

    ownerkeys_ = ['biography', 'business_category_name', 'category_enum', 'connected_fb_page',
                  'edge_follow', 'edge_followed_by', 'external_url', 'full_name', 'has_channel',
                  'has_guides', 'is_business_account', 'is_joined_recently',
                  'is_private', 'is_verified', 'overall_category_name']

    vals = {}

    vals['account'] = _json['owner']['username']

    for key in ownerkeys_:
        if key in ['edge_follow', 'edge_followed_by']:
            vals[key] = _json['owner'][key]['count']
        else:
            vals[key] = _json['owner'][key]

    return vals


def extract_text_from_image(img_path):
    """

    """

    kernel = np.ones((5, 5), np.uint8)

    img = cv2.imread(img_path)
    morph = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY, kernel)
    d = pytesseract.image_to_data(morph, output_type=Output.DICT)

    return ' '.join([w for w in d['text'] if len(w)]).strip()


def extract_mentions(text):
    """

    """

    r_ = '@([\w_.]+[\w_])'

    mentions_list = re.findall(r_, text.lower())
    unique_mentions = set(mentions_list)
    mentions = ' '.join(unique_mentions)

    return mentions


def extract_url(text):
    """

    """

    str_urls = ''
    r_ = '[^\s(){}]+\.com(?:/[a-zA-Z0-9\-_]+)*'

    prep_text = re.sub('(https?://)', ' ', text.replace('•',
                                                        ' ').replace('...', ' ')).lower()

    urls_ = re.findall(r_, prep_text)
    str_urls = ' '.join(urls_)

    return str_urls


def remove_hashtags_mentions_urls(text):
    """

    """
    r_ = ['(@[\w_.]+[\w_])', '(#\w+)', '[^\s(){}]+\.com(?:/[a-zA-Z0-9\-_]+)*']

    prep_text = re.sub('(https?://)', ' ', text.replace('...', ' '))

    for r in r_:
        prep_text = re.sub(r, ' ', prep_text)

    return prep_text


def extract_emoji_terms(text):
    """

    """

    emoji_list = emoji.emoji_lis(text)
    unique_terms = set([emoji.demojize(e['emoji']).replace(
        ':', '').replace('_', ' ') for e in emoji_list])
    str_terms = ' '.join(unique_terms)

    return str_terms


def convert_special_char_to_normal(text):
    target = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G',
              'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '!', '?', '.', ',', '"', "'"]
    special_list = {
        'serifBold': ['𝐚', '𝐛', '𝐜', '𝐝', '𝐞', '𝐟', '𝐠', '𝐡', '𝐢', '𝐣', '𝐤', '𝐥', '𝐦', '𝐧', '𝐨', '𝐩', '𝐪', '𝐫', '𝐬', '𝐭', '𝐮', '𝐯', '𝐰', '𝐱', '𝐲', '𝐳', '𝐀', '𝐁', '𝐂', '𝐃', '𝐄', '𝐅', '𝐆', '𝐇', '𝐈', '𝐉', '𝐊', '𝐋', '𝐌', '𝐍', '𝐎', '𝐏', '𝐐', '𝐑', '𝐒', '𝐓', '𝐔', '𝐕', '𝐖', '𝐗', '𝐘', '𝐙', '𝟎', '𝟏', '𝟐', '𝟑', '𝟒', '𝟓', '𝟔', '𝟕', '𝟖', '𝟗', '❗', '❓', '.', ',', '"', "'"],
        'serifItalic': ['𝑎', '𝑏', '𝑐', '𝑑', '𝑒', '𝑓', '𝑔', 'ℎ', '𝑖', '𝑗', '𝑘', '𝑙', '𝑚', '𝑛', '𝑜', '𝑝', '𝑞', '𝑟', '𝑠', '𝑡', '𝑢', '𝑣', '𝑤', '𝑥', '𝑦', '𝑧', '𝐴', '𝐵', '𝐶', '𝐷', '𝐸', '𝐹', '𝐺', '𝐻', '𝐼', '𝐽', '𝐾', '𝐿', '𝑀', '𝑁', '𝑂', '𝑃', '𝑄', '𝑅', '𝑆', '𝑇', '𝑈', '𝑉', '𝑊', '𝑋', '𝑌', '𝑍', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '!', '?', '.', ',', '"', "'"],
        'serifBoldItalic': ['𝒂', '𝒃', '𝒄', '𝒅', '𝒆', '𝒇', '𝒈', '𝒉', '𝒊', '𝒋', '𝒌', '𝒍', '𝒎', '𝒏', '𝒐', '𝒑', '𝒒', '𝒓', '𝒔', '𝒕', '𝒖', '𝒗', '𝒘', '𝒙', '𝒚', '𝒛', '𝑨', '𝑩', '𝑪', '𝑫', '𝑬', '𝑭', '𝑮', '𝑯', '𝑰', '𝑱', '𝑲', '𝑳', '𝑴', '𝑵', '𝑶', '𝑷', '𝑸', '𝑹', '𝑺', '𝑻', '𝑼', '𝑽', '𝑾', '𝑿', '𝒀', '𝒁', '𝟎', '𝟏', '𝟐', '𝟑', '𝟒', '𝟓', '𝟔', '𝟕', '𝟖', '𝟗', '❗', '❓', '.', ',', '"', "'"],
        'sans': ['𝖺', '𝖻', '𝖼', '𝖽', '𝖾', '𝖿', '𝗀', '𝗁', '𝗂', '𝗃', '𝗄', '𝗅', '𝗆', '𝗇', '𝗈', '𝗉', '𝗊', '𝗋', '𝗌', '𝗍', '𝗎', '𝗏', '𝗐', '𝗑', '𝗒', '𝗓', '𝖠', '𝖡', '𝖢', '𝖣', '𝖤', '𝖥', '𝖦', '𝖧', '𝖨', '𝖩', '𝖪', '𝖫', '𝖬', '𝖭', '𝖮', '𝖯', '𝖰', '𝖱', '𝖲', '𝖳', '𝖴', '𝖵', '𝖶', '𝖷', '𝖸', '𝖹', '𝟢', '𝟣', '𝟤', '𝟥', '𝟦', '𝟧', '𝟨', '𝟩', '𝟪', '𝟫', '!', '?', '.', ',', '"', "'"],
        'sansBold': ['𝗮', '𝗯', '𝗰', '𝗱', '𝗲', '𝗳', '𝗴', '𝗵', '𝗶', '𝗷', '𝗸', '𝗹', '𝗺', '𝗻', '𝗼', '𝗽', '𝗾', '𝗿', '𝘀', '𝘁', '𝘂', '𝘃', '𝘄', '𝘅', '𝘆', '𝘇', '𝗔', '𝗕', '𝗖', '𝗗', '𝗘', '𝗙', '𝗚', '𝗛', '𝗜', '𝗝', '𝗞', '𝗟', '𝗠', '𝗡', '𝗢', '𝗣', '𝗤', '𝗥', '𝗦', '𝗧', '𝗨', '𝗩', '𝗪', '𝗫', '𝗬', '𝗭', '𝟬', '𝟭', '𝟮', '𝟯', '𝟰', '𝟱', '𝟲', '𝟳', '𝟴', '𝟵', '❗', '❓', '.', ',', '"', "'"],
        'sansItalic': ['𝘢', '𝘣', '𝘤', '𝘥', '𝘦', '𝘧', '𝘨', '𝘩', '𝘪', '𝘫', '𝘬', '𝘭', '𝘮', '𝘯', '𝘰', '𝘱', '𝘲', '𝘳', '𝘴', '𝘵', '𝘶', '𝘷', '𝘸', '𝘹', '𝘺', '𝘻', '𝘈', '𝘉', '𝘊', '𝘋', '𝘌', '𝘍', '𝘎', '𝘏', '𝘐', '𝘑', '𝘒', '𝘓', '𝘔', '𝘕', '𝘖', '𝘗', '𝘘', '𝘙', '𝘚', '𝘛', '𝘜', '𝘝', '𝘞', '𝘟', '𝘠', '𝘡', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '!', '?', '.', ',', '"', "'"],
        'sansBoldItalic': ['𝙖', '𝙗', '𝙘', '𝙙', '𝙚', '𝙛', '𝙜', '𝙝', '𝙞', '𝙟', '𝙠', '𝙡', '𝙢', '𝙣', '𝙤', '𝙥', '𝙦', '𝙧', '𝙨', '𝙩', '𝙪', '𝙫', '𝙬', '𝙭', '𝙮', '𝙯', '𝘼', '𝘽', '𝘾', '𝘿', '𝙀', '𝙁', '𝙂', '𝙃', '𝙄', '𝙅', '𝙆', '𝙇', '𝙈', '𝙉', '𝙊', '𝙋', '𝙌', '𝙍', '𝙎', '𝙏', '𝙐', '𝙑', '𝙒', '𝙓', '𝙔', '𝙕', '𝟎', '𝟏', '𝟐', '𝟑', '𝟒', '𝟓', '𝟔', '𝟕', '𝟖', '𝟗', '❗', '❓', '.', ',', '"', "'"],
        'script': ['𝒶', '𝒷', '𝒸', '𝒹', 'ℯ', '𝒻', 'ℊ', '𝒽', '𝒾', '𝒿', '𝓀', '𝓁', '𝓂', '𝓃', 'ℴ', '𝓅', '𝓆', '𝓇', '𝓈', '𝓉', '𝓊', '𝓋', '𝓌', '𝓍', '𝓎', '𝓏', '𝒜', 'ℬ', '𝒞', '𝒟', 'ℰ', 'ℱ', '𝒢', 'ℋ', 'ℐ', '𝒥', '𝒦', 'ℒ', 'ℳ', '𝒩', '𝒪', '𝒫', '𝒬', 'ℛ', '𝒮', '𝒯', '𝒰', '𝒱', '𝒲', '𝒳', '𝒴', '𝒵', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '!', '?', '.', ',', '"', "'"],
        'scriptBold': ['𝓪', '𝓫', '𝓬', '𝓭', '𝓮', '𝓯', '𝓰', '𝓱', '𝓲', '𝓳', '𝓴', '𝓵', '𝓶', '𝓷', '𝓸', '𝓹', '𝓺', '𝓻', '𝓼', '𝓽', '𝓾', '𝓿', '𝔀', '𝔁', '𝔂', '𝔃', '𝓐', '𝓑', '𝓒', '𝓓', '𝓔', '𝓕', '𝓖', '𝓗', '𝓘', '𝓙', '𝓚', '𝓛', '𝓜', '𝓝', '𝓞', '𝓟', '𝓠', '𝓡', '𝓢', '𝓣', '𝓤', '𝓥', '𝓦', '𝓧', '𝓨', '𝓩', '𝟎', '𝟏', '𝟐', '𝟑', '𝟒', '𝟓', '𝟔', '𝟕', '𝟖', '𝟗', '❗', '❓', '.', ',', '"', "'"],
        'fraktur': ['𝔞', '𝔟', '𝔠', '𝔡', '𝔢', '𝔣', '𝔤', '𝔥', '𝔦', '𝔧', '𝔨', '𝔩', '𝔪', '𝔫', '𝔬', '𝔭', '𝔮', '𝔯', '𝔰', '𝔱', '𝔲', '𝔳', '𝔴', '𝔵', '𝔶', '𝔷', '𝔄', '𝔅', 'ℭ', '𝔇', '𝔈', '𝔉', '𝔊', 'ℌ', 'ℑ', '𝔍', '𝔎', '𝔏', '𝔐', '𝔑', '𝔒', '𝔓', '𝔔', 'ℜ', '𝔖', '𝔗', '𝔘', '𝔙', '𝔚', '𝔛', '𝔜', 'ℨ', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '!', '?', '.', ',', '"', "'"],
        'frakturBold': ['𝖆', '𝖇', '𝖈', '𝖉', '𝖊', '𝖋', '𝖌', '𝖍', '𝖎', '𝖏', '𝖐', '𝖑', '𝖒', '𝖓', '𝖔', '𝖕', '𝖖', '𝖗', '𝖘', '𝖙', '𝖚', '𝖛', '𝖜', '𝖝', '𝖞', '𝖟', '𝕬', '𝕭', '𝕮', '𝕯', '𝕰', '𝕱', '𝕲', '𝕳', '𝕴', '𝕵', '𝕶', '𝕷', '𝕸', '𝕹', '𝕺', '𝕻', '𝕼', '𝕽', '𝕾', '𝕿', '𝖀', '𝖁', '𝖂', '𝖃', '𝖄', '𝖅', '𝟎', '𝟏', '𝟐', '𝟑', '𝟒', '𝟓', '𝟔', '𝟕', '𝟖', '𝟗', '❗', '❓', '.', ',', '"', "'"],
        'monospace': ['𝚊', '𝚋', '𝚌', '𝚍', '𝚎', '𝚏', '𝚐', '𝚑', '𝚒', '𝚓', '𝚔', '𝚕', '𝚖', '𝚗', '𝚘', '𝚙', '𝚚', '𝚛', '𝚜', '𝚝', '𝚞', '𝚟', '𝚠', '𝚡', '𝚢', '𝚣', '𝙰', '𝙱', '𝙲', '𝙳', '𝙴', '𝙵', '𝙶', '𝙷', '𝙸', '𝙹', '𝙺', '𝙻', '𝙼', '𝙽', '𝙾', '𝙿', '𝚀', '𝚁', '𝚂', '𝚃', '𝚄', '𝚅', '𝚆', '𝚇', '𝚈', '𝚉', '𝟶', '𝟷', '𝟸', '𝟹', '𝟺', '𝟻', '𝟼', '𝟽', '𝟾', '𝟿', '！', '？', '．', '，', '"', '＇'],
        'fullwidth': ['ａ', 'ｂ', 'ｃ', 'ｄ', 'ｅ', 'ｆ', 'ｇ', 'ｈ', 'ｉ', 'ｊ', 'ｋ', 'ｌ', 'ｍ', 'ｎ', 'ｏ', 'ｐ', 'ｑ', 'ｒ', 'ｓ', 'ｔ', 'ｕ', 'ｖ', 'ｗ', 'ｘ', 'ｙ', 'ｚ', 'Ａ', 'Ｂ', 'Ｃ', 'Ｄ', 'Ｅ', 'Ｆ', 'Ｇ', 'Ｈ', 'Ｉ', 'Ｊ', 'Ｋ', 'Ｌ', 'Ｍ', 'Ｎ', 'Ｏ', 'Ｐ', 'Ｑ', 'Ｒ', 'Ｓ', 'Ｔ', 'Ｕ', 'Ｖ', 'Ｗ', 'Ｘ', 'Ｙ', 'Ｚ', '０', '１', '２', '３', '４', '５', '６', '７', '８', '９', '！', '？', '．', '，', '"', '＇'],
        'doublestruck': ['𝕒', '𝕓', '𝕔', '𝕕', '𝕖', '𝕗', '𝕘', '𝕙', '𝕚', '𝕛', '𝕜', '𝕝', '𝕞', '𝕟', '𝕠', '𝕡', '𝕢', '𝕣', '𝕤', '𝕥', '𝕦', '𝕧', '𝕨', '𝕩', '𝕪', '𝕫', '𝔸', '𝔹', 'ℂ', '𝔻', '𝔼', '𝔽', '𝔾', 'ℍ', '𝕀', '𝕁', '𝕂', '𝕃', '𝕄', 'ℕ', '𝕆', 'ℙ', 'ℚ', 'ℝ', '𝕊', '𝕋', '𝕌', '𝕍', '𝕎', '𝕏', '𝕐', 'ℤ', '𝟘', '𝟙', '𝟚', '𝟛', '𝟜', '𝟝', '𝟞', '𝟟', '𝟠', '𝟡', '❕', '❔', '.', ',', '"', "'"],
        'capitalized': ['ᴀ', 'ʙ', 'ᴄ', 'ᴅ', 'ᴇ', 'ꜰ', 'ɢ', 'ʜ', 'ɪ', 'ᴊ', 'ᴋ', 'ʟ', 'ᴍ', 'ɴ', 'ᴏ', 'ᴘ', 'q', 'ʀ', 'ꜱ', 'ᴛ', 'ᴜ', 'ᴠ', 'ᴡ', 'x', 'ʏ', 'ᴢ', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '﹗', '﹖', '﹒', '﹐', '"', "'"],
        'circled': ['ⓐ', 'ⓑ', 'ⓒ', 'ⓓ', 'ⓔ', 'ⓕ', 'ⓖ', 'ⓗ', 'ⓘ', 'ⓙ', 'ⓚ', 'ⓛ', 'ⓜ', 'ⓝ', 'ⓞ', 'ⓟ', 'ⓠ', 'ⓡ', 'ⓢ', 'ⓣ', 'ⓤ', 'ⓥ', 'ⓦ', 'ⓧ', 'ⓨ', 'ⓩ', 'Ⓐ', 'Ⓑ', 'Ⓒ', 'Ⓓ', 'Ⓔ', 'Ⓕ', 'Ⓖ', 'Ⓗ', 'Ⓘ', 'Ⓙ', 'Ⓚ', 'Ⓛ', 'Ⓜ', 'Ⓝ', 'Ⓞ', 'Ⓟ', 'Ⓠ', 'Ⓡ', 'Ⓢ', 'Ⓣ', 'Ⓤ', 'Ⓥ', 'Ⓦ', 'Ⓧ', 'Ⓨ', 'Ⓩ', '⓪', '①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧', '⑨', '!', '?', '.', ',', '"', "'"],
        'parenthesized': ['⒜', '⒝', '⒞', '⒟', '⒠', '⒡', '⒢', '⒣', '⒤', '⒥', '⒦', '⒧', '⒨', '⒩', '⒪', '⒫', '⒬', '⒭', '⒮', '⒯', '⒰', '⒱', '⒲', '⒳', '⒴', '⒵', '🄐', '🄑', '🄒', '🄓', '🄔', '🄕', '🄖', '🄗', '🄘', '🄙', '🄚', '🄛', '🄜', '🄝', '🄞', '🄟', '🄠', '🄡', '🄢', '🄣', '🄤', '🄥', '🄦', '🄧', '🄨', '🄩', '⓿', '⑴', '⑵', '⑶', '⑷', '⑸', '⑹', '⑺', '⑻', '⑼', '!', '?', '.', ',', '"', "'"],
        'underlinedSingle': ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '!', '?', '.', ',', '"', "'"],
        'underlinedDouble': ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '!', '?', '.', ',', '"', "'"],
        'strikethroughSingle': ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '!', '?', '.', ',', '"', "'"],
        'crosshatch': ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '!', '?', '.', ',', '"', "'"],
    }

    words = text.split(' ')
    phrase = []

    for word in words:
        letters = [l for l in word]
        translated = ''

        for letter in letters:
            for key, value in special_list.items():
                if letter in value:
                    idx = value.index(letter)
                    translated += target[idx]

        phrase.append(translated)

    phrase = ' '.join(phrase)

    return phrase


def decontracted(phrase):
    # specific
    phrase = re.sub("won\'t", "will not", phrase)
    phrase = re.sub("can\'t", "can not", phrase)

    # general
    phrase = re.sub("n\'t", " not", phrase)
    phrase = re.sub("\'re", " are", phrase)
    phrase = re.sub("\'s", " is", phrase)
    phrase = re.sub("\'d", " would", phrase)
    phrase = re.sub("\'ll", " will", phrase)
    phrase = re.sub("\'t", " not", phrase)
    phrase = re.sub("\'ve", " have", phrase)
    phrase = re.sub("\'m", " am", phrase)

    return phrase


def british_to_american(text):
    """
    """
    br_am = pickle.load(open("british_to_american.pkl", 'rb'))

    words_list = text.split()

    for idx, word in enumerate(words_list):
        first_letter = word[0]
        word = word.lower()
        if word in br_am.keys():
            words_list[idx] = first_letter + br_am[word][1:]

    text = ' '.join(words_list)

    return text


def precleaning(text, account):
    """

    """
    br_am = pickle.load(open("british_to_american.pkl", 'rb'))
    r_ = "((\w+[\-’']\w+)|([a-zA-Z0-9\.',;:?!]+)+)"

    text = restore_spaced_title(text)
    text = remove_hashtags_mentions_urls(text)

    text = ' '.join([e[0] for e in re.findall(
        r_, text) if (e != account)]).strip()
    text = text.replace('’', "'")
    text = ud.normalize('NFKD', text)
    text = decontracted(text)
    text = british_to_american(text)

    return text


def connect_to_db():
    """
    On your Terminal:
    $ echo .env >> .gitignore

    # ----
    # WAY_1
    # ----

    $ touch .env
    $ echo export MONGOUSER = your_username >> .env
    $ echo export MONGOPASSWORD = your_password >> .env
    $ echo export MONGODBNAME = your_database_name >> .env

    # ----
    # WAY_2
    # ----

    $ nano .env

    # write in .env the next lines
    # export MONGOUSER = 'your_username'
    # export MONGOPASSWORD = 'your_password'
    # export MONGODBNAME = 'your_database_name'
    On your Jupyter Notebook:

    from dotenv import load_dotenv
    import os


    project_folder = os.path.expanduser('~/') # the folder of your project
    load_dotenv(os.path.join(project_folder, '.env'))

    MONGOUSER = os.getenv("MONGOUSER")
    MONGOPASSWORD = os.getenv("MONGOPASSWORD")
    MONGODBNAME = os.getenv("MONGODBNAME")

    client = pymongo.MongoClient(f"mongodb+srv://{MONGOUSER}:{MONGOPASSWORD}@something.something.gcp.mongodb.net/{MONGODBNAME}?moresomething")
    db = client['your_database_name'] # connect to my database

    collection1 = db['collection1_name'] # one collection
    collection2 = db['collection2_name'] # another collection
    """
    project_folder = os.path.expanduser('../../')
    load_dotenv(os.path.join(project_folder, '.env'))

    MONGOUSER = os.getenv("MONGOUSER")
    MONGOPASSWORD = os.getenv("MONGOPASSWORD")
    MONGODBNAME = os.getenv("MONGODBNAME")

    client = pymongo.MongoClient(
        f"mongodb+srv://{MONGOUSER}:{MONGOPASSWORD}@autotherapy.vfbkj.gcp.mongodb.net/{MONGODBNAME}?retryWrites=true&w=majority")

    return client


def display_topics(model, feature_names, no_top_words, topic_names=None):
    for ix, topic in enumerate(model.components_):
        if not topic_names or not topic_names[ix]:
            print("\nTopic ", ix + 1)
        else:
            print("\nTopic: '", topic_names[ix], "'")
        print(", ".join([feature_names[i]
                         for i in topic.argsort()[:-no_top_words - 1:-1]]))
