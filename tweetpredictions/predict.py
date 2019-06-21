import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import numpy as np 
import os
import time

def warn(*args, **kwargs):
    pass
import warnings
warnings.warn = warn

from sklearn.linear_model import LogisticRegression
from .models import DB, User, Predictions
from .twitter import BASILICA, add_or_update_user


def predict_user(user1_name, user2_name, tweet_text):
    # Verify User name not submitted with @ in it
    user1_name = user1_name.replace('@','')
    user2_name = user2_name.replace('@','')

    # Add or Update User
    add_or_update_user(user1_name)
    add_or_update_user(user2_name)

    user1 = User.query.filter(User.name == user1_name).one()
    user2 = User.query.filter(User.name == user2_name).one()
    user1_embeddings = np.array([tweet.embedding for tweet in user1.text])
    user2_embeddings = np.array([tweet.embedding for tweet in user2.text])
    embeddings = np.vstack([user1_embeddings, user2_embeddings])
    labels = np.concatenate([np.ones(len(user1.text)),
                            np.zeros(len(user2.text))])
    log_reg = LogisticRegression(solver='lbfgs').fit(embeddings, labels)
    tweet_embedding = BASILICA.embed_sentence(tweet_text, model='twitter')
    pred_prob = log_reg.predict_proba(np.array(tweet_embedding).reshape(1,-1))
    u2_prob, u1_prob = pred_prob[0]
    if u2_prob > u1_prob:
        more_likely_user = user2_name
        less_likely_user = user1_name
    elif u2_prob < u1_prob:
        more_likely_user = user1_name
        less_likely_user = user2_name
    else:
        more_likely_user = "It's a Tie!"
        less_likely_user = "It's a Tie!"
    return u1_prob, u2_prob, less_likely_user, more_likely_user


def visualize_prediction(u1_name, u1_prob, u2_name, u2_prob):

    labels = [u1_name, u2_name]
    data = [u1_prob, u2_prob]

    for i, label in enumerate(labels): 
        if '@' not in label:
            labels[i] = '@' + label

    # Adjust figure size
    fig, ax = plt.subplots(figsize=(14,7))
    # Adjust color of gridlines
    ax.grid(alpha=0.3)

    plt.barh(labels, data, color='#759AFF')

    for i, label in enumerate(data):
        ax.text(label + .01, i-0.05, str(label)[2:4] + '.' + str(label)[5:7] + '%', color='black', fontsize=18, fontweight='bold')

    # Set location of x-axis ticks
    ax.set(xticks=[0, 0.2, 0.4, 0.6, 0.8, 1.0])

    # Set x-axis tick labels (not strictly neccesary in this case)
    ax.set_xticklabels(["0%", "20%", "40%", "60%", "80%", "100%"])

    # Set x-axis label
    ax.text(-.12, 1.7, 'Estimated probability of each user being the more likely to tweet it', fontweight='bold', fontsize=24)
    # Set font-size of axes
    ax.tick_params(axis='both', labelsize=18)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    plt.tick_params(top=False, bottom=False, left=False, right=False, labelleft=True, labelbottom=True)

    t = str(time.time())
    t = t.replace('.', '')
    new_viz_name = 'images/compare_' + t + '.png'

    for filename in os.listdir('tweetpredictions/static/images/'):
        if filename.startswith('compare_'):
            os.remove('tweetpredictions/static/images/' + filename)

    plt.savefig("tweetpredictions/static/" + new_viz_name, bbox_inches='tight')
    return new_viz_name

def add_prediction(text, u1_name, u1_prob, u2_name, u2_prob):
    try:
        pred = Predictions()
        DB.session.add(pred)
        pred.text = text
        if '@' in u1_name:
            pred.user_1_name = u1_name
        else:
            pred.user_1_name = '@' + u1_name
        pred.user_1_prob = round(u1_prob * 100, 2)
        if '@' in u2_name:
            pred.user_2_name = u2_name
        else:
            pred.user_2_name = '@' + u2_name
        pred.user_2_prob = round(u2_prob *100, 2)
    except Exception as e:
        print(f'Error adding Prediction: {e}')
    else:
        DB.session.commit()
