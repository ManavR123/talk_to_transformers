import argparse
import csv
import re
import os
import shutil

import nltk
from nltk.tokenize import TweetTokenizer

import praw
from praw.models import MoreComments

from tqdm import tqdm

reddit = praw.Reddit(
    client_id=os.environ.get("redditClientId"),
    client_secret=os.environ.get("redditSecret"),
    user_agent=os.environ.get("redditName"),
)

MAX_DEPTH = 5
tokenizer = TweetTokenizer(preserve_case=True)
STOP_WORDS = set(nltk.corpus.stopwords.words("english"))


def clean_text(text):
    text = re.sub(' +', ' ', text)

    return (
        text.replace("\n", " ")
        .replace("\r", "")
        .replace("\t", " ")
        .replace("b/c", "because")
        .replace("j/k", "just kidding")
        .replace("w/o", "without")
        .replace("w/", "with")
        .replace(chr(92), "")
        # get rid of unicode to keep things simple
        .encode('ascii', 'ignore').decode('ascii')
    )


def valid_comment(comment):
    words = tokenizer.tokenize(comment)
    if len(words) > 200:
        return False

    if len(set(words).intersection(STOP_WORDS)) < 3:
        return False

    if "http" in comment:
        return False
    
    if not comment:
        return comment

    return True


def scrape_subreddit(subreddit_name, num_posts):
    if os.path.isdir(subreddit_name):
        shutil.rmtree(f"./{subreddit_name}")

    os.mkdir(subreddit_name)

    subreddit = reddit.subreddit(subreddit_name)

    posts = []
    for post in tqdm(subreddit.hot(limit=num_posts)):
        posts.append([post.subreddit, post.id, post.url, post.num_comments, post.created])

        submission = reddit.submission(id=post.id)
        submission.comments.replace_more(limit=None)

        def get_comment_paths(comment_forest, depth=0):
            if not comment_forest or depth == MAX_DEPTH:
                return [[]]

            paths = []
            for top_level_comment in comment_forest:
                comment = clean_text(top_level_comment.body)
                if not valid_comment(comment):
                    continue

                for path in get_comment_paths(top_level_comment.replies, depth=depth + 1):
                    paths.append([comment] + path)

            return paths

        comment_paths = get_comment_paths(submission.comments)
        comment_paths = list(filter(lambda x: len(x) > 1, comment_paths))

        with open(os.path.join(subreddit_name, "comments.csv"), "a+", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile, delimiter=",", quoting=csv.QUOTE_MINIMAL)
            writer.writerows(comment_paths)

    with open(os.path.join(subreddit_name, "post_data.csv"), "a+", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=",", quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["subreddit", "id", "url", "num_comments", "created"])
        writer.writerows(posts)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
    "--subreddit", type=str, help="name of subreddit to scrape",
    )
    parser.add_argument(
    "--num_posts", type=int, default=100, help="number of posts to scrape",
    )
    args = parser.parse_args()
    scrape_subreddit(args.subreddit, args.num_posts)
