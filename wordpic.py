from models import Petition, db
import time
from datetime import datetime, date
import locale
from peewee import chunked
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt
from collections import Counter, OrderedDict
import numpy as np
import matplotlib.dates as mdates
import os


def get_names(petition_n):
    names = []
    query = Petition.select(Petition.username).where(Petition.petition_id == petition_n)
    for i in query:
        try:
            names.append(" ".join(i.username.split()).split(' ')[1])
        except IndexError:
            names.append(" ".join(i.username.split()).split(' ')[0])
    return Counter(names)


def get_genders(petition_n):
    query = Petition.select(Petition.gender).where(Petition.petition_id == petition_n)
    genders = [i.gender for i in query]
    return Counter(genders)


def get_dates(petition_n):
    query = Petition.select(Petition.sign_date).where(Petition.petition_id == petition_n)
    dates = Counter([i.sign_date for i in query])
    dates = OrderedDict(sorted(dates.items(), reverse=False))
    return dates


def draw_pic(petition_n):
    wordcloud = WordCloud(background_color="white", width=2400, height=1600, max_words=100)
    freq = get_names(petition_n)
    wordcloud.generate_from_frequencies(freq)
    plt.figure(figsize=(24, 16))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.savefig(os.path.join('img', f'word {petition_n}.png'), dpi=200)


def draw_bars_pie(petition_n):
    fig, ax = plt.subplots(2, 1, figsize=(10, 10))

    data = get_dates(petition_n)

    def autolabel(rects, height_factor):
        for i, rect in enumerate(rects):
            height = rect.get_height()
            label = '%d' % int(height)
            ax[0].text(rect.get_x() + rect.get_width() / 2., 0.5 * height,
                       '{}'.format(label),
                       ha='center', va='bottom', rotation=90, size=8)

    dates = data.keys()
    values = data.values()
    ax[0].bar(dates, values)
    xfmt = mdates.DateFormatter('%m-%d')
    ax[0].xaxis.set_major_formatter(xfmt)
    plt.setp(ax[0].get_xticklabels(), rotation=45, )
    ax[0].set_title(f'Петиция {petition_n}')
    autolabel(ax[0].patches, height_factor=0.85)

    genders = get_genders(petition_n)

    def make_autopct(values):
        def my_autopct(pct):
            total = sum(values)
            val = int(round(pct * total / 100.0))
            return '{p:.1f}%\n{v:d}'.format(p=pct, v=val)

        return my_autopct

    # sizes = list(genders.values())
    sizes = [genders[True], genders[False], genders[None], ]
    labels = list(genders.keys())
    colors = ['cornflowerblue', 'pink', 'gray']
    ax[1].pie(
        sizes, autopct=make_autopct(sizes), radius=1.3, pctdistance=0.8,
        shadow=True, labeldistance=1.1, colors=colors)
    ax[1].legend(labels=['Муж', 'Жен', 'Не определено'], loc="right", bbox_to_anchor=(1.6, 0.5, 0, 0.7))
    fig.savefig(os.path.join('img', f'diagram {petition_n}.png'), dpi=200)
    fig.clf()

    plt.close()


if __name__ == '__main__':
    petition = 92038
    draw_bars_pie(petition)
    draw_pic(petition)
