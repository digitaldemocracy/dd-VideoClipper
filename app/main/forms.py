from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, RadioField, IntegerField, SelectField, FileField
from wtforms.validators import DataRequired, regexp
from wtforms.fields.html5 import DateField
from wtforms.fields import FieldList

class VEditForm(Form):
   videos = FieldList(StringField('Video'), min_entries=3) 
   #video = StringField('Video')
   start = IntegerField('start')
   length = IntegerField('length')
   uid = StringField('uid', validators=[DataRequired()])
   method = SelectField('method', choices=[('cut', 'cut'), ('concat', 'concat'), ('upload', 'upload'), ('delete', 'delete')])
   date = DateField('DatePicker', format='%Y-%m-%d')
   submit = SubmitField('Submit')
