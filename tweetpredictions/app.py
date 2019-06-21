from decouple import config
from flask import Flask, render_template, request, url_for
from .models import DB, User, Predictions
from .predict import predict_user, visualize_prediction, add_prediction
from .twitter import add_or_update_user, display_tweets

def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = config('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    DB.init_app(app)

    @app.route('/')
    def root():
        predictions = Predictions.query.all()
        predictions.reverse()
        return render_template('base.html', title='Home', predictions=predictions)


    @app.route('/user', methods=['POST'])
    @app.route('/user/<name>', methods=['GET'])
    def user(name=None):
        message = ''
        tweets = []
        name = name or request.values['user_name']
        try:
            if request.method == 'POST':
                add_or_update_user(name)
                message = 'User {} successfully added!'.format(name)
            tweets = User.query.filter(User.name == name).one().text
        except Exception as e:
            message = 'Error adding {}: {}'.format(name, e)
            tweets = []
        return render_template('user.html', title=name, tweets=tweets,
                               message=message)

    @app.route('/compare', methods=['POST', 'GET'])
    def compare():
        user_1 = request.form['user_1']
        user_2 = request.form['user_2']
        input_text = request.form['tweet_text']
        message = ''
        less_likely_user, more_likely_user = (0,0)
        try:
            u1_prob, u2_prob, less_likely_user, more_likely_user = predict_user(user_1,
                                                                                user_2,
                                                                                input_text)
            viz_name = visualize_prediction(user_1, u1_prob, user_2, u2_prob)
            u1_tweets = display_tweets(more_likely_user)
            u2_tweets = display_tweets(less_likely_user)
            add_prediction(input_text, user_1, u1_prob, user_2, u2_prob)
            message = 'Comparision Successfully Made'
        except Exception as e:
            message = 'Error comparing {} vs. {}: {}'.format(user_1,
                                                             user_2, e)
        return render_template('compare.html', user_1=user_1, user_2=user_2,
                               input_text=input_text, u1_prob=u1_prob,
                               u2_prob=u2_prob,
                               less_likely_user=less_likely_user,
                               more_likely_user=more_likely_user,
                               message=message,
                               u1_tweets=u1_tweets,
                               u2_tweets=u2_tweets,
                               viz_name=viz_name)

    @app.route('/archive')
    def archive():
        try:
            predictions = Predictions.query.all()
            predictions.reverse()
            message = 'Success!'
        except Exception as e:
            message = f'Error Viewing Past Predictions: {e}'
            predictions = []
        return render_template('archive.html', predictions=predictions,
                               messsage=message)

    @app.route('/reset')
    def reset():
        DB.drop_all()
        DB.create_all()
        return render_template('base.html', title='DB Reset!', users=[])

    return app
