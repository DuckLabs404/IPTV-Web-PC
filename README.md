# 📺 IPTV-Web-PC

<p align="center">
  <img src="https://img.shields.io/badge/DEVELOPED%20BY-DUCK%20LABS-orange?style=for-the-badge" alt="Developed By Duck Labs">
  <img src="https://img.shields.io/badge/PYTHON-3.X-blue?style=for-the-badge&logo=python" alt="Python 3.x">
  <img src="https://img.shields.io/badge/STATUS-EM%20DESENVOLVIMENTO-red?style=for-the-badge" alt="Status">
</p>

## 🚀 Visão Geral

O **IPTV-Web-PC** é um player de listas IPTV baseado na web projetado para rodar diretamente no navegador de forma leve, rápida e com interface customizada. O sistema processa listas no formato `.m3u` (locais ou por URL), dividindo o conteúdo de forma inteligente e integrada.

Para viabilizar a reprodução estável e contornar de vez as restrições de segurança dos navegadores (erros de CORS ao carregar streams externos), o ecossistema utiliza um **servidor proxy local em Python** trabalhando em conjunto com um **mecanismo de decoding** dedicado para transmissões ao vivo.

---

## 📸 Demonstração da Interface

<p align="center">
  <img src="preview-player.jpg" width="65%" alt="Player Ao Vivo" title="Player Ao Vivo">
  <img src="preview-series.png" width="30%" alt="Categorias de Séries" title="Variedade de Séries">
</p>

*Interface escura e minimalista, exibindo a reprodução estável de canais de TV ao vivo (Live) e o mapeamento completo e organizado de extensas listas de séries e streaming.*

## 🛠️ Recursos & Funcionalidades Atualizadas

* **Nova Interface Fluida:** Layout reformulado, mais limpo e focado na experiência de navegação do usuário.
* **Decoder Nativo Integrado:** Decodificação otimizada para garantir a estabilidade e a reprodução de fluxos e transmissões ao vivo (Live TV).
* **Suporte Multi-Formato:** Player aprimorado para aceitar e processar diferentes extensões e formatos de transmissão de vídeo diretamente no client-side.
* **Bypass de CORS:** Servidor proxy em Python (`proxy_server.py`) robusto que gerencia os cabeçalhos e requisições de mídia em tempo real.

---

## 🚧 Status Atual do Desenvolvimento

- [x] Estrutura e Nova Interface Web (`iptv-player.html`)
- [x] Decoder de transmissões ao vivo integrado
- [x] Suporte a múltiplos formatos de stream
- [x] Servidor proxy funcional de requisições (`proxy_server.py`)
- [ ] Implementação de Modo Escuro (Dark Mode) nativo
- [ ] Sistema de busca interna por canais/filmes e gerenciamento de favoritos

---

## 💻 Como Executar o Repositório Local

### 1. Clonar o Repositório
```bash
git clone [https://github.com/DuckLabs404/IPTV-Web-PC.git](https://github.com/DuckLabs404/IPTV-Web-PC.git)
cd IPTV-Web-PC