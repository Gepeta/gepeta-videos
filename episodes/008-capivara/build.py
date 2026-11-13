import re
kit = open('/home/claude/gepeta-videos/episodes/006-tamandua/index.html').read()
M = "// ================================================================ "
twoD = kit[kit.index(M + "2D"):kit.index(M + "DIREÇÃO")]
NEWRE = "const RED = /^(fácil|nojenta|cocô|onça|porra|fugir|carrapatos)/i, GRN = /^(\\d+|graça|maior|minutos|duas|dez|vinte|capim|ama|vida|brasil)$/i;"
twoD = re.sub(r"const RED = /.*?/i, GRN = /.*?/i;", lambda m: NEWRE, twoD, count=1, flags=re.S)
new = open('scene.js').read()
A, B = new.split("//@@2D@@")
head = '''<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
@font-face { font-family: Cap; src: url('file:///usr/share/fonts/opentype/inter/Inter-Black.otf'); }
@font-face { font-family: CapI; src: url('file:///usr/share/fonts/opentype/inter/Inter-BlackItalic.otf'); }
html,body{margin:0;background:#000}
</style>
<script type="importmap">{"imports":{"three":"./node_modules/three/build/three.module.js","three/addons/":"./node_modules/three/examples/jsm/"}}</script>
</head><body>
<canvas id="out" width="1080" height="1920"></canvas>
<script type="module">
'''
open('index.html', 'w').write(head + A + twoD + B + "\n</script></body></html>\n")
print("ok")
