import type { Activity } from '../types'

export const mockSchedule: Activity[] = [
  {
    uid: 'programacao-01',
    type: 'talk',
    title: 'Construindo tecnologia com impacto',
    description:
      'Uma conversa sobre escolhas técnicas, colaboração e os caminhos entre a universidade e o mercado.',
    speakers: [
      { name: 'Marina Silva', bio: 'Engenheira de software e ex-aluna do IME-USP.' },
    ],
    startsAt: '2026-10-19T13:00:00-03:00',
    endsAt: '2026-10-19T14:00:00-03:00',
    location: 'Auditório Jacy Monteiro',
  },
  {
    uid: 'programacao-02',
    type: 'coffee_break',
    title: 'Coffee break',
    speakers: [],
    startsAt: '2026-10-19T14:00:00-03:00',
    endsAt: '2026-10-19T14:30:00-03:00',
    location: 'Saguão do Bloco B',
  },
  {
    uid: 'programacao-03',
    type: 'conversation',
    title: 'Pesquisa em computação: por onde começar?',
    description:
      'Pesquisadores compartilham experiências de iniciação científica, pós-graduação e carreira acadêmica.',
    speakers: [{ name: 'Rafael Costa' }, { name: 'Ana Pereira' }],
    startsAt: '2026-10-19T14:30:00-03:00',
    endsAt: '2026-10-19T15:30:00-03:00',
    location: 'Auditório Jacy Monteiro',
  },
  {
    uid: 'programacao-04',
    type: 'talk',
    title: 'Inteligência artificial além do hype',
    description:
      'Fundamentos, limitações e decisões responsáveis ao colocar modelos de IA em produção.',
    speakers: [{ name: 'Beatriz Almeida' }],
    startsAt: '2026-10-20T13:00:00-03:00',
    endsAt: '2026-10-20T14:00:00-03:00',
    location: 'Auditório Jacy Monteiro',
  },
  {
    uid: 'programacao-05',
    type: 'closing',
    title: 'Encerramento e próximos passos',
    speakers: [{ name: 'Equipe SymComp' }],
    startsAt: '2026-10-20T17:00:00-03:00',
    endsAt: '2026-10-20T17:30:00-03:00',
    location: 'Auditório Jacy Monteiro',
  },
]
