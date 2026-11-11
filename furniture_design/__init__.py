"""furniture-design: the knowledge base and the furniture-design@ quern package.

Importing it registers the furniture/* calculations the package's rules reach, as importing
geometry registers geometry/*. A design tree pins furniture-design@ in quern.lock, mounts
`knowledge()` beside its pieces, and runs the rules.
"""

from .knowledge import knowledge
from .natives import register

register()

__all__ = ["knowledge"]
