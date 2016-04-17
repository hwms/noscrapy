from flask import Blueprint, flash, redirect, render_template, url_for
from markupsafe import escape

from .forms import SignupForm

frontend = Blueprint('frontend', __name__)


@frontend.route('/')
def index():
    return render_template('frontend/index.html')


@frontend.route('/example-form/', methods=('GET', 'POST'))
def example_form():
    form = SignupForm(csrf_enabled=False)

    if form.validate_on_submit():
        flash('Hello, {}. You have successfully signed up'
              .format(escape(form.name.data)))
        return redirect(url_for('.index'))

    return render_template('frontend/signup.html', form=form)
