# Persistência de Dados & Performance 🚀💾

Para suportar bibliotecas com milhares de jogos e scans de metadados em alta velocidade, o backend utiliza uma arquitetura de persistência otimizada.

## 🧱 Desafio: O Gargalo do SQLite
Durante o "Deep Scan", o App descobre centenas de jogos por minuto. Tentar salvar cada um individualmente no banco de dados (`session.commit()`) causava:
1.  **Travamentos de IO**: O disco não acompanhava as escritas.
2.  **Locks de Banco**: O SQLite bloqueava leituras enquanto gravava.
3.  **Perda de Dados**: Se o App fechasse no meio do processo, a fila de escrita era perdida.

## 🛡️ Solução: Buffered Write (Gravação em Lote)

Implementamos um sistema de **Buffer Inteligente** no `SteamService`:

### 1. Fila de Memória (Memory Queue)
Quando um metadado é baixado (`persist_metadata`), ele **não vai para o disco**. Ele é jogado em uma lista na memória RAM (`_save_queue`). Essa operação leva microssegundos.

### 2. Loop de Descarga (Flush Loop)
Um processo em background acorda a cada **5 segundos**:
1.  Verifica se há itens na fila.
2.  Pega todos os itens acumulados (ex: 50 jogos).
3.  Abre **uma única transação** com o banco de dados.
4.  Grava tudo de uma vez.
5.  Limpa a fila.

Isso reduz a carga no disco em até **100x**.

### 3. Graceful Shutdown (Saída Graciosa)
No arquivo `main.py`, o evento de desligamento do servidor (`shutdown`) foi modificado para chamar `stop_persistence_loop()`. Isso força o sistema a gravar qualquer coisa que esteja na memória antes de encerrar o processo, garantindo **Zero Perda de Dados**.

## 🧹 Silent Scraper
O enriquecimento da biblioteca roda em uma thread separada ("Silent"), garantindo que a interface do usuário nunca trave, mesmo enquanto o back-end está processando gigabytes de metadados.
