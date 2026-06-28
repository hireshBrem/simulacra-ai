import Phaser from 'phaser'
import { simBus } from '@/lib/simBus'
import type { SimEvent } from '@/lib/simBus'
import {
  ZONES, AGENT_CONFIG, CANVAS_W, CANVAS_H,
  getAgentConfig, getZoneForAction,
} from './constants'

// ── Avatar ───────────────────────────────────────────────────────────────────

class Avatar {
  private scene: Phaser.Scene
  readonly agentId: string
  container: Phaser.GameObjects.Container
  private body: Phaser.GameObjects.Arc
  private highlight: Phaser.GameObjects.Arc
  private shadow: Phaser.GameObjects.Ellipse
  private nameLabel: Phaser.GameObjects.Text
  private moodLabel: Phaser.GameObjects.Text
  private bubble: Phaser.GameObjects.Container | null = null

  constructor(
    scene: Phaser.Scene,
    x: number, y: number,
    color: number,
    name: string,
    agentId: string,
  ) {
    this.scene = scene
    this.agentId = agentId

    this.shadow = scene.add.ellipse(0, 10, 26, 10, 0x000000, 0.35)
    this.body = scene.add.arc(0, 0, 13, 0, 360, false, color, 1)
    this.highlight = scene.add.arc(-4, -4, 4, 0, 360, false, 0xffffff, 0.2)

    this.nameLabel = scene.add.text(0, 18, name.split(' ')[0].toUpperCase(), {
      fontFamily: 'monospace',
      fontSize: '7px',
      color: '#aabbff',
      align: 'center',
    }).setOrigin(0.5, 0)

    this.moodLabel = scene.add.text(0, 28, '', {
      fontFamily: 'monospace',
      fontSize: '6px',
      color: '#556677',
      align: 'center',
    }).setOrigin(0.5, 0)

    this.container = scene.add.container(x, y, [
      this.shadow, this.body, this.highlight, this.nameLabel, this.moodLabel,
    ])
    this.container.setDepth(10)
  }

  walkTo(x: number, y: number, onComplete?: () => void) {
    this.clearBubble()
    // Kill existing tweens on this container (idle bob + any prior walk)
    this.scene.tweens.killTweensOf(this.container)
    this.scene.tweens.add({
      targets: this.container,
      x, y,
      duration: 1300,
      ease: 'Sine.easeInOut',
      onComplete: () => {
        // Resume idle bob after arriving
        const arrivedY = this.container.y
        this.scene.tweens.add({
          targets: this.container,
          y: arrivedY - 2,
          duration: 1100,
          yoyo: true,
          repeat: -1,
          ease: 'Sine.easeInOut',
        })
        onComplete?.()
      },
    })
  }

  setMood(mood: string) {
    this.moodLabel.setText(mood.toLowerCase())
  }

  pulse() {
    this.scene.tweens.add({
      targets: this.body,
      scaleX: 1.4, scaleY: 1.4,
      duration: 200,
      yoyo: true,
      ease: 'Sine.easeOut',
    })
  }

  showBubble(text: string, isThought: boolean, ttl = 5000) {
    this.clearBubble()

    const bw = 200
    const pad = 8
    const lineH = 13
    const fontSize = 9
    const charsPerLine = 28

    // Wrap text manually
    const words = text.split(' ')
    const lines: string[] = []
    let line = ''
    for (const w of words) {
      if ((line + ' ' + w).trim().length > charsPerLine) {
        if (line) lines.push(line.trim())
        line = w
      } else {
        line = (line + ' ' + w).trim()
      }
    }
    if (line) lines.push(line.trim())

    const maxLines = 3
    const shown = lines.slice(0, maxLines)
    if (lines.length > maxLines) shown[maxLines - 1] = shown[maxLines - 1].slice(0, -3) + '...'

    const bh = pad * 2 + shown.length * lineH
    const bx = -bw / 2
    const by = -(bh + 20)

    const gfx = this.scene.add.graphics()

    // Shadow
    gfx.fillStyle(0x000000, 0.4)
    gfx.fillRect(bx + 2, by + 2, bw, bh)

    // Body
    gfx.fillStyle(isThought ? 0x0d0d2a : 0xf0f0f5, 0.96)
    gfx.fillRect(bx, by, bw, bh)

    // Border (2px pixel-art style)
    gfx.lineStyle(2, isThought ? 0x3344aa : 0x999999, 1)
    gfx.strokeRect(bx, by, bw, bh)

    // Tail triangle
    gfx.fillStyle(isThought ? 0x0d0d2a : 0xf0f0f5, 0.96)
    gfx.fillTriangle(-5, by + bh, 5, by + bh, 0, by + bh + 10)
    gfx.lineStyle(2, isThought ? 0x3344aa : 0x999999, 1)
    gfx.strokeTriangle(-5, by + bh, 5, by + bh, 0, by + bh + 10)

    const textObj = this.scene.add.text(0, by + pad, shown.join('\n'), {
      fontFamily: 'monospace',
      fontSize: `${fontSize}px`,
      color: isThought ? '#7788cc' : '#111122',
      align: 'center',
      lineSpacing: 2,
    }).setOrigin(0.5, 0)

    const items: Phaser.GameObjects.GameObject[] = [gfx, textObj]

    if (isThought) {
      const icon = this.scene.add.text(bx + 4, by + 3, '🔒', { fontSize: '8px' })
      items.push(icon)
    }

    this.bubble = this.scene.add.container(0, 0, items)
    this.bubble.setDepth(20)
    this.container.add(this.bubble)

    if (ttl > 0) {
      this.scene.time.delayedCall(ttl, () => {
        if (!this.bubble) return
        this.scene.tweens.add({
          targets: this.bubble,
          alpha: 0,
          duration: 400,
          onComplete: () => this.clearBubble(),
        })
      })
    }
  }

  clearBubble() {
    if (this.bubble) {
      this.bubble.destroy(true)
      this.container.remove(this.bubble)
      this.bubble = null
    }
  }

  floatText(text: string, color = '#ffdd44') {
    const ft = this.scene.add.text(
      this.container.x, this.container.y - 20, text, {
        fontFamily: 'monospace',
        fontSize: '8px',
        color,
      },
    ).setOrigin(0.5).setDepth(30)

    this.scene.tweens.add({
      targets: ft,
      y: ft.y - 44,
      alpha: 0,
      duration: 2200,
      ease: 'Cubic.easeOut',
      onComplete: () => ft.destroy(),
    })
  }

  destroy() {
    this.clearBubble()
    this.container.destroy()
  }
}

// ── SimScene ─────────────────────────────────────────────────────────────────

export class SimScene extends Phaser.Scene {
  private avatars: Record<string, Avatar> = {}
  private avatarZones: Record<string, string> = {}
  private simHandler!: (e: SimEvent) => void
  private worldBannerBg!: Phaser.GameObjects.Rectangle
  private worldBannerText!: Phaser.GameObjects.Text
  private bannerTween: Phaser.Tweens.Tween | null = null

  constructor() {
    super('SimScene')
  }

  create() {
    this.drawBackground()
    this.drawZones()
    this.drawSectionHeaders()
    this.drawPaths()
    this.createAvatars()
    this.createWorldBanner()

    this.simHandler = (e: SimEvent) => this.handleSimEvent(e)
    simBus.on('sim', this.simHandler)
  }

  shutdown() {
    simBus.off('sim', this.simHandler)
  }

  // ── Map drawing ────────────────────────────────────────────────────────────

  private drawBackground() {
    const g = this.add.graphics()
    g.fillStyle(0x080810, 1)
    g.fillRect(0, 0, CANVAS_W, CANVAS_H)

    // Subtle grid
    g.lineStyle(1, 0x111120, 0.8)
    for (let x = 0; x < CANVAS_W; x += 32) {
      g.beginPath(); g.moveTo(x, 0); g.lineTo(x, CANVAS_H); g.strokePath()
    }
    for (let y = 0; y < CANVAS_H; y += 32) {
      g.beginPath(); g.moveTo(0, y); g.lineTo(CANVAS_W, y); g.strokePath()
    }
  }

  private drawZones() {
    const g = this.add.graphics()

    for (const zone of Object.values(ZONES)) {
      // Fill
      g.fillStyle(zone.fillColor, 1)
      g.fillRect(zone.x, zone.y, zone.w, zone.h)

      // 2px border
      g.lineStyle(2, zone.borderColor, 1)
      g.strokeRect(zone.x, zone.y, zone.w, zone.h)

      // Corner accents
      g.fillStyle(zone.borderColor, 1)
      const corners = [
        [zone.x, zone.y],
        [zone.x + zone.w - 4, zone.y],
        [zone.x, zone.y + zone.h - 4],
        [zone.x + zone.w - 4, zone.y + zone.h - 4],
      ] as const
      for (const [cx, cy] of corners) g.fillRect(cx, cy, 4, 4)

      // Label
      this.add.text(zone.x + 8, zone.y + 6, zone.label, {
        fontFamily: 'monospace',
        fontSize: '7px',
        color: zone.textColor,
      }).setAlpha(0.9)
    }
  }

  private drawSectionHeaders() {
    const headers = [
      { label: 'WEST + NORTH', x: 130, color: '#69b7d6' },
      { label: 'CIVIC COMMONS', x: 480, color: '#77d8a2' },
      { label: 'SOUTHEAST + SERVICE', x: 830, color: '#94dfad' },
    ]
    for (const h of headers) {
      this.add.text(h.x, 24, h.label, {
        fontFamily: 'monospace',
        fontSize: '8px',
        color: h.color,
      }).setOrigin(0.5).setAlpha(0.7)
    }

    // Vertical dividers
    const dg = this.add.graphics()
    dg.lineStyle(1, 0x222244, 1)
    dg.beginPath(); dg.moveTo(320, 15); dg.lineTo(320, 360); dg.strokePath()
    dg.beginPath(); dg.moveTo(640, 15); dg.lineTo(640, 360); dg.strokePath()
  }

  private drawPaths() {
    // Subtle pathways between zones
    const g = this.add.graphics()
    g.fillStyle(0x0e0e1e, 1)
    g.fillRect(244, 100, 126, 20)
    g.fillRect(244, 260, 126, 20)
    g.fillRect(590, 100, 130, 20)
    g.fillRect(590, 260, 130, 20)
    g.fillRect(444, 164, 72, 46)
    g.fillRect(404, 340, 152, 40)

    // Senate path up
    g.fillRect(454, 330, 52, 50)
  }

  // ── Avatars ────────────────────────────────────────────────────────────────

  private createAvatars() {
    const zoneCounts: Record<string, number> = {}
    for (const [agentId, cfg] of Object.entries(AGENT_CONFIG)) {
      const slot = zoneCounts[cfg.homeZone] ?? 0
      zoneCounts[cfg.homeZone] = slot + 1
      const { x, y } = this.slotPosition(cfg.homeZone, slot)
      const av = new Avatar(
        this,
        x,
        y,
        cfg.color,
        cfg.name,
        agentId,
      )
      this.avatars[agentId] = av
      this.avatarZones[agentId] = cfg.homeZone

      // Gentle idle bob using a looping tween
      const startY = av.container.y
      this.tweens.add({
        targets: av.container,
        y: startY - 2,
        duration: 1100 + Math.random() * 300,
        yoyo: true,
        repeat: -1,
        ease: 'Sine.easeInOut',
      })
    }
  }

  private slotPosition(zoneKey: string, slot: number) {
    const zone = ZONES[zoneKey]
    const cols = zone.w >= 280 ? 5 : 4
    const col = slot % cols
    const row = Math.floor(slot / cols)
    const x = zone.x + 34 + col * 46
    const y = zone.y + 34 + row * 36
    return {
      x: Math.min(x, zone.x + zone.w - 28),
      y: Math.min(y, zone.y + zone.h - 28),
    }
  }

  private ensureAvatar(agentId: string, name?: string): Avatar {
    const existing = this.avatars[agentId]
    if (existing) return existing

    const cfg = getAgentConfig(agentId, name)
    const av = new Avatar(
      this,
      this.slotPosition(cfg.homeZone, 0).x,
      this.slotPosition(cfg.homeZone, 0).y,
      cfg.color,
      cfg.name,
      agentId,
    )
    this.avatars[agentId] = av
    this.avatarZones[agentId] = cfg.homeZone
    return av
  }

  private agentSortKey(agentId: string): number {
    const numeric = Number(agentId.replace('agent-', ''))
    return Number.isFinite(numeric) ? numeric : Number.MAX_SAFE_INTEGER
  }

  private moveAvatarToZone(
    agentId: string,
    name: string | undefined,
    zoneKey: string,
    onComplete?: () => void,
  ) {
    this.ensureAvatar(agentId, name)
    this.avatarZones[agentId] = zoneKey

    const occupants = Object.entries(this.avatarZones)
      .filter(([, currentZone]) => currentZone === zoneKey)
      .map(([currentAgentId]) => currentAgentId)
      .sort((a, b) => this.agentSortKey(a) - this.agentSortKey(b) || a.localeCompare(b))

    for (const [slot, occupantId] of occupants.entries()) {
      const occupant = this.avatars[occupantId]
      if (!occupant) continue

      const position = this.slotPosition(zoneKey, slot)
      occupant.walkTo(
        position.x,
        position.y,
        occupantId === agentId ? onComplete : undefined,
      )
    }
  }

  // ── World banner ───────────────────────────────────────────────────────────

  private createWorldBanner() {
    this.worldBannerBg = this.add.rectangle(CANVAS_W / 2, CANVAS_H - 24, CANVAS_W - 20, 30, 0x0a0a1a, 0.9)
      .setStrokeStyle(1, 0x222255)
      .setDepth(25)
      .setAlpha(0)

    this.worldBannerText = this.add.text(CANVAS_W / 2, CANVAS_H - 24, '', {
      fontFamily: 'monospace',
      fontSize: '9px',
      color: '#8899ff',
    }).setOrigin(0.5).setDepth(26).setAlpha(0)
  }

  private showWorldBanner(content: string) {
    const short = content.length > 110 ? content.slice(0, 107) + '...' : content
    this.worldBannerText.setText(`⚡ ${short}`)
    this.bannerTween?.stop()

    this.worldBannerBg.setAlpha(1)
    this.worldBannerText.setAlpha(1)
  }

  // ── SimBus handler ─────────────────────────────────────────────────────────

  private handleSimEvent(e: SimEvent) {
    switch (e.type) {
      case 'simulation_started': {
        this.showWorldBanner('LIVE SF SIMULATION STARTED')
        break
      }

      case 'simulation_stopped': {
        this.showWorldBanner(`LIVE SF SIMULATION STOPPED AFTER ${e.ticks_run} TICKS`)
        break
      }

      case 'tick_started': {
        this.showWorldBanner(`STEP ${e.step} / ${e.current_time}`)
        break
      }

      case 'world_event': {
        this.showWorldBanner(e.content)
        // Flash effect across background
        this.cameras.main.flash(300, 20, 30, 60, false)
        break
      }

      case 'agent_thinking': {
        this.ensureAvatar(e.agent_id, e.agent_name)
        const homeZone = getAgentConfig(e.agent_id, e.agent_name).homeZone
        this.moveAvatarToZone(e.agent_id, e.agent_name, homeZone)
        const av = this.avatars[e.agent_id]
        av.showBubble('...', true, 3000)
        break
      }

      case 'agent_action': {
        this.ensureAvatar(e.agent_id, e.agent_name)
        const targetZone = getZoneForAction(e.agent_id, e.action_type)
        this.moveAvatarToZone(e.agent_id, e.agent_name, targetZone, () => {
          const av = this.avatars[e.agent_id]
          av.pulse()
          const label = `[${e.action_type.replace('_', ' ')}]\n${e.public_action}`
          av.showBubble(label, false, 6000)
          av.setMood(e.emotional_state)
        })
        break
      }

      case 'agent_observed': {
        const av = this.ensureAvatar(e.agent_id, e.agent_name)
        av.showBubble('...', true, 1800)
        break
      }

      case 'agent_planned': {
        const av = this.ensureAvatar(e.agent_id, e.agent_name)
        av.setMood(e.emotional_state)
        if (e.inner_monologue) av.showBubble(e.inner_monologue, true, 3000)
        break
      }

      case 'agent_moved': {
        this.moveAvatarToZone(e.agent_id, e.agent_name, e.to_zone, () => {
          const av = this.avatars[e.agent_id]
          av.pulse()
          av.setMood(e.emotional_state)
          av.showBubble(e.activity, false, 4000)
        })
        break
      }

      case 'encounter_start': {
        const [p1, p2] = e.participants
        this.moveAvatarToZone(p1.agent_id, p1.name, 'transit_commons')
        this.moveAvatarToZone(p2.agent_id, p2.name, 'transit_commons')
        this.showWorldBanner(`ENCOUNTER: ${e.topic}`)
        break
      }

      case 'agent_utterance': {
        const av = this.ensureAvatar(e.speaker_id, e.speaker_name)
        av.pulse()
        av.showBubble(e.utterance, false, 6000)
        break
      }

      case 'memory_saved': {
        this.ensureAvatar(e.agent_id, e.agent_name).floatText('+MEMORY', '#44ffaa')
        break
      }

      case 'reflection_saved': {
        this.ensureAvatar(e.agent_id, e.agent_name).floatText('+REFLECTION', '#44ffaa')
        break
      }

      case 'encounter_end': {
        for (const participant of e.participants) {
          this.ensureAvatar(participant.agent_id, participant.name).floatText('END', '#ffaa44')
        }
        break
      }

      case 'done': {
        // Fade banner after a short pause
        this.time.delayedCall(3000, () => {
          this.bannerTween = this.tweens.add({
            targets: [this.worldBannerBg, this.worldBannerText],
            alpha: 0, duration: 800,
          })
        })
        break
      }
    }
  }

}
