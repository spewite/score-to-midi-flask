
class ScoreQualityError(Exception):
  """Raised when the score image quality is too low for processing."""
  pass

class ScoreStructureError(Exception):
  """Raised when the score image structure is not correct."""
  pass

class MidiNotFound(Exception):
  """Raised when the MIDI file is not found."""
  pass

class ScoreTooLargeImageError(Exception):
  """Raised when the uploaded image is too large."""
  pass

class AudiverisTimeoutError(Exception):
  """Raised when Audiveris times out processing a file."""
  pass