import { redirect } from 'next/navigation'

export default function Semana() {
  // TODO: Remove this redirect when /semana becomes the public preview page.
  // The other Semana routes must also be disabled before deploying that WIP preview.
  redirect('/semana/inicio')
}
