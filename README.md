# 📺 IPTV-Web-PC

<p align="center">
  <img src="https://img.shields.io/badge/DEVELOPED%20BY-DUCK%20LABS-orange?style=for-the-badge" alt="Developed By Duck Labs">
  <img src="https://img.shields.io/badge/PYTHON-3.X-blue?style=for-the-badge&logo=python" alt="Python 3.x">
  <img src="https://img.shields.io/badge/STATUS-EM%20DESENVOLVIMENTO-red?style=for-the-badge" alt="Status">
</p>

## 🚀 Visão Geral

O **IPTV-Web-PC** é um player de listas IPTV baseado na web projetado para rodar diretamente no navegador do computador de forma leve e rápida. O objetivo principal é permitir a reprodução de listas no formato `.m3u` (tanto por arquivos locais quanto por links/URLs diretas), categorizando automaticamente o conteúdo em **Canais ao Vivo**, **Séries** e **Filmes**.

Para contornar as restrições de segurança do navegador (erros de CORS ao tentar carregar fluxos de vídeo externos), o projeto conta com um **servidor proxy local em Python**, garantindo estabilidade e autonomia na reprodução sem depender de softwares de terceiros (como VLC ou Kodi).

---

## 🛠️ Recursos & Funcionalidades

* **Suporte Híbrido de Listas:** Carregamento prático de arquivos `.m3u` locais ou via links remotos.
* **Segmentação Automática (Roadmap):** Engine planejada para separar o conteúdo bruto em abas organizadas de canais, filmes e séries.
* **Bypass de CORS:** Servidor proxy nativo em Python que intercepta e libera as requisições de mídia direto no browser.
* **Player Integrado:** Interface minimalista para assistir o conteúdo sem sair da página.

---

## 🚧 Status Atual & Próximos Passos

O projeto encontra-se em **fase ativa de desenvolvimento (MVP)**.

- [x] Estrutura base da interface web (`iptv-player.html`)
- [x] Servidor proxy funcional de requisições (`proxy_server.py`)
- [ ] Implementação de layout moderno com Modo Escuro (Dark Mode)
- [ ] Integração de reprodutor avançado (Hls.js / Video.js) para maior suporte a streams
- [ ] Sistema de busca interna e salvamento de favoritos


### 🔄 O que já está pronto:
* **`iptv-player.html`**: Interface inicial com decoder integrado para reprodução estável de transmissões ao vivo.
* **`proxy_server.py`**: Script em Python responsável por receber as requisições do navegador, buscar os dados do fluxo IPTV e devolver os dados burlando o bloqueio de CORS.

---

