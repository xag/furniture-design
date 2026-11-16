import sys, importlib.util
from pathlib import Path
sys.path.insert(0, 'C:/Users/trans/Projects/furniture')
from app import model
from furniture_design.scene import scene
# the viewer drawn is the worktree's, not the installed one
spec = importlib.util.spec_from_file_location('furniture_design.proto_viewer', 'C:/Users/trans/Projects/furniture-design-proto3d/furniture_design/viewer.py')
pv = importlib.util.module_from_spec(spec); spec.loader.exec_module(pv)
node = model.load(Path(sys.argv[1]))
tree = model.tree(node)
sc = scene(tree, model.path_of(node))
pv.viewer_html(sc, Path(sys.argv[2]), sys.argv[3] if len(sys.argv) > 3 else "fr")
print('ok', len(sc.parts), 'parts')
