# News Outlet Freedom Detection

There are many news organizations around the world. News organizations play a vital role in relaying important news of home and abroad to its readers. These news often cover incidents that are either positive, negative, or neutral. Moreover, some news stories can be viewed as talking for a country or talking against it. 

> Freedom of speech is the right to express one's ideas and opinions without censorship, restraint, or fear of retribution.

A news outlet is free if it can report news in an unbiased manner and free from censorship. In this project, we aim to detect if a local news organization is free. To do so, we compare the sentiment and stance of the organization with international news reporting institutions **Reuters** and **Associated Press**. A news outlet whose news correlates well with these international organizations are deemed as having freedom of press. Meaning, they are free from censorship.

![Python](https://img.shields.io/badge/Python-20232A?style=for-the-badge&logo=python)
![Jupyter](https://img.shields.io/badge/jupyter-20232A?style=for-the-badge&logo=jupyter)
![PyTorch](https://img.shields.io/badge/PyTorch-20232A?style=for-the-badge&logo=pytorch)
![HuggingFace](https://img.shields.io/badge/%F0%9F%A4%97-HuggingFace-20232A)
![LLAMA2](https://img.shields.io/badge/LLaMa2-20232A?style=for-the-badge&logo=Meta)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1MZ5INZ7PWzq2pRyfP8SvEIruCz4LNdqa?usp=sharing)

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#problem-statement">Problem Statement</a></li>
    <li><a href="#data-collection">Data Collection</a></li>
    <li><a href="#bertopic">BERTopic</a></li>
    <li><a href="#sentiment-and-stance-analysis-with-llama-2">Sentiment and stance analysis with LLaMa-2</a></li>
    <li><a href="#case-studies">Case Studies</a></li>
    <ul>
        <li><a href="#china">China</a></li>
        <li><a href="#canada">Canada</a></li>
        <li><a href="#russia">Russia</a></li>
    </ul>
  </ol>
</details>

***

## Problem Statement

This study investigates freedom of speech in local news across countries, examining topic-specific distinctions by comparing sentiment and stance scores with international sources to reveal correlations and assess agreement levels.

<p align="right">(<a href="#news-outlet-freedom-detection">back to top</a>)</p>

## Data Collection

| Source        | Canada                       | Russia           | China       |
| ------------- | ---------------------------- | ---------------- | ----------- |
| Local         | CBC and Global News          | The Moscow Times | China Daily |
| International | Reuters and Associated Press |

* Used Selenium to search and accumulate article URLs. 
* Employed News Please to fetch article data from collected URLs.
* Raw data was processed to get it ready for the text mining steps.

![Data Distribution](images\plots\barchart_scraped_data.png)

<p align="right">(<a href="#news-outlet-freedom-detection">back to top</a>)</p>

## BERTopic

I used BERTopic to perform topic modeling. BERTopic has 4 distinct phases:

1. It uses **Sentence Transformer Model** to convert sentences into vector representations. Often having dimensions exceeding 256.

2. To reduce dimensions from 256, BERTopic employs **UMAP**. This reduces the dimensions while retaining global and local information among the data.

3. Afterwards, vectors are clustered using **HDBSCAN** a hiererchical algorithm.

4. Finally, c-TF-IDF is used to get topic representations for each cluster.

5. Fed top 10 represention words for each topic into ChatGPT to get a word for custom topic name.

![BERTopic](images\BERTopic_diagram.png)

<p align="right">(<a href="#news-outlet-freedom-detection">back to top</a>)</p>

***

## Sentiment and stance analysis with LLaMa-2

I used LLaMa-2, the open-source LLM from meta, for sentiment and stance analysis. To do so, I first had to finetune the base version of a 6 billion parameter LLaMa2 model.

### Funetuning LLaMa-2

1. Engineered prompt to get the best possible answer from an LLM. The prompt was tuned with [Prompt Perfect](https://promptperfect.jina.ai/).

        As a neutral news analyst, assess the sentiment and stance of the news article excerpt and assign a score between -1.0 (completely negative/against-{country}) and 1.0 (completely positive/pro-{country}) for both sentiment and stance. Provide a single short sentence to justify your scores, drawing on the article's language, tone, and presentation to support your analysis.

        Article Excerpt:
        - Title: "{title}"
        - Content: "{content}{dot}"

        Output format: 
        1. Sentiment: [Positive/Neutral/Negative]
            * Score: [Your Score]
            * Reason: [Your Reason] 
        2. Stance: [Pro-{country}/Impartial/Against-{country}]
            * Score: [Your Score]
            * Reason: [Your Reason]

2. Select 300 samples from dataset to finetune LLaMa-2 model. Fit each example in the prompt and feed it to ChatGPT. Save answers from ChatGPT as finetuning dataset.

3. Utilize huggingface's autotrain package to finetune LLaMa-2. 

    * Used QLoRA to enable training on single GPU on google colab.

    * Used PEFT (Parameter Efficient Finetuning) to reduce training time.


### Sentiment and Stance Analysis 

1. Use finetuned model to inference on collected data.

2. Parse responses to get sentiment and stance classes and scores for each article.

3. Perform hypothesis testing to arrive at conclusions.

| Test Name       | Parameter of Interest  | Null Hypothesis                                                          |
| --------------- | ---------------------- | ------------------------------------------------------------------------ |
| Welch Test      | Mean                   | Both sources on average report news with the same score.                 |
| Wilcoxon Test   | Median                 |
| F-test          | Variance               | News from sources have similar variance across sentiment and/or stance.  |
| Pearson’s Test  | Linear Correlation     | Sentiment and/or stance of reported news from sources aren’t correlated. |
| Spearman’s Test | Monotonic Relationship |

<p align="right">(<a href="#news-outlet-freedom-detection">back to top</a>)</p>

***

## Case Studies

### Canada

![Canadian News Topic Distribution](images\plots\Canada\canada_barchart_topics.png)

![Canadian News Sentiment Score Distribution](images\plots\Canada\canada_boxplot_sentiment.png)

![Canadian News Sentiment Score inference results](images\plots\Canada\canada_heatmap_inference_sentiment.png)

![Canadian News Stance Score Distribution](images\plots\Canada\canada_boxplot_stance.png)

![Canadian News Stance Score inference results](images\plots\Canada\canada_heatmap_inference_stance.png)

### China

### Russia