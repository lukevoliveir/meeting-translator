# 🌐 Guia de Uso - Meeting Translator

## O que é o Meeting Translator?

O **Meeting Translator** é um aplicativo que escuta suas reuniões em tempo real, transcreve o áudio e exibe as legendas traduzidas em uma janela flutuante. Funciona em Zoom, Google Meet, Microsoft Teams e qualquer outra plataforma.

### Por que usar?

- ✅ **Sem configuração complexa** — basta selecionar um idioma e começar
- ✅ **Funciona com fone e alto-falante** — o app escuta o áudio do seu computador
- ✅ **Ninguém descobre** — apenas você vê as legendas
- ✅ **Offline** — a transcrição roda localmente, sem enviar áudio para a internet
- ✅ **Perfil do Falante** — aprenda a sotaque e vocabulário de alguém com YouTube

---

## O que você precisa antes de começar

### 1. Python 3.9 ou superior
Baixe em: https://www.python.org/downloads/

### 2. Windows: Ativar Stereo Mix
Stereo Mix captura o áudio do seu PC antes de sair pelos alto-falantes.

**Passos:**
1. Clique com botão direito no ícone de volume (canto inferior direito)
2. Escolha "Sons" ou "Volume mixer"
3. Vá para a aba "Gravação"
4. Se não vir "Stereo Mix", clique com botão direito no espaço vazio e marque "Mostrar dispositivos desabilitados"
5. Clique com botão direito em "Stereo Mix" → "Ativar"
6. Clique com botão direito novamente → "Definir como dispositivo padrão"

Se ainda não funcionar: seu PC pode não ter Stereo Mix. Considere usar um cabo de áudio ou aplicativo como VB-Audio Virtual Cable.

### 3. macOS: Instalar BlackHole
BlackHole é um software virtual que captura o áudio do seu Mac.

Baixe em: https://github.com/ExistentialAudio/BlackHole

Instalação:
1. Baixe `BlackHole-0.3.4.pkg`
2. Execute o instalador
3. Reinicie o Mac
4. O Meeting Translator encontrará automaticamente o BlackHole

### 4. Linux
Use o PulseAudio (padrão na maioria das distribuições). O Meeting Translator encontra automaticamente.

---

## Como instalar

### Windows
1. Abra `Prompt de Comando` (cmd.exe)
2. Navegue até a pasta do app: `cd caminho/para/meeting-translator`
3. Execute: `install.bat`
4. Aguarde a instalação terminar

### macOS / Linux
1. Abra `Terminal`
2. Navegue até a pasta: `cd caminho/para/meeting-translator`
3. Execute: `./install.sh`
4. Aguarde a instalação terminar

---

## Como usar

### Uso simples (sem perfil)

**1. Inicie o app:**
- Windows: clique duas vezes em `run.bat`
- macOS/Linux: execute `./run.sh` no Terminal

**2. Escolha o idioma:**
- A janela "🌐 Meeting Translator" aparece
- Selecione o idioma para legendas (ex: Português)
- Clique "Próximo →"

**3. Perfil (opcional):**
- Se quiser pular: clique "Pular — iniciar sem perfil"
- A janela flutuante aparece

**4. Comece a reunião:**
- Abra Zoom, Google Meet, Teams ou outro app
- Inicie a reunião normalmente
- As legendas aparecem na janela preta na parte inferior da tela

**5. Encerre:**
- Clique no botão ✕ na janela de legendas
- Confirme para encerrar
- Um resumo é exibido

---

## Preparando uma call importante com antecedência

### ⚠️ IMPORTANTE: Crie o perfil ANTES da reunião!

Se você tem uma call com alguém cujo sotaque ou vocabulário é importante, crie um "Perfil do Falante" **dias antes**, não na hora da call.

### Exemplo real:

**Você tem uma call na quinta-feira com o Dr. Michael Horton, um teólogo americano. Aqui está o que fazer:**

#### Passo 1: NA VÉSPERA OU ALGUMAS HORAS ANTES

1. Execute o Meeting Translator
2. Escolha "Português" como idioma
3. Na tela "Perfil do Falante", você vê:
   - Um campo "URL do YouTube"
   - Um botão "+ Adicionar"

4. **Busque vídeos do Dr. Michael Horton:**
   - Abra YouTube em outro aba
   - Procure por "Michael Horton lecture" ou "Michael Horton interview"
   - Encontre vídeos dele falando (20 a 40 minutos cada é ideal)

5. **Adicione 2-3 URLs:**
   - Copie a URL de cada vídeo
   - Cole em "URL do YouTube"
   - Clique "+ Adicionar"
   - Repita para 2-3 vídeos

6. **Clique "Analisar vídeos e criar perfil"**
   - Uma barra de progresso aparece
   - Serão mostrados passos: "Baixando...", "Transcrevendo...", etc
   - **Isso leva 20-60 minutos** dependendo do tamanho dos vídeos
   - **Deixe o computador funcionando durante isso!**

7. **Quando terminar:**
   - Um resumo é exibido: vocabulário, estatísticas
   - Clique "Usar perfil e iniciar"
   - O app inicia com o perfil pronto
   - Você PODE fechar o app agora — o perfil é salvo

#### Passo 2: NA HORA DA CALL (quinta-feira)

1. Execute o Meeting Translator novamente
2. Escolha "Português"
3. Na tela "Perfil do Falante", você vê um **dropdown** com "Dr. Michael Horton"
4. Selecione-o
   - Carrega **em menos de 1 segundo** (não reprocessa os vídeos!)
5. Clique "Usar perfil e iniciar"
6. Abra a reunião normalmente
7. As legendas já estão otimizadas para o sotaque e vocabulário dele

### Por que funciona?

Termos teológicos como:
- "soteriology" (soteriologia)
- "sanctification" (santificação)
- "covenant theology" (teologia do pacto)
- "Christology" (cristologia)

Sem o perfil, o Whisper pode ouvir como palavras aleatórias. Com o perfil, ele **aprende** que essas palavras aparecem com frequência e as transcreve corretamente.

### Pode reusar o perfil?

**SIM!** Depois de criar um perfil:
- Ele é salvo permanentemente no seu computador
- Na próxima call com a mesma pessoa, selecione o perfil no dropdown
- Carrega em menos de 1 segundo, sem reprocessar

---

## Dúvidas frequentes

### P: O app funciona com fone de ouvido?
**R:** Sim! O aplicativo escuta o áudio do seu PC (via Stereo Mix ou BlackHole), não do microfone. Funciona com fone, caixa, etc.

### P: Precisa de internet?
**R:** Parcialmente:
- **Transcrição (Whisper):** Roda 100% offline no seu computador
- **Tradução:** Precisa de internet (usa Google Translate)
- **Download de vídeos:** Só durante criação de perfil (yt-dlp)

### P: Os outros participantes vão saber que estou usando?
**R:** Não. O aplicativo escuta o áudio local. Nenhuma transmissão de dados. Você não envia áudio para ninguém.

### P: O que é o perfil do falante e por que criar antes?
**R:** É um arquivo que contém as palavras mais comuns e o sotaque de uma pessoa (extraído de vídeos do YouTube). O Whisper usa isso como contexto para transcrever melhor.

**Por que antes?** Baixar e processar vídeos leva 20-60 minutos. Se fizer durante a reunião, você perde tempo valioso. Faça com calma no dia anterior ou algumas horas antes.

### P: Posso usar o mesmo perfil em reuniões futuras?
**R:** Sim! O perfil é salvo permanentemente. Use-o quantas vezes quiser com a mesma pessoa.

### P: E se a pessoa não tiver vídeos no YouTube?
**R:** Use o aplicativo sem perfil. Funciona bem mesmo assim. O Whisper é bom o bastante para maioria dos sotaques e vocabulários gerais.

### P: Como fechar o aplicativo?
**R:** Clique no botão **✕** na janela de legendas. Uma tela de confirmação aparece. Clique "Encerrar". Um resumo da sessão é exibido. Clique "Fechar" para sair.

---

## Problemas?

### "Stereo Mix não aparece" (Windows)
- Seu PC pode não suportar Stereo Mix (alguns notebooks)
- Solução: baixe VB-Audio Virtual Cable (gratuito): https://vb-audio.com/Cable/

### "Dispositivo não encontrado" (macOS)
- Certifique-se de que BlackHole está instalado e o Mac foi reiniciado
- Abra System Preferences → Sound → Output e selecione BlackHole

### "Modelo Whisper muito grande"
- Na primeira execução, o modelo (1.5 GB) é baixado
- Isso é normal. A próxima execução é rápida
- Você precisa de ~2 GB livres no disco

### Nada acontece após clicar "Iniciar"
- Aguarde 10-30 segundos enquanto o Whisper carrega
- Na primeira execução, o modelo está sendo baixado
- Verifique se sua conexão de internet está estável

---

## Sugestões de uso

- **Reuniões importantes:** Crie um perfil do falante principal no dia anterior
- **Sotaque forte:** Procure por 3-4 vídeos, não apenas 1
- **Termos técnicos:** Use o glossário embutido (tech, finance, legal) na tela de idioma
- **Qualidade de áudio:** Se o áudio estiver muito ruidoso, a transcrição será pior. Pedir para participante melhorar o microfone ajuda

---

**Versão 1.0 — Meeting Translator**  
https://github.com/seu-usuario/meeting-translator
