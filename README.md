# Talk To Transformers!

This is the repo for our talk-to-transformers app, which can be found [here](https://talk-to-transformers.herokuapp.com/). In this README, we will briefly explain the code architecture and discuss some of the design decisions we made in this project.

## Tech Stack

This site is a single page React app with a Flask backend. This stack was chosen mainly based on personal preference, as well as for the sake of simplicity.

### Backend

We use the Python package Flask, a lightweight web application framework, to manage our backend system. Given that we don't have a very complicated backend system, Flask seemed like the best choice, providing a quick and easy REST API to manage the single route that our frontend relies on. The nature of this project as a deep learning exercise also played a role in our selecting a Python backend, enabling easier downstream integration in case we were to use native PyTorch models as part of our application.

### Frontend

For the frontend, we use the popular JavaScript library React. Using React simplified the process for developing the frontend, as we used the `create-react-app` tool to bootstrap the app and took advantage of the many popular existing packages to build out a simple UI. React is also excellent at managing interactions on a webpage and maintaining and updating the state of interactions through built-in "hooks", which made keeping track of conversations super simple.

As for the UI of our website, we used the Material UI library to stylize our components and provide a clean user interface.

### Deployment

Our app is currently deployed on Heroku, a lightweight cloud platform service. Heroku allowed us to deploy our app for unlimited time at no cost, with a simple, painless deployment process that required almost no changes to our codebase. This wouldn't have been feasible had we ultimately incorporated a PyTorch model directly into our backend, since `torch` by itself is too large to fit into Heroku's slog. However, we found a way to bypass this using HuggingFace!

The language models used in our application are hosted separately in the HuggingFace model hub. This model hub not only allows us to share the models we trained with everyone in community for direct use in their code, but also provides an accelerated inference API that allows us to generate responses for the user very quickly. 

This helped resolve what was initially the largest bottleneck in our development process, as reducing the latency caused by model inference is a difficult and costly problem with only a handful of solutions. For starters, we could have had the model in our app natively — this would have required us to host on a larger platform such as AWS, however, which poses additional few setup challenges and has much higher hosting costs. The HuggingFace approach, on the other hand, provides an easy-to-use API with excellent user experience while also posing a straightforward solution to the inference problem.

Of course, nothing comes without some cost. With HuggingFace, we are slightly rate-limited such that deploying this application to millions of users would not be possible under the free plan. Given the limited audience we are expecting for this project, however, this seemed like a sensible tradeoff.

## The Actual ML

Now, let's get into the meat of what makes this application interesting: the deep learning models that power it!

### Model Description

All of the models used in the application are based on the popular GPT-2 language model, which is a decoder-only transformer model (link to original [paper](https://d4mucfpksywv.cloudfront.net/better-language-models/language-models.pdf)). Microsoft extended this model by specifically training it on multi-turn conversation data. This resulted in the state-of-the-art [DialoGPT](https://arxiv.org/pdf/1911.00536.pdf) model. DialoGPT is trained on large-scale dialogue pairs/sessions extracted from Reddit discussion chains.

In our application, we provide 2 models that users can converse with:

- DialoGPT-large-base: this is the largest version of the model trained by Microsoft that can be found on the HuggingFace model hub
- DialoGPT-Berkeley: this is a version of the base model finetuned on discussions chains found on the UC Berkeley subreddit [r/berkeley](https://www.reddit.com/r/berkeley/)

We were inspired to train a model on the Berkeley subreddit not only since we are Berkeley students, but also to see if a model that is fine-tuned on a particular subreddit would provide more interesting and focused conversations. We did notice that it was definitely able to pick up on a few of the interesting specifics pertaining to Berkeley students — it identifies that it attends UC Berkeley, for starters, and oftentimes even claims to be studying computer science! This aligns with expectations, as EECS/CS courses and activities happen to be predominant topics of discussion on the subreddit.

### Training

The model is trained to optimize the probability of some target sequence T given a source source sequence S — i.e. P(T | S). You can train the model for multi-turn conversations, which is a sequence of targets T<sub>1</sub>, ..., T<sub>k</sub>, by optimizing all P(T<sub>i</sub> | T<sub>1</sub>, ..., T<sub>i-1</sub>).

Therefore, we can train the model by calculating the probability of generating each next sequence in the conversation and subsequently optimizing with respect to that gradient.

An interesting challenge for training is that the large version of the models we were working with took up almost the entire space on a single 1080Ti Nvidia GPU, which made single GPU training infeasible unless we reverted to a smaller model. We wanted to stick with the bigger models, however, to take advantage of their more expressive capabilities. So, we went ahead and implemented model parallelism, which was fortunately made easy by the `HuggingFace/transformers` library! This specifically provided multi-GPU parallelism for GPT-based models, allowing us to train the larger model and get more interesting results.

The code used for training can be found in `/talk_to_transformers/training/train.py`.

### Data

Lastly, we want to briefly discuss the data used for training. As mentioned earlier, we trained on data from the Berkeley subreddit. We scraped the subreddit using the Reddit API, which provided an easy-to-use interface for collecting data quickly.

However, not all conversations found on the subreddit are high-quality data. So, we implemented a few guardrails inspired from the DialoGPT paper to limit out bad data without manual inspection.

The code used for scraping the data can be found in `/talk_to_transformers/training/data/scrape.py`.

## Future Work

Regarding next steps, we are currently working on integrating voice cloning capabilities within our website. In doing so, our transformer models will be able to mimic a voice of your choice when replying, allowing users to converse with anyone they'd like! Though we had initially hoped to have this fully integrated in our final deliverable for this project, we faced a number of unforeseen obstacles along the way which posed significant implementation challenges.

Our audio model is based on Corentin Jemime's real-time voice cloning work [here](https://github.com/CorentinJ/Real-Time-Voice-Cloning), bringing Google's [Speaker Verification to Multispeaker Text-To-Speech Synthesis (SV2TTS)](https://arxiv.org/pdf/1806.04558.pdf) transfer learning pipeline to life with the help of the latest [Tacotron](https://google.github.io/tacotron/) models for speech synthesis and DeepMind's [WaveRNN](https://arxiv.org/pdf/1802.08435v1.pdf) as a real-time vocoder. The PyTorch model implementation pairs well with our Flask backend, allowing for more straightforward integration with the existing [talk-to-transformers](https://talk-to-transformers.herokuapp.com/) application than other non-Python alternatives.

To help demonstrate the full capabilities of this model, we've set up a Colab demo [here](https://colab.research.google.com/drive/1IQBWb-2GJ8N96LWIuVDea0Yg_ZNCRyUn?usp=sharing) which leverages pre-trained model weights to synthesize cloned speech of some specified text based on either an uploaded audio clip or a live recording. This demo code can also be found in `/voice_cloning` at `voice-cloning.ipynb`, and represents added functionality which you should expect to see available on [talk-to-transformers](https://talk-to-transformers.herokuapp.com/) in the near future!

If you have any questions, feel reach to post an issue on repo or reach out to us directly at either manav.rathod@berkeley.edu or harishpalani@berkeley.edu.

Happy talking!
