// Patrocinadores exibidos em /semana/patrocinadores.
//
// Como editar:
// - Para adicionar um patrocinador, copie um item da lista e ajuste os campos.
//   Para remover, apague o item. Com a lista vazia, a página mostra
//   "Patrocinadores em breve.".
// - As logos ficam em public/company-logos/. Informe o caminho e as dimensões
//   reais do arquivo (width e height, em pixels).
// - `palestra` é opcional. Sem ela, o "Saber mais +" mostra só a empresa, sem
//   as abas Palestra e Palestrante.
// - Datas no formato AAAA-MM-DD e horários no formato "HH:MM - HH:MM", no
//   horário de Brasília.

export type SponsorTalk = {
  titulo: string
  data: string
  horario: string
  descricao: string
  palestrante: string
  sobre: string
}

export type Sponsor = {
  nome: string
  logo: { src: string; width: number; height: number }
  site?: string
  cota?: string
  descricao?: string
  palestra?: SponsorTalk
}

export const sponsors: Sponsor[] = [
  {
    nome: 'Incognia',
    logo: { src: '/company-logos/incognia.webp', width: 848, height: 158 },
    site: 'https://www.incognia.com/pt/',
    cota: 'GIGA+',
    // TODO: dados provisórios
    palestra: {
      titulo: 'Palestra Incognia',
      data: '2026-10-05',
      horario: '14:00 - 15:00',
      descricao: 'Detalhes da palestra em breve.',
      palestrante: 'A confirmar',
      sobre: 'Informações sobre o palestrante em breve.',
    },
  },
  {
    nome: 'Tako',
    logo: { src: '/company-logos/tako_logotipo.svg', width: 791, height: 207 },
    site: 'https://tako.ai/pt/',
    cota: 'GIGA+',
    // TODO: dados provisórios
    palestra: {
      titulo: 'Palestra Tako',
      data: '2026-10-06',
      horario: '14:00 - 15:00',
      descricao: 'Detalhes da palestra em breve.',
      palestrante: 'A confirmar',
      sobre: 'Informações sobre o palestrante em breve.',
    },
  },
  {
    nome: 'Asper',
    logo: { src: '/company-logos/colored-1.webp', width: 2500, height: 592 },
    site: 'https://www.asper.tec.br/',
    cota: 'GIGA+',
    // TODO: dados provisórios
    palestra: {
      titulo: 'Palestra Asper',
      data: '2026-10-07',
      horario: '14:00 - 15:00',
      descricao: 'Detalhes da palestra em breve.',
      palestrante: 'A confirmar',
      sobre: 'Informações sobre o palestrante em breve.',
    },
  },
]
