# Plano de Correção – Permissões e Logs da Aplicação

## Contexto do Problema
A aplicação de download de jogos grava logs e arquivos dinâmicos dentro da própria pasta instalada.
Quando instalada em `Program Files (x86)` ou `Program Files`, o Windows bloqueia escrita, gerando erros
de permissão (`EPERM`). Executar como administrador apenas mascara o problema.

---

## Objetivo Estratégico
Adequar a aplicação aos **padrões profissionais do Windows**, garantindo:
- Execução sem privilégios elevados
- Compatibilidade com instalações em pastas protegidas
- Estabilidade, segurança e facilidade de distribuição

---

## Princípio Arquitetural
Separação clara de responsabilidades:

### Pasta da Aplicação
- Executável (.exe)
- Recursos estáticos (ícones, assets, binários)
- **Nunca** sofre escrita em tempo de execução

### Pasta de Dados do Usuário
- Logs
- Cache
- Configurações
- Estado de downloads

---

## Planejamento de Ação

### Fase 1 – Diagnóstico Interno
- Mapear todos os pontos onde a aplicação grava arquivos
- Identificar:
  - Logs
  - Arquivos temporários
  - Estado de downloads
- Garantir que nenhum dado mutável dependa da pasta raiz da aplicação

### Fase 2 – Definição do Local de Dados
- Adotar o **diretório de dados do usuário da aplicação** como padrão
- Garantir que o caminho seja:
  - Único por usuário
  - Persistente entre execuções
  - Compatível com políticas do Windows

### Fase 3 – Redirecionamento de Escrita
- Redirecionar criação de logs para o diretório de dados
- Redirecionar arquivos temporários e cache
- Manter leitura de assets a partir da pasta instalada

### Fase 4 – Ajustes no Instalador
- Instalador executa como administrador
- Aplicação final **não solicita privilégios elevados**
- Nenhuma dependência de permissões especiais após instalação

### Fase 5 – Validação
- Testar instalação em:
  - `Program Files (x86)`
  - Conta sem privilégios administrativos
- Validar:
  - Criação de logs
  - Execução contínua
  - Downloads funcionando corretamente

---

## Resultado Esperado
- Aplicação executa sem erros de permissão
- Nenhuma necessidade de modo administrador
- Comportamento consistente em qualquer máquina
- Arquitetura pronta para distribuição pública

---

## Visão de Longo Prazo
Essa correção:
- Facilita futuras atualizações
- Reduz riscos de bloqueio por antivírus
- Prepara a aplicação para ambientes corporativos
- Eleva o projeto ao padrão de software profissional

---

## Resumo Executivo
O problema não é a instalação nem permissões manuais.
É **arquitetura**.
Separando corretamente executável e dados, o erro deixa de existir de forma definitiva.
