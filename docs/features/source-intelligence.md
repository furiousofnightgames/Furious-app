# Inteligência de Fontes (Source Intelligence) 📡🧠

Antes de comprometer sua banda, o Furious App analisa a "saúde" do download para garantir a melhor velocidade e estabilidade.

## 🩺 Análise de Alternativas Saudáveis

Quando o usuário seleciona um jogo que possui múltiplas fontes (ex: FitGirl, DODI, ElAmigos), o App entra em ação:

### 1. Pré-Flight Check (Sondagem UDP)
O App dispara "sondas" silenciosas para os rastreadores (trackers) dos Magnet Links disponíveis.
- **Protocolo UDP**: Leve e rápido, não inicia o download.
- **Contagem Real**: Obtém o número exato de **Seeders** (quem tem o arquivo completo) e **Peers** (quem está baixando).

### 2. Recomendação Inteligente
Se o usuário escolheu uma versão com 5 Seeders, mas existe uma alternativa idêntica com 500 Seeders:
- **Alerta de Oportunidade**: O App sugere a troca da fonte.
- **Benefício**: Downloads até 100x mais rápidos e menor chance de estagnar em 99%.

### 3. Validação de Link
Para downloads diretos (HTTP), o sistema faz requisições `HEAD` para garantir que o arquivo ainda existe no servidor e suporta "Resume" (continuar de onde parou), evitando links quebrados frustrantes.
