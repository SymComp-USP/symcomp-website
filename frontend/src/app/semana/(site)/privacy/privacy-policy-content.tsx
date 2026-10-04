import type { ReactNode } from 'react'

function Section({ title, children }: Readonly<{ title: string; children: ReactNode }>) {
  return (
    <section className="space-y-3">
      <h2 className="text-2xl font-semibold">{title}</h2>
      {children}
    </section>
  )
}

export function PrivacyPolicyContent() {
  return (
    <>
      <Section title="Política de Privacidade completa">
        <p>
          Conheça a política de privacidade do https://symcomp.ime.usp.br. Esta política
          ajudará você a entender quais dados coletamos, por que os coletamos e quais são
          seus direitos em relação a eles.
        </p>
        <p>Última atualização: 4 de outubro de 2026.</p>
      </Section>

      <Section title="Proprietário e Controlador de Dados">
        <p>Simpósio da Computação</p>
        <p>
          R. do Matão, 1010 - Bloco B - Butantã
          <br />
          São Paulo - SP, 05508-090
        </p>
        <p>
          E-mail de contato do Proprietário:{' '}
          <a
            className="underline underline-offset-4"
            href="mailto:semanadacomputacao@ime.usp.br"
          >
            semanadacomputacao@ime.usp.br
          </a>
        </p>
      </Section>

      <Section title="Tipos de Dados coletados">
        <p>
          Entre os tipos de Dados Pessoais que este Aplicativo coleta, por si mesmo ou
          através de terceiros, existem: e-mail e senha.
        </p>
        <p>
          Detalhes completos sobre cada tipo de Dados Pessoais coletados são fornecidos
          nas seções dedicadas desta política de privacidade ou por textos explicativos
          específicos exibidos antes da coleta de Dados.
        </p>
        <p>
          Os Dados Pessoais poderão ser fornecidos livremente pelo Usuário, ou, no caso
          dos Dados de Utilização, coletados automaticamente ao se utilizar este
          Aplicativo.
        </p>
        <p>
          A menos que especificado diferentemente, todos os Dados solicitados por este
          Aplicativo são obrigatórios e a falta de fornecimento destes Dados poderá
          impossibilitar este Aplicativo de fornecer os seus Serviços. Nos casos em que
          este Aplicativo afirmar especificamente que alguns Dados não forem obrigatórios,
          os Usuários ficam livres para deixarem de comunicar estes Dados sem nenhuma
          consequência para a disponibilidade ou o funcionamento do Serviço.
        </p>
        <p>
          Os Usuários que tiverem dúvidas a respeito de quais Dados Pessoais são
          obrigatórios estão convidados a entrar em contato com o Proprietário.
        </p>
        <p>
          Quaisquer usos de cookies – ou de outras ferramentas de rastreamento – por este
          Aplicativo ou pelos proprietários de serviços terceiros utilizados por este
          Aplicativo serão para a finalidade de fornecer os Serviços solicitados pelo
          Usuário, além das demais finalidades descritas neste documento e na Política de
          Cookies.
        </p>
        <p>
          Os Usuários ficam responsáveis por quaisquer Dados Pessoais de terceiros que
          forem obtidos, publicados ou compartilhados através deste Serviço (este
          Aplicativo).
        </p>
      </Section>

      <Section title="Modo e local de processamento dos Dados">
        <h3 className="text-xl font-semibold">Método de processamento</h3>
        <p>
          O Proprietário tomará as medidas de segurança adequadas para impedir o acesso
          não autorizado, divulgação, alteração ou destruição não autorizada dos Dados.
        </p>
        <p>
          O processamento dos Dados é realizado utilizando computadores e/ou ferramentas
          de TI habilitadas, seguindo procedimentos organizacionais e meios estritamente
          relacionados com os fins indicados. Além do Proprietário, em alguns casos, os
          Dados podem ser acessados por pessoas encarregadas da operação deste Serviço,
          como administração, vendas, marketing e administração legal do sistema, ou por
          pessoas externas, como fornecedores de serviços técnicos, provedores de
          hospedagem, empresas de TI e agências de comunicação, nomeadas quando necessário
          como Processadores de Dados. A lista atualizada destas partes pode ser
          solicitada ao Proprietário a qualquer momento.
        </p>
        <h3 className="text-xl font-semibold">Lugar</h3>
        <p>
          Os dados são processados nas sedes de operação dos Proprietários e em quaisquer
          outros lugares onde as partes envolvidas com o processamento estiverem
          localizadas. Dependendo da localização do Usuário, as transferências poderão
          envolver outro país.
        </p>
        <h3 className="text-xl font-semibold">Período de conservação</h3>
        <p>
          Salvo especificação em contrário neste documento, os Dados Pessoais serão
          tratados e armazenados pelo tempo necessário para as finalidades para as quais
          foram coletados e poderão ser retidos por mais tempo em razão de obrigação legal
          aplicável ou com base no consentimento dos Usuários.
        </p>
      </Section>

      <Section title="As finalidades do processamento">
        <p>
          Os Dados relativos ao Usuário são coletados para permitir que o Proprietário
          preste seu Serviço, cumpra suas obrigações legais, responda a solicitações de
          execução, proteja seus direitos e interesses (ou aqueles de seus Usuários ou
          terceiros), detecte atividade maliciosa ou fraudulenta, bem como para registro e
          autenticação.
        </p>
      </Section>

      <Section title="Informações detalhadas sobre o processamento de Dados Pessoais">
        <h3 className="text-xl font-semibold">Registro e autenticação</h3>
        <p>
          Ao se registrar ou autenticar, os Usuários permitem a este serviço
          identificá-los e dar-lhes acesso a serviços dedicados. Os serviços podem ser
          fornecidos por terceiros; neste caso, o Aplicativo poderá acessar alguns Dados
          armazenados por estes serviços para fins de registro ou identificação. Alguns
          serviços também podem coletar Dados Pessoais para fins de direcionamento e
          perfil.
        </p>
        <h3 className="text-xl font-semibold">Google OAuth</h3>
        <p>
          Companhia: Google Ireland Limited.
          <br />
          Lugar de processamento: Irlanda.
          <br />
          Dados Pessoais processados: vários tipos de Dados como especificados na política
          de privacidade do serviço.
        </p>
        <h3 className="text-xl font-semibold">GitHub OAuth</h3>
        <p>
          Companhia: GitHub Inc.
          <br />
          Lugar de processamento: EUA.
          <br />
          Dados Pessoais processados: vários tipos de Dados como especificados na política
          de privacidade do serviço.
        </p>
        <h3 className="text-xl font-semibold">
          Registro e autenticação fornecidos diretamente por este Aplicativo
        </h3>
        <p>
          Os Dados Pessoais são coletados e armazenados somente para fins de registro ou
          identificação. Os Dados coletados são somente aqueles necessários para a
          prestação do serviço solicitado pelos Usuários.
        </p>
        <h3 className="text-xl font-semibold">Registro direto</h3>
        <p>Dados Pessoais processados: e-mail +1.</p>
      </Section>

      <Section title="Informações adicionais para Usuários no Brasil">
        <h3 className="text-xl font-semibold">
          Em que nos embasamos para processar suas informações pessoais
        </h3>
        <p>
          Podemos processar suas informações pessoais somente se tivermos uma base legal.
          As bases legais são: sua anuência; conformidade com obrigação legal ou
          regulamentar; cumprimento de políticas públicas; estudos conduzidos por
          entidades de pesquisa, preferivelmente com informações anônimas; execução de
          contrato e procedimentos preliminares; exercício de direitos em processos
          judiciais, administrativos ou de arbitragem; proteção da vida, segurança física
          ou saúde; interesses legítimos; e proteção ao crédito.
        </p>
        <p>
          Para saber mais sobre as bases legais, entre em contato conosco pelos dados
          deste documento.
        </p>
        <h3 className="text-xl font-semibold">Categorias e finalidades</h3>
        <p>
          As categorias de informações pessoais processadas estão na seção “Informações
          detalhadas sobre o processamento de Dados Pessoais”. As finalidades estão na
          seção “As finalidades do processamento”.
        </p>
        <h3 className="text-xl font-semibold">
          Seus direitos de privacidade como brasileiro
        </h3>
        <p>Você tem o direito de:</p>
        <ul className="list-disc space-y-2 pl-6">
          <li>
            obter confirmação sobre a existência de tratamento e acesso a seus dados;
          </li>
          <li>corrigir informações incompletas, inexatas ou desatualizadas;</li>
          <li>
            obter anonimização, bloqueio ou eliminação de dados desnecessários, excessivos
            ou tratados em desacordo com a LGPD;
          </li>
          <li>
            obter informações sobre consentimento, suas consequências e compartilhamentos;
          </li>
          <li>
            obter portabilidade, mediante solicitação expressa, respeitados segredos
            comerciais e industriais;
          </li>
          <li>
            obter exclusão de dados tratados com consentimento, salvo exceções do art. 16
            da LGPD, e retirar o consentimento a qualquer momento;
          </li>
          <li>
            reclamar à ANPD ou órgãos de defesa do consumidor, opor-se a tratamento
            irregular e solicitar informações, critérios, procedimentos e revisão de
            decisões automatizadas.
          </li>
        </ul>
        <p>Você não será discriminado nem sofrerá prejuízo por exercer esses direitos.</p>
        <h3 className="text-xl font-semibold">
          Como registrar e receber resposta à solicitação
        </h3>
        <p>
          Você poderá registrar gratuitamente, a qualquer momento, uma solicitação
          expressa para exercer seus direitos, usando os dados de contato deste documento
          ou por representante legal.
        </p>
        <p>
          Faremos o possível para responder imediatamente. Se não for possível,
          comunicaremos os motivos de fato ou de direito. Para pedidos de acesso ou
          confirmação, informe se deseja formato eletrônico ou impresso e resposta
          simplificada ou completa. A resposta completa será fornecida em até 15 dias,
          incluindo origem, confirmação de registros, critérios e finalidades, preservados
          os segredos comerciais e industriais.
        </p>
        <p>
          Quando solicitado, comunicaremos retificação, exclusão, anonimização ou bloqueio
          às partes com quem compartilhamos os dados, exceto se impossível ou
          desproporcional.
        </p>
        <h3 className="text-xl font-semibold">
          Transferência de informações pessoais para fora do Brasil
        </h3>
        <p>
          Podemos transferir informações para fora do Brasil quando permitido por lei,
          inclusive para cooperação jurídica internacional, proteção da vida ou segurança,
          autorização da ANPD, acordo de cooperação internacional, política pública,
          obrigação legal ou regulamentar, execução de contrato ou exercício regular de
          direitos.
        </p>
      </Section>

      <Section title="Informações adicionais sobre a coleta e processamento de Dados">
        <h3 className="text-xl font-semibold">Ação jurídica</h3>
        <p>
          Os Dados Pessoais podem ser utilizados para fins jurídicos pelo Proprietário em
          juízo ou nas etapas conducentes à possível ação jurídica decorrente de uso
          indevido deste Serviço ou dos Serviços relacionados. O Proprietário poderá ser
          obrigado a revelar Dados Pessoais mediante solicitação de autoridades
          governamentais.
        </p>
        <h3 className="text-xl font-semibold">Informações adicionais e logs</h3>
        <p>
          Além desta política, o Aplicativo poderá fornecer informações adicionais e
          contextuais sobre serviços específicos ou coleta e processamento de Dados
          Pessoais mediante solicitação. Para operação e manutenção, o Aplicativo e
          terceiros poderão coletar logs do sistema e usar outros Dados Pessoais, como
          endereço IP.
        </p>
        <h3 className="text-xl font-semibold">Mudanças nesta política</h3>
        <p>
          O Proprietário pode alterar esta política a qualquer momento, notificando os
          Usuários nesta página, dentro do Serviço e, quando técnica e juridicamente
          viável, pelos dados de contato disponíveis. Recomendamos consultar esta página
          regularmente. Se mudanças afetarem tratamentos baseados em consentimento,
          coletaremos nova anuência quando exigida.
        </p>
      </Section>

      <Section title="Definições e referências jurídicas">
        <h3 className="text-xl font-semibold">Dados Pessoais (ou Dados)</h3>
        <p>
          Quaisquer informações que diretamente, indiretamente ou em relação com outras
          informações – incluindo número de identificação pessoal – permitam identificar
          ou tornar identificável uma pessoa física.
        </p>
        <h3 className="text-xl font-semibold">Dados de Uso</h3>
        <p>
          Informações coletadas automaticamente, como endereços IP ou nomes de domínio,
          URI, data e hora, método do pedido, tamanho e status da resposta, país de
          origem, características do navegador e sistema operacional, tempo por visita,
          páginas visitadas e parâmetros do dispositivo e ambiente de TI.
        </p>
        <h3 className="text-xl font-semibold">Usuário e Titular dos Dados</h3>
        <p>
          Usuário é a pessoa que usa este Aplicativo e, salvo especificação diferente,
          coincide com o Titular dos Dados: a pessoa física a quem os Dados Pessoais se
          referem.
        </p>
        <h3 className="text-xl font-semibold">Processador e Controlador de Dados</h3>
        <p>
          Processador é a pessoa física ou jurídica, administração pública, agência ou
          órgão que processa Dados Pessoais em nome do Controlador. Controlador é quem
          determina as finalidades e meios do processamento, incluindo medidas de
          segurança; salvo indicação diferente, é o Proprietário deste Aplicativo.
        </p>
        <h3 className="text-xl font-semibold">
          Este Aplicativo, Serviço e informação jurídica
        </h3>
        <p>
          Este Aplicativo é o meio pelo qual Dados Pessoais são coletados e processados.
          Serviço é o serviço fornecido por este Aplicativo conforme termos relativos, se
          disponíveis, neste site. Esta política se refere somente a este Aplicativo, se
          não afirmado diferentemente.
        </p>
      </Section>

      <Section title="Política de Cookies completa">
        <p>
          Este documento informa os Usuários sobre as tecnologias que ajudam este
          Aplicativo a alcançar as finalidades descritas abaixo. Essas tecnologias
          permitem ao Proprietário acessar e armazenar informações, por exemplo usando um
          Cookie, ou usar recursos, por exemplo executando um script, em um dispositivo
          enquanto os Usuários interagem com este Aplicativo.
        </p>
        <p>
          Para fins de simplicidade, todas essas tecnologias são definidas como
          “Rastreadores”, salvo quando houver motivo para diferenciá-las. Cookies podem
          ser usados em navegadores web e dispositivos móveis; o termo Cookie é empregado
          aqui apenas quando indicar esse tipo específico de Rastreador.
        </p>
        <p>
          Algumas finalidades podem exigir permissão do Usuário. Quando dada, essa
          permissão pode ser retirada livremente a qualquer momento seguindo as instruções
          deste documento.
        </p>
        <p>
          Este Aplicativo usa apenas Rastreadores gerenciados diretamente pelo
          Proprietário, conhecidos como Rastreadores próprios. A validade e expiração
          podem variar; alguns expiram ao término da sessão de navegação.
        </p>
        <h3 className="text-xl font-semibold">Como este Aplicativo usa Rastreadores</h3>
        <p>
          <strong>Necessários.</strong> Este Aplicativo usa Cookies técnicos e
          Rastreadores similares para executar atividades estritamente necessárias para
          operar ou prestar o Serviço.
        </p>
        <p>
          Em função da complexidade objetiva dessas tecnologias, recomendamos que os
          Usuários entrem em contato com o Proprietário para receber mais informações
          sobre seu uso.
        </p>
        <h3 className="text-xl font-semibold">Definições de Cookies e Rastreadores</h3>
        <p>
          Cookie é um Rastreador composto por pequenos conjuntos de dados armazenados no
          navegador do Usuário. Rastreador é qualquer tecnologia, como Cookies,
          identificadores únicos, web beacons, scripts embutidos, e-tags e fingerprinting,
          que permita rastrear Usuários acessando ou armazenando informações no
          dispositivo.
        </p>
        <p>Última atualização: 4 de outubro de 2026.</p>
      </Section>
    </>
  )
}
