// Patrocinadores exibidos em /semana/patrocinadores.
//
// Como editar:
// - Para adicionar um patrocinador, copie um item da lista e ajuste os campos.
//   Para remover, apague o item. Com a lista vazia, a página mostra
//   "Patrocinadores em breve.".
// - As logos ficam em public/semana/2026/sponsors/. Prefira ícones quadrados:
//   eles aparecem dentro de um selo branco. Informe as dimensões reais do
//   arquivo (width e height, em pixels).
// - `sobre` é opcional: um texto curto sobre a empresa, exibido no
//   "Saber mais +". Sem ele, o popup mostra só a logo, o nome e o site.

export type Sponsor = {
  nome: string
  logo: { src: string; width: number; height: number }
  site?: string
  cota?: string
  sobre?: string
}

export const sponsors: Sponsor[] = [
  {
    nome: 'Incognia',
    logo: { src: '/semana/2026/sponsors/incognia.png', width: 268, height: 268 },
    site: 'https://www.incognia.com/pt/',
    cota: 'GIGA+',
    sobre:
      'A Incognia é uma plataforma de inteligência de risco baseada em IA que usa a localização como identidade para reconhecer usuários legítimos e barrar fraudadores. Ela ajuda empresas de delivery, marketplaces, redes sociais e serviços financeiros a prevenir fraudes em contas, cupons e pagamentos, e conta com clientes como iFood, Banco Pan e Stone.',
  },
  {
    nome: 'Tako',
    logo: { src: '/semana/2026/sponsors/tako.jpeg', width: 200, height: 200 },
    site: 'https://tako.ai/pt/',
    cota: 'GIGA+',
    sobre:
      'A Tako é uma empresa brasileira de tecnologia para RH que usa inteligência artificial em todo o ciclo de vida do colaborador. Sua plataforma automatiza folha de pagamento, gestão de pessoas e conformidade trabalhista, e o Tako Recruiter conduz entrevistas e triagem de candidatos com IA.',
  },
  {
    nome: 'Asper',
    logo: { src: '/semana/2026/sponsors/asper.jpeg', width: 200, height: 200 },
    site: 'https://www.asper.tec.br/',
    cota: 'GIGA+',
    sobre:
      'A Asper atua em segurança cibernética e oferece serviços gerenciados de segurança para proteger o ambiente digital das empresas, permitindo que seus clientes se concentrem no próprio negócio.',
  },
]
