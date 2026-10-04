import type { MetadataRoute } from 'next'

export default function sitemap(): MetadataRoute.Sitemap {
  return [
    {
      url: 'https://symcomp.ime.usp.br/semana',
    },
    {
      url: 'https://symcomp.ime.usp.br/semana/cronograma',
    },
    {
      url: 'https://symcomp.ime.usp.br/semana/desafios',
    },
    {
      url: 'https://symcomp.ime.usp.br/semana/ranking',
    },
    {
      url: 'https://symcomp.ime.usp.br/semana/patrocinadores',
    },
    {
      url: 'https://symcomp.ime.usp.br/semana/sobre-nos',
    },
    {
      url: 'https://symcomp.ime.usp.br/semana/privacy',
    },
    {
      url: 'https://symcomp.ime.usp.br/bytecafe',
    },
  ]
}
