class BaseSchema:
 """ 
 This is the base class for deining and validating request/response data.
 """

 def __init__(self, **kwargs):
  self._raw = kwargs
  self.validate(kwargs)
 
 def validate(self, data: dict):
  """ This method is going to be overwritten in subclasses to perform validation """
  raise NotImplementedError("Subclasses must implement validate()")
 
 def to_dict(self):
  return self._raw
 
 @classmethod
 def from_dict(cls, data: dict):
  """Validate and return a new instance from a dictionary."""
  return cls(**data)