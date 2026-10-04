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
          Esta política se aplica ao aplicativo 16ª Semana da Computação, organizado pela
          SymComp no IME-USP e disponível em https://symcomp.ime.usp.br/semana. Ela
          explica como tratamos seus dados no cadastro, no login e na participação nas
          atividades e desafios do evento.
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
          Coletamos nome, e-mail e informações de verificação da conta. No cadastro
          direto, recebemos uma senha e armazenamos seu hash, não a senha em texto
          legível. No login por Google ou GitHub, armazenamos também o provedor e o
          identificador da conta nesse provedor; não recebemos sua senha do provedor.
        </p>
        <p>
          Conforme sua participação, também tratamos apelido, inscrição no evento,
          registros de presença, respostas aos desafios, resultados, pontuação e horas de
          participação, vinculados à sua conta. Dados técnicos de sessão e registros de
          operação são usados para autenticação, manutenção e segurança.
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
          Dados podem ser acessados pela equipe autorizada responsável pela operação do
          evento e do sistema e por prestadores de infraestrutura e serviços técnicos, na
          medida necessária para prestar o serviço, atender solicitações, proteger as
          contas ou cumprir obrigações legais. Você pode solicitar informações sobre os
          prestadores envolvidos pelo e-mail de contato desta política.
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
        <p>
          Os dados de cadastro, inclusive os obtidos do Google, ficam no banco de dados do
          aplicativo para manter sua conta e reconhecer acessos posteriores. Os registros
          de participação são mantidos enquanto necessários à gestão do evento e ao
          histórico de participação. Desativar uma conta não apaga automaticamente esses
          registros. Para solicitar exclusão ou informações sobre a retenção dos seus
          dados, use o e-mail de contato abaixo. Eventuais dados cuja conservação seja
          necessária por obrigação legal ou exercício de direitos serão tratados apenas
          para essas finalidades.
        </p>
      </Section>

      <Section title="As finalidades do processamento">
        <p>
          Os Dados relativos ao Usuário são coletados para permitir que o Proprietário
          preste seu Serviço, cumpra suas obrigações legais, responda a solicitações de
          execução, proteja seus direitos e interesses (ou aqueles de seus Usuários ou
          terceiros), detecte atividade maliciosa ou fraudulenta, bem como para registro e
          autenticação, gestão das inscrições, confirmação de presença, correção dos
          desafios e cálculo de pontos e horas de participação.
        </p>
      </Section>

      <Section title="Informações detalhadas sobre o processamento de Dados Pessoais">
        <h3 className="text-xl font-semibold">Registro e autenticação</h3>
        <p>
          Ao se registrar ou autenticar, os Usuários permitem a este serviço
          identificá-los e dar-lhes acesso a serviços dedicados. Os serviços podem ser
          fornecidos por terceiros; neste caso, o Aplicativo poderá acessar alguns Dados
          armazenados por estes serviços para fins de registro ou identificação, conforme
          descrito abaixo.
        </p>
        <h3 className="text-xl font-semibold">
          Login com Google: acesso e uso dos dados
        </h3>
        <p>
          Ao escolher entrar com Google, solicitamos as permissões openid, email e
          profile. Recebemos informações de identidade e perfil básico e utilizamos seu
          nome, endereço de e-mail, confirmação de que o e-mail foi verificado e
          identificador único da conta Google (sub). Esses dados permitem criar sua conta,
          reconhecer você em acessos posteriores e dar acesso ao perfil e às
          funcionalidades de participação no evento.
        </p>
        <p>
          Não solicitamos acesso ao Gmail, Google Drive, contatos ou calendário. Não
          recebemos sua senha Google. A foto de perfil não é armazenada no cadastro. Os
          tokens recebidos do Google são usados durante a autenticação e não são
          armazenados no cadastro; a sessão do aplicativo utiliza tokens próprios.
        </p>
        <h3 className="text-xl font-semibold">
          Compartilhamento e proteção dos dados Google
        </h3>
        <p>
          Os dados de identidade recebidos do Google são armazenados no banco de dados do
          aplicativo, com acesso às funções administrativas restrito a usuários
          autorizados. A autenticação usa HTTPS e cookies de sessão protegidos contra
          acesso por scripts no navegador. O tratamento segue as finalidades, os
          destinatários e os critérios de retenção descritos nesta política.
        </p>
        <p>
          Não vendemos dados Google nem os usamos para publicidade, direcionamento de
          anúncios ou treinamento de modelos de inteligência artificial. Não fornecemos
          esses dados a patrocinadores para marketing. O compartilhamento limita-se ao
          necessário para operar as funcionalidades do aplicativo, proteger sua segurança
          ou cumprir obrigações legais. O uso e a transferência de informações recebidas
          das APIs Google seguem a{' '}
          <a
            className="underline underline-offset-4"
            href="https://developers.google.com/terms/api-services-user-data-policy"
          >
            Política de Dados do Usuário dos Serviços de API do Google
          </a>
          , incluindo os requisitos de Uso Limitado.
        </p>
        <h3 className="text-xl font-semibold">
          Revogação de acesso e pedidos de exclusão
        </h3>
        <p>
          Você pode remover a conexão com o aplicativo nas{' '}
          <a
            className="underline underline-offset-4"
            href="https://myaccount.google.com/connections"
          >
            configurações de conexões da sua Conta Google
          </a>
          . A revogação não exclui automaticamente sua conta ou os dados já armazenados no
          aplicativo, nem encerra necessariamente uma sessão já iniciada. Para encerrar a
          sessão, use a opção de sair do site.
        </p>
        <p>
          Para solicitar acesso, correção ou exclusão dos dados da sua conta e da sua
          participação, inclusive os recebidos do Google, escreva para{' '}
          <a
            className="underline underline-offset-4"
            href="mailto:semanadacomputacao@ime.usp.br"
          >
            semanadacomputacao@ime.usp.br
          </a>
          . Informe o e-mail da conta e o pedido, sem enviar senhas ou tokens. Podemos
          solicitar confirmação de identidade antes de atender ao pedido. A exclusão está
          sujeita às hipóteses de conservação descritas nesta política.
        </p>
        <h3 className="text-xl font-semibold">GitHub OAuth</h3>
        <p>
          Ao escolher entrar com GitHub, solicitamos read:user e user:email para obter o
          perfil e identificar o e-mail principal verificado. Armazenamos o nome (ou nome
          de usuário), e-mail, identificador da conta e estado de verificação para criar e
          autenticar sua conta, com os mesmos critérios de retenção e canais de
          atendimento descritos nesta política.
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
        <p>
          Dados tratados: nome, e-mail, hash da senha e estado de verificação da conta.
          Usamos o e-mail também para enviar mensagens de verificação e recuperação de
          acesso quando solicitadas.
        </p>
        <h3 className="text-xl font-semibold">Participação e ranking público</h3>
        <p>
          O ranking público exibe o apelido do participante e sua pontuação, associados a
          um identificador de participação. Escolha um apelido que você aceite tornar
          público. O ranking não exibe seu e-mail nem seu identificador Google. A equipe
          autorizada pode consultar registros de participação, presenças e respostas aos
          desafios para administrar o evento e conferir resultados.
        </p>
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
          O aplicativo usa cookies próprios para autenticação. Ao acessar Google ou GitHub
          para entrar, o tratamento realizado nos sites desses provedores também está
          sujeito às respectivas políticas de privacidade.
        </p>
        <h3 className="text-xl font-semibold">Como este Aplicativo usa Rastreadores</h3>
        <p>
          <strong>Necessários.</strong> O cookie oauth_state protege o fluxo de login por
          Google ou GitHub e tem validade de até dez minutos. O cookie refresh_token
          mantém a sessão autenticada pelo prazo de validade configurado pelo serviço; ele
          é removido ao sair. Você pode apagar ou bloquear cookies nas configurações do
          navegador, mas isso pode impedir o login e o acesso às áreas autenticadas.
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
