📺 IPTV Web PC — Player de Lista M3U no Navegador
Line spacing: 1.25
Este é um projeto leve e prático desenvolvido para reproduzir listas de canais de TV ao vivo, séries e filmes diretamente pelo navegador. O sistema processa tanto arquivos .m3u locais quanto links (URLs) de listas IPTV, utilizando um servidor proxy local em Python para contornar restrições de acesso e garantir a reprodução dos fluxos de vídeo.

🚀 Funcionalidades Principais
Suporte a Arquivos e Links: Carregamento de listas M3U locais ou via URL.
Streaming Direto: Reprodução de canais ao vivo, filmes e séries sem precisar de softwares externos.
Servidor Proxy Integrado: Script em Python que gerencia as requisições e evita bloqueios de CORS ao carregar os canais no navegador.
Interface Web: Player de vídeo integrado para assistir ao conteúdo de forma direta.

🛠️ Tecnologias Utilizadas
Frontend: HTML5, CSS3 e JavaScript.
Backend/Proxy: Python.

⚙️ Como Configurar o Repositório Local
Abra o terminal na pasta do seu projeto e execute os comandos abaixo para vincular e subir os arquivos para o GitHub:
git remote add origin https://github.com/DuckLabs404/IPTV-Web-PC.git
git branch -M main
git add iptv-player.html proxy_server.py README.md
git commit -m "Commit inicial: Estrutura do player, servidor proxy e documentação"
git push -u origin main


