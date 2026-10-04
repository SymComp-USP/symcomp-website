import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Política de Privacidade | Semana da Computação',
  description: 'Política de privacidade da Semana da Computação.',
}

export default function PrivacyPage() {
  return (
    <main className="mx-auto w-full max-w-4xl px-6 py-12 sm:py-16">
      <article className="space-y-6 rounded-none border-[6px] border-[hsl(var(--semana-contrast))] bg-card p-6 text-card-foreground sm:p-10">
        <header className="space-y-3">
          <h1 className="font-[family-name:var(--font-semana-display)] text-4xl uppercase sm:text-5xl">
            Política de privacidade
          </h1>
          <p className="text-muted-foreground">
            Última atualização: 4 de outubro de 2026.
          </p>
        </header>
        <section className="space-y-3">
          <h2 className="text-2xl font-semibold">Proprietário e controlador</h2>
          <p>
            O controlador dos dados é o Simpósio da Computação, localizado na R. do Matão,
            1010 — Bloco B, Butantã, São Paulo — SP, 05508-090. Para dúvidas ou
            solicitações sobre privacidade, escreva para{' '}
            <a
              className="underline underline-offset-4"
              href="mailto:semanadacomputacao@ime.usp.br"
            >
              semanadacomputacao@ime.usp.br
            </a>
            .
          </p>
        </section>
        <section className="space-y-3">
          <h2 className="text-2xl font-semibold">Dados coletados</h2>
          <p>
            A SymComp trata nome, endereço de e-mail e o identificador da conta para
            criar, autenticar e manter seu perfil na Semana da Computação.
          </p>
          <p>
            No cadastro direto, também tratamos a senha informada para permitir o acesso à
            conta. Dados técnicos, como endereço IP e registros de acesso, podem ser
            tratados para operação, segurança e manutenção do site.
          </p>
          <p>
            Dados de uso podem incluir endereço IP, navegador, sistema operacional,
            páginas acessadas, data e hora das requisições e registros técnicos do
            servidor. Cookies e tecnologias semelhantes são usados para prestar os
            serviços solicitados e nas finalidades descritas nesta política.
          </p>
        </section>
        <section className="space-y-3">
          <h2 className="text-2xl font-semibold">Login com Google e GitHub</h2>
          <p>
            No Google, solicitamos somente <code>openid</code>, <code>email</code> e{' '}
            <code>profile</code>. No GitHub, solicitamos <code>read:user</code> e{' '}
            <code>user:email</code>. Esses dados confirmam seu e-mail e identificam sua
            conta.
          </p>
          <p>
            Tokens de acesso fornecidos por Google e GitHub são usados somente durante a
            autenticação e não são armazenados pela aplicação.
          </p>
        </section>
        <section className="space-y-3">
          <h2 className="text-2xl font-semibold">Como e por que os dados são usados</h2>
          <p>
            Usamos esses dados para registro, autenticação, fornecimento das
            funcionalidades da Semana da Computação, segurança e cumprimento de obrigações
            legais. Os dados são conservados pelo tempo necessário para essas finalidades
            ou por período maior quando exigido por lei.
          </p>
          <p>
            O tratamento é realizado com computadores e ferramentas de TI, com medidas
            adequadas para impedir acesso, alteração, divulgação ou destruição não
            autorizados. Dados podem ser acessados por pessoas responsáveis pela operação
            do serviço e por fornecedores técnicos, de hospedagem e TI quando necessário.
          </p>
        </section>
        <section className="space-y-3">
          <h2 className="text-2xl font-semibold">Cookies e transferências</h2>
          <p>
            Este site usa rastreadores. Consulte a Política de Cookies para conhecer as
            categorias, finalidades e controles disponíveis. Dados podem ser processados
            em locais onde estejam o controlador ou fornecedores envolvidos no tratamento,
            inclusive fora do Brasil, quando permitido pela legislação aplicável.
          </p>
        </section>
        <section className="space-y-3">
          <h2 className="text-2xl font-semibold">Seus direitos</h2>
          <p>
            Nos termos da LGPD, você pode solicitar confirmação de tratamento, acesso,
            correção, anonimização, bloqueio, exclusão, portabilidade, informação sobre
            compartilhamentos e revogação de consentimento. Contato:{' '}
            <a
              className="underline underline-offset-4"
              href="mailto:semanadacomputacao@ime.usp.br"
            >
              semanadacomputacao@ime.usp.br
            </a>
            .
          </p>
          <p>
            Você também pode se opor a tratamentos em desconformidade com a LGPD, pedir
            informações sobre decisões automatizadas e registrar reclamação perante a
            ANPD. Solicitações podem ser feitas gratuitamente pelo contato acima; quando
            cabível, a resposta completa será fornecida em até 15 dias.
          </p>
        </section>
        <section className="space-y-3">
          <h2 className="text-2xl font-semibold">Informações adicionais</h2>
          <p>
            Dados poderão ser utilizados para defesa de direitos em processos judiciais ou
            quando houver obrigação de fornecê-los a autoridades competentes. Esta
            política pode ser atualizada; mudanças relevantes serão comunicadas nesta
            página e, quando necessário, será solicitada nova anuência.
          </p>
        </section>
        <section className="space-y-3">
          <h2 className="text-2xl font-semibold">Política completa</h2>
          <p>
            A política completa de privacidade está disponível abaixo. Ela também descreve
            o uso de cookies e como alterações nesta política são comunicadas.
          </p>
          <iframe
            className="h-[70rem] w-full border-0"
            src="https://www.iubenda.com/privacy-policy/40876019"
            title="Política de Privacidade"
          />
          <p className="text-sm text-muted-foreground">
            Se a política não aparecer, abra{' '}
            <a
              className="underline underline-offset-4"
              href="https://www.iubenda.com/privacy-policy/40876019"
            >
              Política de Privacidade
            </a>
            .
          </p>
        </section>
        <div>
          <a
            className="rounded-full border-2 border-[hsl(var(--semana-contrast))] px-4 py-2 font-medium text-[hsl(var(--semana-contrast))]"
            href="https://www.iubenda.com/privacy-policy/40876019/cookie-policy"
            title="Política de Cookies"
          >
            Política de Cookies
          </a>
        </div>
      </article>
    </main>
  )
}
