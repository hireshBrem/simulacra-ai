'use client'

import { useEffect, useRef } from 'react'
import { CANVAS_W, CANVAS_H } from '@/game/constants'

export default function PhaserGame() {
  const containerRef = useRef<HTMLDivElement>(null)
  const gameRef = useRef<import('phaser').Game | null>(null)

  useEffect(() => {
    if (gameRef.current || !containerRef.current) return

    let mounted = true

    const init = async () => {
      await document.fonts.ready
      if (!mounted) return

      const Phaser = (await import('phaser')).default
      if (!mounted) return

      const { SimScene } = await import('@/game/SimScene')
      if (!mounted) return

      const game = new Phaser.Game({
        type: Phaser.AUTO,
        width: CANVAS_W,
        height: CANVAS_H,
        backgroundColor: '#080810',
        scene: [SimScene],
        parent: containerRef.current!,
        pixelArt: true,
        antialias: false,
        roundPixels: true,
        render: {
          pixelArt: true,
          antialias: false,
          roundPixels: true,
        },
      })

      if (!mounted) {
        game.destroy(true)
        return
      }
      gameRef.current = game
    }

    init()

    return () => {
      mounted = false
      gameRef.current?.destroy(true)
      gameRef.current = null
    }
  }, [])

  return (
    <div
      ref={containerRef}
      className="w-full"
      style={{
        imageRendering: 'pixelated',
        aspectRatio: `${CANVAS_W} / ${CANVAS_H}`,
      }}
    />
  )
}
