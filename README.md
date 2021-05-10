# Talk-To-Transformers

This is the repo for the talk-to-transformers app that can be found [here](https://talk-to-transformers.herokuapp.com/). In this README, we will briefly explain the code architecture and discuss some of the design decisions for the project.

## Tech Stack

This is a simple single page React app with a Flask backend. This stack was chosen mainly out of personal preference and for the sake of simplicity.

### Backend

We use the python package Flask, a lightweight web application framework to manage our backend system. We don't have a very complicated backend system, so Flask seemed like the best choice to provide a quick and easy REST API to manage the single route our frontend relies on. We also wantd to stick to a python backend, so that if we were use to native PyTorch models as part of our application, we would be able to integrate them more easily.

### Frontend

For the frontend, we use the popular javascript library React. Using React simplified the process for developing the frontend as we used the `create-react-app` tool to boostrap the app and took advantage of the many popular existing packages to build out a simple UI. React is also excellent at managing interactions on a webpage and maintaining and updating the state of interactions through built-in "hooks", which made keeping track of conversations super simple.

For most of out the UI, we used the Material UI library to design and stylize our components to provide a clean user interface.

### Deployment

Our app is currently deployed on Heroku, a cloud platform service. Heroku allows us to deploy our app for free for unlimited time because it is so lightweight and deploying is so simple and required almost no changes to our codebase. This wouldn't have been feasible if we did incorporate a PyTorch model directly into our backend since torch byitself is too big to fit into Heroku's slog. However, we found a way to bypass it using HuggingFace!

The language models used in the application are hosted separetely in the HuggingFace model hub. This model hub not only allowed us to share the models we trained with everyone in community so that they can download them directly and use in their code, but it also provides an accelerated inference API that allows us to generate responses for the user very quickly. This was initially the largest bottleneck in our development process. Reducing the latency caused by model inference is a difficult and costly problem. Having the model in our app natively would require us to host on a larger platform such as AWS, which has a few more challenges with setting up properly and is more costly to host on. HuggingFace, on the other hand, has developed amazing solutions to the inference problem and provides us an easy to use API to provide a better user experience. Of course, nothing comes without some cost. With HuggingFace, we are slightly rate limited such that deploying this application to millions of users would not be possible under the free plan, but given the limited audience we are expecting, this seemed like a sensible decision.

## The Actual ML

Now, let's get into the meat of what makes this application interesting: the deep learning models that power it!

### Model Description

All of the models used in the application are based on the popular GPT2 language model, which is a decoder only transformer model (link to original [paper](https://d4mucfpksywv.cloudfront.net/better-language-models/language-models.pdf)). Microsoft extended this model by specifically training it on multi-turn conversation data. This resulted in the state-of-the-art [DialoGPT](https://arxiv.org/pdf/1911.00536.pdf) model. DialoGPT is trained on large-scale dialogue pairs/sessions extracted from Reddit discussion chains.

In our application, we provide 2 models that users can converse with:

- DialoGPT-large-base: this is the largest version of the model trained by Microsoft that can be found on the HuggingFace model hub
- DialoGPT-Berkeley: this is a version of the base model finetuned on discussions chains found on the UC Berkeley subreddit [r/berekeley](https://www.reddit.com/r/berkeley/).

We were inspired to train a model on the Berkeley subreddit not only since we are Berkeley students, but also to see if a model that is trained more  on a particular subreddit would provide more interesting and focused conversations. We did notice that it was definitely able to pick up on a few interesting specifics of Berkeley students such as identifying that it goes to school at Berkeley and often times claims to be studying computer science, which is the major that is predominately discussed on the subreddit.

### Training

The model is trained to optimize the probability of some target sequence T given a source source sequence S i.e. P(T | S). You can train model for multi-turn conversations, which is a sequence of targets T_{1}, ..., T_{k}, by optimizing all P(T_{i} | T_{1}, ..., T_{i - 1}).

So, to train the model we calculate the probability of generating each next sequence in the conversation and optimize with respect to that gradient.

An interesting challenge for training is that the large version of the models we were working with took up almost the entire space on a single 1080Ti Nvidia GPU, which made single GPU training infeasible unless we reverted to a smaller model. We wanted to stick with the bigger models, however, to take advantage of their more expressive capabilities. So, we went ahead and implemented model-parallelism, which was luckily made easy by the HuggingFace/transformers library that specifically provided multi-gpu model parallelism for GPT based models. This enabled us to train the larger model and get more interesting results!

The code used for training can be found in `/training/train.py`

### Data

Lastly, I want to briefly discuss the data we used for training. As I mentioned, we trained on data from the Berkeley subreddit. We scraped the subreddit using the Reddit API, which provided an easy-to-use interface for collecting data quickly.

However, not all conversations found on the subreddit are high quality data. So, we implemented a few guardrails inspired from the DialoGPT paper to limit out bad data without manual inspection.

The code used for scraping the data can be found in `/training/data/scrape.py`.

## Future Work

If you have any questions feel reach to post an issue on repo or reach out to us directly at either manav.rathod@berkeley.edu or harishpalani@berkeley.edu.

Happy talking!
