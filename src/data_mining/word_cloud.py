import re
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from random import randint

def red_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    return "hsl(0, 100%%, %d%%)" % randint(25, 75)

def green_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    return "hsl(120, 100%%, %d%%)" % randint(25, 75)

def blue_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    return "hsl(240, 100%%, %d%%)" % randint(25, 75)

def purple_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    return "hsl(270, 100%%, %d%%)" % randint(25, 75)

def gray_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    return "hsl(0, 0%%, %d%%)" % randint(10, 90)

def create_word_cloud(df, column, color_func, stop_words):
    text = " ".join(t for t in df[column])
    text =  re.sub(r'[^\x00-\x7F]+', '', text)
    text = " ".join(word for word in text.split() 
                    if word not in stop_words)
    wordcloud = WordCloud(width=800, height=400, max_words=50,
                          stopwords=stop_words,
                          background_color="white",
                          color_func=color_func).generate(text)
    return wordcloud

def wordcloud_subplot(stop_words, df, column, color_func, title, row, col, ax):
    word_cloud = create_word_cloud(df, column, color_func, stop_words)
    ax[row, col].imshow(word_cloud, interpolation='bilinear')
    ax[row, col].axis("off")
    ax[row, col].title.set_text(title)

def create_word_cloud_collage(df, column, stop_words, country):
    fig, ax = plt.subplots(nrows=2, ncols=2, figsize=(12, 6))
    fig.suptitle(f'Word Cloud for {column}', fontsize=16)

    wordcloud_subplot(stop_words, df[df.sentiment_class == "negative"],
                      column, red_color_func, "Negative Sentiment",
                      row=0, col=0, ax=ax)
    wordcloud_subplot(stop_words, df[df.sentiment_class == "positive"],
                      column, green_color_func, "Positive Sentiment",
                      row=0, col=1, ax=ax)
    
    wordcloud_subplot(stop_words, df[df.stance_class == f"against-{country}"],
                      column, gray_color_func, f"Against-{country}",
                      row=1, col=0, ax=ax)
    wordcloud_subplot(stop_words, df[df.stance_class == f"pro-{country}"],
                      column, blue_color_func, f"Pro-{country}",
                      row=1, col=1, ax=ax)

    plt.show()
    
def create_contrastive_word_cloud(df, column, stop_words):
    fig, ax = plt.subplots(nrows=2, ncols=2, figsize=(12, 6))
    fig.suptitle(f'Word Cloud for {column}', fontsize=16)

    wordcloud_subplot(stop_words, df[(df.sentiment_class == "negative") &
                                     (df.source_type == "local")],
                      column, red_color_func, "Local Negative Sentiment",
                      row=0, col=0, ax=ax)
    wordcloud_subplot(stop_words, df[(df.sentiment_class == "positive") &
                                     (df.source_type == "local")],
                      column, green_color_func, "Local Positive Sentiment",
                      row=0, col=1, ax=ax)
    
    wordcloud_subplot(stop_words, df[(df.sentiment_class == "negative") &
                                     (df.source_type == "international")],
                      column, gray_color_func, "International Negative Sentiment",
                      row=1, col=0, ax=ax)
    wordcloud_subplot(stop_words, df[(df.sentiment_class == "positive") &
                                     (df.source_type == "international")],
                      column, blue_color_func, "International Positive Sentiment",
                      row=1, col=1, ax=ax)

    plt.show()