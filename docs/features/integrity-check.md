# Verificação de Integridade (Quick-Check) 🛡️

O **Quick-Check** é um sistema de auditoria de arquivos pós-download que garante que o conteúdo baixado é seguro, completo e instalável antes que o usuário tente executar `setup.exe`.

## 🧠 Filosofia: "O Disco é a Verdade"

Diferente de sistemas que confiam cegamente em logs de download, o Quick-Check realiza uma **Varredura Física** no disco rígido. Se o arquivo não está lá fisicamente, ele não existe para o sistema.

## 🕵️‍♂️ Fluxo de Verificação

### 1. Detecção Automática
Ao clicar em "Instalar", o sistema intercepta a ação e inicia o `IntegrityService`.
- **Manifesto de Arquivos**: O serviço lista recursivamente todos os arquivos na pasta de destino.
- **Detecção de Componentes**: Busca por arquivos críticos:
    - Instaladores (`setup.exe`, `install.exe`) 🚀
    - Arquivos de Dados (`.bin`, `.pak`) 📦
    - Scripts de Verificação (`verify.bat`, `md5`) 🛡️

### 2. Detecção de Anomalias
O sistema verifica condições de falha comuns em Repacks:
- **Arquivos Fantasmas (0-bytes)**: Detecta arquivos que existem no nome, mas têm 0 KB de tamanho (sinal de corrupção ou erro de disco).
- **Lacunas de Sequência**: Verifica se falta algum volume (ex: tem `data-1.bin` e `data-3.bin`, mas falta o `data-2.bin`).
- **Instalador Ausente**: Alerta se não houver nenhum executável de instalação.

### 3. Validação de Tamanho (Card-Sync)
Para eliminar falsos positivos, o sistema usa a lógica **Card-Sync**:
- Compara o **Tamanho Físico Total** encontrado no disco.
- Compara com o **Tamanho Exibido no Card** (metadados).
- **Auto-Sync**: Se o disco contém arquivos saudáveis e completos, mas o tamanho difere ligeiramente do metadado inicial (ex: 1.09 GB vs 1.00 GB no Magnet), o sistema **atualiza o banco de dados** para refletir a realidade do disco, marcando como ✅ SUCESSO.

## 🚦 Status de Saúde

| Status | Score | Descrição |
|--------|-------|-----------|
| **HEALTHY** | 90-100% | Download perfeito. Todos os arquivos presentes e tamanhos batem. |
| **WARNING** | 50-89% | Download instalável, mas com avisos (ex: falta arquivo MD5 opcional). |
| **CRITICAL** | < 50% | Falha grave. Faltam arquivos vitais (.bin ou .exe). Instalação bloqueada. |

## 💻 Logs no Terminal

O Quick-Check gera logs de auditoria detalhados no terminal do backend para transparência total:

```text
[Integrity] EXAME DE RAIO-X PARA JOB #42
============================================================
[Manifesto] Listando 7 arquivos encontrados:
  🚀 [EXE] setup.exe (5.31 MB)
  📦 [BIN] data-1.bin (1.06 GB)
  🛡️ [BAT] verify.bat (1.2 KB)

[Audit de Tamanho]
  • Fisicamente no Disco:       1.09 GB
  • Tamanho Exibido no Card:    1.09 GB
  • Conclusão do Audit: ✅ INTEGRIDADE OK (Bate com o Card)

[Conclusão] Score: 100% | Status: HEALTHY
```
