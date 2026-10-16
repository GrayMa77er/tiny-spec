// tiny-spec view — the in-session half of the visualizer.
//
// Every few seconds this runs the plugin's own tiny_spec/state.py (the same derivation
// `tiny-spec view` serves in a browser) and draws it inside Claude Code: a one-line band
// above the prompt while a run is active, and a /tiny-spec pane with Run / Graph /
// Report / Explorer tabs. On top of the git-derived state it shows what git can't —
// which tiny-spec executor and reviewer subagents are running right now — read live
// from $.agent.list(). It writes nothing: no store, no files, no state.

const PANE = 'tiny-spec'
const POLL_MS = 5000
const ACTIVE = ['building', 'paused', 'blocked', 'exhausted', 'fork', 'review', 'built', 'planning']
const HALTED = ['blocked', 'exhausted', 'fork', 'paused']
const MARK = {
  merged: '✓', built: '●', review: '⇡', building: '◐', paused: '‖', blocked: '✗',
  exhausted: '✗', fork: '⑂', planning: '…', 'not-started': '○',
}
const COLOR = {
  merged: 'green', built: 'green', review: 'blue', building: 'yellow', paused: 'magenta',
  blocked: 'red', exhausted: 'red', fork: 'red', planning: 'gray', 'not-started': 'gray',
}

let snap = null // last state.py result
let error = '' // why the last refresh failed, if it did
let agents = [] // tiny-spec subagents in this session
let tab = 'run'
let picked = ''
let busy = false

// --------------------------------------------------------------------- data

async function isProject($) {
  return (await $.fs.exists('.spec')) || (await $.fs.exists('BREAKDOWN.md'))
}

async function refresh($) {
  if (busy) return
  busy = true
  try {
    if (!(await isProject($))) {
      snap = null
      return
    }
    const script = $.plugin.root + '/tiny_spec/state.py'
    const root = await $.session.cwd()
    let out = null
    for (const py of ['python3', 'python']) {
      try {
        out = await $.process.run([py, script, '--root', root])
        break
      } catch (err) {
        out = null
      }
    }
    if (!out) {
      error = 'needs python3 on PATH to read git state'
    } else if (out.exitCode !== 0) {
      error = (out.stderr || 'state.py failed').trim().split('\n').pop()
    } else {
      snap = JSON.parse(out.stdout)
      error = ''
    }
    const all = await $.agent.list()
    agents = (all || []).filter((a) => /tiny-spec-build-(executor|reviewer)/.test(agentKind(a)))
  } catch (err) {
    error = String((err && err.message) || err)
  } finally {
    busy = false
    $.ui.invalidate('ui.render')
  }
}

function agentKind(a) {
  return String(a.agentType || a.type || a.name || a.description || '')
}

function role(a) {
  return /reviewer/.test(agentKind(a)) ? 'reviewer' : 'executor'
}

function live() {
  return agents.filter((a) => a.status === 'running' || a.status === 'pending' || a.status === 'waiting')
}

function features() {
  return (snap && snap.features) || []
}

function isActive() {
  return live().length > 0 || features().some((f) => ACTIVE.includes(f.state))
}

function progress(f) {
  return f.total ? f.done_count + '/' + f.total : ''
}

function batchLabel() {
  const n = (snap && snap.batches.length) || 0
  return n ? 'batch 1/' + n : 'backlog merged'
}

// --------------------------------------------------------------------- hooks

export function register(on) {
  on('session.start', async ($, e, next) => {
    $.clock.every(POLL_MS, () => refresh($))
    refresh($)
    try {
      await $.command.register({
        name: 'tiny-spec',
        description: 'Open the tiny-spec run view (Run / Graph / Report / Explorer)',
        immediate: true,
      })
    } catch (err) {
      $.ui.log('could not register /tiny-spec: ' + String((err && err.message) || err))
    }
    return next(e)
  })

  on('command.run', { command: 'tiny-spec' }, async ($) => {
    await refresh($)
    await $.ui.open({ id: PANE, title: 'tiny-spec', focus: true, closeOnEscape: true })
    return {}
  })

  // The band: one line, only while a run is in flight, so it never clutters a
  // session that isn't building anything.
  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    if (!snap || !isActive()) return next(e)
    const { Box, Text } = $.ui.resolve(e)
    const parts = [Text({ bold: true, children: ['▸ tiny-spec'] }), Text({ dimColor: true, children: [batchLabel()] })]
    for (const f of features().filter((x) => ACTIVE.includes(x.state)).slice(0, 4)) {
      const cur = f.current_task ? ' ' + f.current_task.id : ''
      parts.push(Text({ color: COLOR[f.state], children: [MARK[f.state] + ' ' + f.slug + ' ' + progress(f) + cur] }))
    }
    const running = live()
    if (running.length) {
      parts.push(Text({ color: 'yellow', children: [running.length + ' agent' + (running.length > 1 ? 's' : '') + ' running'] }))
    }
    parts.push(Text({ dimColor: true, children: ['/tiny-spec'] }))
    const theirs = await next(e)
    return Box({ flexDirection: 'column', children: [Box({ flexDirection: 'row', columnGap: 2, children: parts }), theirs] })
  })

  on('ui.render', { component: 'Pane' }, async ($, e, next) => {
    if (e.requestId !== PANE) return next(e)
    const ui = $.ui.resolve(e)
    const { Box, Text, Button } = ui
    const redraw = () => $.ui.invalidate('ui.render')
    const tabButton = (name, label, hotkey) =>
      Button({
        key: 'tab-' + name, label, hotkey, plain: true, dimColor: tab !== name,
        onPress: () => { tab = name; redraw() },
      })
    const header = Box({
      flexDirection: 'row', columnGap: 3,
      children: [
        tabButton('run', 'Run', '1'), tabButton('graph', 'Graph', '2'),
        tabButton('report', 'Report', '3'), tabButton('explorer', 'Explorer', '4'),
        Button({ key: 'refresh', label: 'Refresh', hotkey: 'r', plain: true, dimColor: true, onPress: () => refresh($) }),
      ],
    })
    let body
    if (error) body = [Text({ color: 'red', children: ['tiny-spec: ' + error] })]
    else if (!snap) body = [Text({ dimColor: true, children: ['No .spec/ or BREAKDOWN.md in this directory.'] })]
    else if (tab === 'graph') body = graphView(ui)
    else if (tab === 'report') body = reportView(ui)
    else if (tab === 'explorer') body = explorerView(ui, redraw)
    else body = runView(ui)
    return Box({ flexDirection: 'column', children: [header, Text({ children: [' '] }), ...body] })
  })
}

// --------------------------------------------------------------------- views

function line({ Text }, f, extra) {
  return Text({
    color: COLOR[f.state],
    wrap: 'truncate-end',
    children: [MARK[f.state] + ' ' + f.title + '  ' + f.slug + '  ' + f.state + (progress(f) ? ' ' + progress(f) : '') + (extra || '')],
  })
}

function runView(ui) {
  const { Text } = ui
  const out = []
  const by = Object.fromEntries(features().map((f) => [f.slug, f]))
  snap.batches.forEach((batch, i) => {
    out.push(Text({ bold: true, children: ['Batch ' + (i + 1) + ' of ' + snap.batches.length + (i === 0 ? ' · current' : '')] }))
    for (const slug of batch) {
      const f = by[slug]
      const cur = f.current_task ? '  next ' + f.current_task.id + ' ' + f.current_task.title : ''
      out.push(line(ui, f, cur))
    }
  })
  const merged = features().filter((f) => f.state === 'merged')
  if (merged.length) out.push(Text({ dimColor: true, children: ['Merged: ' + merged.map((f) => f.slug).join(', ')] }))
  const running = live()
  out.push(Text({ children: [' '] }))
  out.push(Text({ bold: true, children: ['Live agents'] }))
  if (!running.length) out.push(Text({ dimColor: true, children: ['none running'] }))
  for (const a of running) {
    out.push(Text({ color: 'yellow', wrap: 'truncate-end', children: ['◐ ' + role(a) + ' · ' + a.status + (a.description ? ' · ' + a.description : '')] }))
  }
  for (const p of snap.problems || []) out.push(Text({ color: 'red', children: ['! ' + p] }))
  return out
}

function graphView(ui) {
  const { Text } = ui
  const out = [Text({ dimColor: true, children: ['needs: edges, by depth — arrows point from a feature to what must come first'] })]
  const depth = Math.max(0, ...features().map((f) => f.depth))
  for (let d = 0; d <= depth; d++) {
    out.push(Text({ bold: true, children: ['depth ' + d] }))
    for (const f of features().filter((x) => x.depth === d)) {
      out.push(line(ui, f, f.needs.length ? '  ← ' + f.needs.join(', ') : ''))
    }
  }
  return out
}

function reportView(ui) {
  const { Text } = ui
  const fs = features()
  const merged = fs.filter((f) => f.state === 'merged')
  const halted = fs.filter((f) => HALTED.includes(f.state))
  const waiting = fs.filter((f) => f.state === 'review' || f.state === 'built')
  const left = fs.filter((f) => f.state === 'not-started' || f.state === 'planning')
  const worst = ['blocked', 'exhausted', 'fork', 'paused'].find((s) => snap.counts[s])
  const state = worst || (merged.length === fs.length && fs.length ? 'done' : 'in progress')
  const out = [Text({ bold: true, color: worst ? 'red' : 'green', children: ['Run state: ' + state + ' — ' + merged.length + ' of ' + fs.length + ' merged'] })]
  if (halted.length) {
    out.push(Text({ bold: true, children: ['Stopped'] }))
    for (const f of halted) {
      const last = f.halts && f.halts[f.halts.length - 1]
      const why = f.state === 'paused' ? 'pause: ' + (f.current_task ? f.current_task.pause : '') : last ? last.note || last.title : ''
      out.push(line(ui, f, '  at ' + (f.current_task ? f.current_task.id : '?') + ' — ' + why))
    }
  }
  if (waiting.length) {
    out.push(Text({ bold: true, children: ['Built, not merged'] }))
    for (const f of waiting) out.push(line(ui, f, f.pr ? '  PR #' + f.pr.number : ''))
  }
  if (left.length) out.push(Text({ dimColor: true, children: ['Never started: ' + left.map((f) => f.slug).join(', ')] }))
  if (snap.cleanup.length) {
    out.push(Text({ bold: true, children: ['Worktree cleanup (yours to run)'] }))
    for (const c of snap.cleanup) out.push(Text({ dimColor: true, wrap: 'truncate-middle', children: [c.command] }))
  }
  return out
}

function explorerView(ui, redraw) {
  const { Text, Select } = ui
  const fs = features()
  if (!fs.length) return [Text({ dimColor: true, children: ['No features yet.'] })]
  if (!fs.find((f) => f.slug === picked)) picked = fs[0].slug
  const f = fs.find((x) => x.slug === picked)
  const out = [
    Select({
      key: 'feature', label: 'Feature', value: picked,
      options: fs.map((x) => ({ value: x.slug, label: MARK[x.state] + ' ' + x.title })),
      onSelect: (v) => { picked = v; redraw() },
    }),
    line(ui, f, f.ref ? '  from ' + f.ref : ''),
  ]
  if (f.reqs.length) {
    out.push(Text({ bold: true, children: ['Requirements'] }))
    for (const r of f.reqs) {
      const tasks = f.tasks.filter((t) => t.req.includes(r.id)).map((t) => (t.done ? '✓' : '○') + t.id)
      const cover = tasks.length ? tasks.join(' ') : f.tasks.length ? 'UNCOVERED' : ''
      // Omit color rather than pass undefined: a prop the element can't take voids the tree.
      const props = { wrap: 'truncate-end', children: [r.id + '  ' + r.text + '  ' + cover] }
      out.push(Text(tasks.length || !f.tasks.length ? props : { ...props, color: 'red' }))
    }
  }
  if (f.tasks.length) {
    out.push(Text({ bold: true, children: ['Tasks'] }))
    for (const t of f.tasks) {
      out.push(Text({ dimColor: t.done, wrap: 'truncate-end', children: [(t.done ? '✓ ' : '○ ') + t.id + ' ' + t.title + (t.pause ? '  [pause: ' + t.pause + ']' : '')] }))
    }
  }
  if (f.commits.length) out.push(Text({ dimColor: true, children: [f.commits.length + ' commit(s), last: ' + f.commits[0].subject] }))
  return out
}
