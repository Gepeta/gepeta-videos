kit = open('/home/claude/gepeta-videos/episodes/006-tamandua/index.html').read()
M = "// ================================================================ "
head = kit[:kit.index(M + "CERRADO")]
twoD = kit[kit.index(M + "2D"):kit.index(M + "DIREÇÃO")]
def rep(s, a, b):
    assert s.count(a) == 1, a
    return s.replace(a, b)
head = rep(head, "if (i < 3) { const light = new THREE.PointLight(0xffe7bd, 4.2, 9, 1.7); light.position.y = -0.45; g.add(light); }",
           "let light = null; if (i < 3) { light = new THREE.PointLight(0xffe7bd, 4.2, 9, 1.7); light.position.y = -0.45; g.add(light); }")
head = rep(head, "cone.position.y = -1.75; g.add(cone);", "cone.position.y = -1.75; g.add(cone); (G.userData.lamps = G.userData.lamps || []).push({ bulb, cone, light });")
head = rep(head, "G.add(spot, spot.target);", "G.add(spot, spot.target); G.userData.spot = spot;")
head = rep(head, "G.add(new THREE.HemisphereLight(0x9fb2a0, 0x2a2418, 0.4));", "const hemiC = new THREE.HemisphereLight(0x9fb2a0, 0x2a2418, 0.4); G.add(hemiC); G.userData.hemi = hemiC;")
head = rep(head, "rim.position.set(-2, 2.5, -4); G.add(rim);", "rim.position.set(-2, 2.5, -4); G.add(rim); G.userData.rim = rim;")
head = rep(head, "fill.position.set(0.9, 1.6, 2.4); G.add(fill);", "fill.position.set(0.9, 1.6, 2.4); G.add(fill); G.userData.fill = fill;")
head = rep(head, "gep.position.set(0, 0, 0); gep.rotation.y = o.ry || 0;", "gep.position.copy(o.pos || V(0, 0, 0)); gep.rotation.y = o.ry || 0;")
head = rep(head, "  if (o.jig) {", "  if (o.af) o.af(RA, LA);\n  if (o.jig) {")
twoD = rep(twoD, "const RED = /^(língua|onça|morder|porrada|foda|garras|ameaçado|soldados|calma|linguarudo|abraço)/i, GRN = /^(\\d+|mil|minuto|um|nenhum|rapidinha|vivo|rodízio|respeito)$/i;",
           "const RED = /^(ejeção|cara|fritar|fodeu|escuro|acabou|faísca|apagou|último|não)/i, GRN = /^(\\d+|bilhões|horas|água|dinheiro|rei|fica|vai|verde|dois|um|meses|segundos)$/i;")
new = open('scene.js').read()
A, B = new.split("//@@2D@@")
open('index.html', 'w').write(head + A + twoD + B + "\n</script></body></html>\n")
print("ok", len(head), len(A), len(twoD), len(B))
