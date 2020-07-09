FROM python:3
ENV PYTHONUNBUFFERED 1

COPY requirements.txt /code/requirements.txt
RUN pip install -r /code/requirements.txt

COPY intro.mp4 /code/intro.mp4
COPY streamable.py /code/streamable.py


WORKDIR /code/

ENV number_of_videos ""
ENV game ""
ENV twitch_id ""
ENV username ""
ENV password ""
ENV subreddit ""
ENV reddit_id ""
ENV reddit_secret ""



CMD  "python streamable.py"
