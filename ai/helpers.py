# ai.helpers.py
import re


def strip_markdown_links(text):
    text = re.sub(r"\[([^\]]*)\]\(https?://[^\)]*\)", r"\1", text)
    text = re.sub(r"https?://\S+", "", text)
    return text
