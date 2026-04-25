#!/bin/bash

echo ""
echo "======================================"
echo "Installer - Tradutor de Reuniões"
echo "======================================"
echo ""

# Check if Python 3.11+ is installed
if ! command -v python3 &> /dev/null; then
    echo "ERRO: Python 3 não foi encontrado!"
    echo ""
    echo "Instale Python 3.11+ usando:"
    echo "  macOS: brew install python3"
    echo "  Ubuntu: sudo apt-get install python3"
    echo ""
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "Python encontrado: $PYTHON_VERSION"

echo ""
echo "Criando ambiente virtual..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "ERRO: Falha ao criar o ambiente virtual!"
    exit 1
fi

echo "Ativando ambiente virtual..."
source venv/bin/activate

if [ $? -ne 0 ]; then
    echo "ERRO: Falha ao ativar o ambiente virtual!"
    exit 1
fi

echo ""
echo "Atualizando pip..."
python -m pip install --upgrade pip > /dev/null 2>&1

echo "Instalando dependências..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "ERRO: Falha ao instalar dependências!"
    exit 1
fi

echo ""
echo "Tornando run.sh executável..."
chmod +x run.sh

echo ""
echo "======================================"
echo "✓ Instalação concluída com sucesso!"
echo "======================================"
echo ""

# Platform-specific instructions
OS=$(uname -s)

if [ "$OS" = "Darwin" ]; then
    echo "IMPORTANTE - Configurar BlackHole no macOS:"
    echo ""
    echo "1. Visite: https://existential.audio/blackhole/"
    echo "2. Baixe e instale BlackHole (versão gratuita)"
    echo "3. Reinicie seu Mac"
    echo "4. Vá para System Preferences > Sound > Output"
    echo "5. Selecione BlackHole como dispositivo de saída"
    echo "6. Execute: ./run.sh"
    echo ""
elif [ "$OS" = "Linux" ]; then
    echo "IMPORTANTE - Configurar PulseAudio no Linux:"
    echo ""
    echo "Para capturar áudio de aplicativos, você pode:"
    echo ""
    echo "Opção 1: Carregar módulo loopback do PulseAudio"
    echo "  pactl load-module module-loopback"
    echo ""
    echo "Opção 2: Usar um mixer de áudio como pavucontrol"
    echo "  sudo apt-get install pavucontrol"
    echo "  pavucontrol"
    echo ""
    echo "6. Execute: ./run.sh"
    echo ""
fi
