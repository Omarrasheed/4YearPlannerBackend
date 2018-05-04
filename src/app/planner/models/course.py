from . import *

class Course(Base):
  __tablename__ = 'courses'
  id             = db.Column(db.Integer, primary_key=True)
  title          = db.Column(db.String(256), unique=True, nullable=False)
  subject        = db.Column(db.String(256), nullable=False)
  number         = db.Column(db.String(256), nullable=False)
  description    = db.Column(db.Text)
  term           = db.Column(db.String(256))
  creditsMax     = db.Column(db.Integer)
  creditsMin     = db.Column(db.Integer)
  prereqs        = db.Column(db.String(256))

  def __init__(self, **kwargs):
    """
    Constructor
    """
    self.title = kwargs.get('title', None)
    self.subject = kwargs.get('subject')
    self.number = kwargs.get('number')
    self.description = kwargs.get('description')
    self.term = kwargs.get('term')
    self.creditsMax = kwargs.get('creditsMax', 0)
    self.creditsMin = kwargs.get('creditsMin', 0)
    self.prereqs = kwargs.get('prereqs', None)