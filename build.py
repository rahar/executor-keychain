src = open('template.html').read()
core = open('core.js').read().replace("if (typeof module !== 'undefined') module.exports = ExecutorCore;", '')
assert '</script' not in core
open('executor.html', 'w').write(src.replace('/*CORE*/', core))
print('built', len(src) + len(core))
