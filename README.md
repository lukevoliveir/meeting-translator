# Tradutor de Reuniões em Tempo Real

Um aplicativo desktop Python que captura áudio do sistema em tempo real, transcreve usando Whisper com detecção automática de idioma, e exibe legendas traduzidas em uma janela flutuante que fica sobre qualquer aplicação.

## 🎯 Características Principais

- **Captura de áudio em tempo real** via loopback de áudio (sem microfone necessário)
- **Transcrição automática** usando o modelo Whisper da OpenAI
- **Detecção de idioma** automática
- **Tradução em tempo real** usando Google Translator (sem necessidade de API key)
- **Janela flutuante** sempre no topo (funciona com Zoom, Google Meet, Microsoft Teams, etc.)
- **Arrastável** - mova a janela clicando e arrastando
- **Atalho de teclado** (Alt+T) para mostrar/ocultar
- **Ícone na bandeja do sistema** (system tray)
- **Menu de contexto** com clique direito
- **Interface limpa** com emojis de bandeira mostrando o idioma

## 📋 Requisitos do Sistema

- **Python**: 3.11 ou superior
- **Sistema Operacional**: Windows 10/11, macOS 12+, ou Ubuntu 22+
- **RAM**: Mínimo 4GB (recomendado 8GB para melhor performance)
- **Processador**: Intel/AMD x64 com suporte SSE4.2

## 🚀 Instalação

### Windows 10/11

1. **Verifique se Python está instalado:**
   ```cmd
   python --version
   ```
   Se não estiver, baixe em: https://www.python.org/ (certifique-se de marcar "Add Python to PATH")

2. **Execute o instalador:**
   ```cmd
   install.bat
   ```

3. **Habilite o Stereo Mix (IMPORTANTE):**
   - Abra **Painel de Controle** → **Som**
   - Clique na aba **Gravação**
   - Clique com botão direito em espaço vazio
   - Marque **"Mostrar Dispositivos Desativados"**
   - Procure por **"Stereo Mix"** ou **"Mistura Estéreo"**
   - Se não encontrar, pode estar desativado no BIOS. Reinicie o computador e verifique as configurações do BIOS
   - Clique com botão direito em **"Stereo Mix"** → **"Ativar"**
   - Clique com botão direito novamente → **"Definir como Dispositivo Padrão"**
   - Clique **"Aplicar"** e **"OK"**

4. **Inicie o aplicativo:**
   ```cmd
   run.bat
   ```

### macOS 12+

1. **Verifique se Python está instalado:**
   ```bash
   python3 --version
   ```
   Se não estiver, instale via Homebrew:
   ```bash
   brew install python3
   ```

2. **Instale o BlackHole (IMPORTANTE):**
   - Visite: https://existential.audio/blackhole/
   - Baixe a versão gratuita (BlackHole 2ch ou 16ch)
   - Instale seguindo as instruções
   - Reinicie o Mac
   - Abra **System Preferences** → **Sound** → **Output**
   - Selecione **BlackHole** como dispositivo de saída

3. **Execute o instalador:**
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

4. **Inicie o aplicativo:**
   ```bash
   ./run.sh
   ```

### Ubuntu 22+ (e outras distribuições Linux)

1. **Verifique se Python está instalado:**
   ```bash
   python3 --version
   ```
   Se não estiver:
   ```bash
   sudo apt-get install python3 python3-venv
   ```

2. **Configure o PulseAudio:**
   ```bash
   pactl load-module module-loopback
   ```
   
   Ou instale um mixer de áudio:
   ```bash
   sudo apt-get install pavucontrol
   pavucontrol
   ```

3. **Execute o instalador:**
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

4. **Inicie o aplicativo:**
   ```bash
   ./run.sh
   ```

## 📖 Como Usar

1. Depois de instalar e configurar conforme acima, inicie o aplicativo
2. Uma janela flutuante aparecerá no canto inferior da tela
3. A janela mostrará "Aguardando áudio..." até que comece a capturar
4. Abra o Zoom, Google Meet, Microsoft Teams ou qualquer outro aplicativo
5. Inicie uma reunião ou toque áudio no computador
6. O aplicativo começará a transcrever e traduzir automaticamente

### Controles

| Ação | Descrição |
|------|-----------|
| **Alt + T** | Mostrar/Ocultar a janela de legendas |
| **Clique e arraste** | Mover a janela para outro lugar |
| **Clique direito** | Menu de contexto com opções |
| **Ícone na bandeja** | Minimizar/restaurar a janela |
| **Ctrl + C** | Fechar o aplicativo (no terminal) |

## ⚙️ Configuração

### Alterar Idioma Alvo

Edite o arquivo `config.py` e procure por:
```python
TARGET_LANG = "pt"
```

Mude para o código do idioma desejado:
- `pt` - Português (Brasil)
- `en` - Inglês
- `es` - Espanhol
- `fr` - Francês
- `de` - Alemão
- `it` - Italiano
- `ja` - Japonês
- `ko` - Coreano
- `zh` - Chinês
- `ru` - Russo

### Alterar Tamanho do Modelo Whisper

Edite o arquivo `config.py`:
```python
WHISPER_MODEL = "base"
```

Opções disponíveis:
- `tiny` - Muito rápido, menos preciso (~39M)
- `base` - Bom balanço entre velocidade e precisão (~140M) - **Recomendado**
- `small` - Mais preciso (~466M)
- `medium` - Muito preciso (~1.5GB)
- `large` - Máxima precisão, lento (~2.9GB)

**Nota**: Modelos maiores requerem mais RAM e processamento, mas são mais precisos.

### Ajustar Sensibilidade de Silêncio

Edite `config.py`:
```python
SILENCE_THRESHOLD = 0.01  # Reduzir para mais sensível, aumentar para menos sensível
```

## 💡 Dicas e Troubleshooting

### Fones de Ouvido Funcionam Normalmente?

**Sim!** O aplicativo captura áudio no nível do sistema operacional, antes do áudio chegar ao dispositivo de saída. Portanto, funciona perfeitamente com:
- Fones de ouvido
- Caixas de som
- Qualquer dispositivo de áudio

### Não Está Capturando Áudio

**Windows:**
- Verificou se Stereo Mix está habilitado?
- Está em Painel de Controle → Som → Gravação?
- Reinicie o aplicativo depois de ativar o Stereo Mix

**macOS:**
- Verificou se BlackHole está instalado?
- Selecionou BlackHole em System Preferences → Sound → Output?
- Reinicie o aplicativo

**Linux:**
- Execute: `pactl list sources` para ver dispositivos disponíveis
- Procure por um dispositivo com "monitor" no nome
- Se não houver, carregue o módulo loopback: `pactl load-module module-loopback`

### Transcrição Muito Lenta

- Reduza o tamanho do modelo em `config.py` (use `tiny` ao invés de `large`)
- Reduza a duração do chunk: `CHUNK_SECONDS = 2` (padrão é 3)
- Verifique se tem GPU disponível (GPU é muito mais rápida que CPU)

### Tradução Incorreta

- Verifique se o idioma alvo está correto em `config.py`
- Google Translator às vezes erra. Idiomas são complexos!
- Se um idioma específico não funciona bem, tente outro

### A Janela Está Invisível

- Pressione Alt+T para mostrar
- Ou clique no ícone na bandeja do sistema e selecione "Mostrar/Ocultar"

### Consumo Alto de CPU

- Modelos Whisper menores consomem menos (use `tiny` ou `base`)
- Se usar GPU, o consumo de CPU será menor
- Reduza a frequência de captura aumentando `CHUNK_SECONDS`

## 📁 Estrutura do Projeto

```
meeting-translator/
├── main.py              # Programa principal
├── config.py            # Configurações
├── requirements.txt     # Dependências Python
├── install.bat          # Instalador para Windows
├── run.bat              # Executar no Windows
├── install.sh           # Instalador para macOS/Linux
├── run.sh               # Executar no macOS/Linux
├── audio/
│   ├── __init__.py
│   └── capture.py       # Captura de áudio via loopback
├── transcriber/
│   ├── __init__.py
│   └── whisper_stt.py   # Transcrição com Whisper
├── translator/
│   ├── __init__.py
│   └── translate.py     # Tradução com Google Translator
└── ui/
    ├── __init__.py
    └── overlay.py       # Interface de usuário (Tkinter)
```

## 🔧 Dependências Principais

- **openai-whisper** - Transcrição de voz
- **sounddevice** - Captura de áudio
- **deep-translator** - Tradução automática
- **numpy** - Processamento de arrays
- **torch** - Backend de machine learning
- **librosa** - Processamento de áudio
- **pynput** - Captura de atalhos de teclado
- **Pillow** - Processamento de imagens
- **pystray** - Ícone na bandeja do sistema

## 🐛 Reportar Problemas

Se encontrar algum bug ou tiver sugestões, descreva:
1. Sistema operacional (Windows/macOS/Linux, versão)
2. Versão do Python
3. Qual é o problema exato
4. Passos para reproduzir
5. Logs ou mensagens de erro

## 📄 Licença

Este projeto é fornecido como está, para uso pessoal e educacional.

## 🙏 Créditos

- **Whisper** - OpenAI
- **Deep Translator** - Nidhaloff
- **Pystray** - Moses Palmer
- **Sounddevice** - Matthias C. Hormann

## 📞 Suporte

Para problemas com:
- **Whisper**: https://github.com/openai/whisper
- **BlackHole (macOS)**: https://existential.audio/blackhole/
- **Stereo Mix (Windows)**: Veja as instruções de instalação acima
- **PulseAudio (Linux)**: https://wiki.archlinux.org/title/PulseAudio

---

**Versão**: 1.0  
**Última atualização**: 2025-04-25

Divirta-se com suas reuniões sem perder nenhuma legendagem! 🎉
