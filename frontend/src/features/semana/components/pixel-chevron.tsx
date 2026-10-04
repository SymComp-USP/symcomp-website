import type { SVGProps } from 'react'

// Pixel-art chevron from the sponsors design: three pixels thick with a
// single-pixel tip. Points right; use direction="left" to mirror it.
const rows = [0, 1, 2, 3, 4, 3, 2, 1, 0]

export function PixelChevron({
  direction = 'right',
  ...props
}: SVGProps<SVGSVGElement> & { direction?: 'left' | 'right' }) {
  return (
    <svg
      aria-hidden="true"
      fill="currentColor"
      shapeRendering="crispEdges"
      viewBox="0 0 7 9"
      xmlns="http://www.w3.org/2000/svg"
      {...props}
    >
      <g transform={direction === 'left' ? 'matrix(-1 0 0 1 7 0)' : undefined}>
        {rows.map((x, y) => (
          <rect height="1" key={y} width="3" x={x} y={y} />
        ))}
      </g>
    </svg>
  )
}
