from . import *

class Course(Base):
  __tablename__ = 'courses'
  id            = db.Column(db.Integer, primary_key=True)
  title         = db.Column(db.String(256), nullable=False)
  subject       = db.Column(db.String(10), nullable=False)
  number        = db.Column(db.String(5), nullable=False)
  description   = db.Column(db.Text)
  term          = db.Column(db.String(100))
  creditsMax    = db.Column(db.Integer)
  creditsMin    = db.Column(db.Integer)
  prereqs       = db.Column(db.Text)
  distribution  = db.Column(db.String(100))
  gradingType   = db.Column(db.String(100))
  acadGroup     = db.Column(db.String(10))
  subjNum       = db.Column(db.String(20), unique=True)

  def __init__(self, **kwargs):
    """
    Constructor
    """
    self.title        = kwargs.get('title', None)
    self.subject      = kwargs.get('subject')
    self.number       = kwargs.get('number')
    self.description  = kwargs.get('description')
    self.term         = kwargs.get('term')
    self.creditsMax   = kwargs.get('creditsMax', 0)
    self.creditsMin   = kwargs.get('creditsMin', 0)
    self.prereqs      = kwargs.get('prereqs', None)
    self.distribution = kwargs.get('distribution', None)
    self.gradingType  = kwargs.get('gradingType')
    self.acadGroup    = kwargs.get('acadGroup')
    self.subjNum      = kwargs.get('subjNum')
