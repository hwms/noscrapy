from flask_wtf import Form
from wtforms import fields
from wtforms.validators import Email, Required


class SignupForm(Form):
    csrf_enabled = False
    name = fields.TextField('Your name', validators=[Required()])
    password = fields.TextField('Your favorite password', validators=[Required()])
    email = fields.TextField('Your email address', validators=[Email()])
    birthday = fields.DateField('Your birthday')

    a_float = fields.FloatField('A floating point number')
    a_decimal = fields.DecimalField('Another floating point number')
    a_integer = fields.IntegerField('An integer')

    now = fields.DateTimeField('Current time',
                               description='...for no particular reason')
    sample_file = fields.FileField('Your favorite file')
    eula = fields.BooleanField('I did not read the terms and conditions',
                               validators=[Required('You must agree to not agree!')])

    submit = fields.SubmitField('Signup')
