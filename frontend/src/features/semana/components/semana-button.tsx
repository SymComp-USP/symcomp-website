import { Button, type ButtonProps } from '@/components/ui/button'
import { cn } from '@/lib/utils'

export function SemanaButton({ className, ...props }: ButtonProps) {
  return (
    <Button
      className={cn(
        'h-auto rounded-none border-[6px] border-[hsl(var(--semana-contrast))] bg-white px-6 py-3 font-[family-name:var(--font-semana-display)] font-bold uppercase text-[hsl(var(--semana-contrast))] shadow-[0_7px_0_hsl(var(--semana-contrast))] transition-transform hover:-translate-y-0.5 hover:bg-[hsl(var(--semana-accent))] active:translate-y-1 active:shadow-[0_3px_0_hsl(var(--semana-contrast))]',
        className,
      )}
      {...props}
    />
  )
}
