import * as React from 'react'

import { Input } from '@/components/ui/input'
import { cn } from '@/lib/utils'

export const SemanaInput = React.forwardRef<
  HTMLInputElement,
  React.ComponentProps<'input'>
>(({ className, ...props }, ref) => (
  <Input
    className={cn(
      'h-12 rounded-none border-[5px] border-[hsl(var(--semana-contrast))] bg-white px-3 font-[family-name:var(--font-semana-body)] text-lg text-[hsl(var(--semana-contrast))] placeholder:text-[hsl(var(--semana-contrast))]/50 focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-background',
      className,
    )}
    ref={ref}
    {...props}
  />
))

SemanaInput.displayName = 'SemanaInput'
