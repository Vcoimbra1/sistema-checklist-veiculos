#  Sistema de Checklist Digital - Pós-Venda Automotivo

##  O Propósito do Projeto (Problema Real)
Este sistema foi idealizado e desenvolvido inteiramente do zero para resolver um gargalo real do meu dia a dia no setor de pós-venda da concessionária Royal Motors, em Bragança Paulista. 

Até então, todo o processo de recebimento e inspeção do estado de conservação dos veículos era feito de forma analógica, no papel. Isso gerava lentidão, acúmulo de arquivos físicos e uma enorme dificuldade de organização para atrelar as fotos das avarias aos registros dos clientes. 

Como estudante do 5º semestre de Análise e Desenvolvimento de Sistemas (ADS) no IFSP e com o objetivo de consolidar minha carreira como Desenvolvedor Backend, decidi aplicar a engenharia de software para arquitetar uma solução que digitalizasse 100% dessa operação.

##  A Solução
Substituí as pranchetas por uma aplicação web responsiva (Single Page Application) integrada a uma API RESTful. Agora, a inspeção é feita diretamente pelo smartphone no pátio da loja:
1. O veículo é cadastrado no sistema.
2. O estado de conservação (limpeza, pneus, etc.) é registrado.
3. As evidências fotográficas são tiradas usando a câmera nativa do celular direto no navegador, sendo enviadas e organizadas automaticamente no servidor local.
4. Os dados ficam centralizados e disponíveis em um **Painel Administrativo** para gestão via desktop.

##  Arquitetura e Tecnologias (Foco em Backend)
A arquitetura foi pensada para rodar em uma rede local, utilizando tunelamento para acesso móvel seguro.

**Backend:**
* **Python 3** com framework **FastAPI** (Alta performance e rotas assíncronas).
* **Banco de Dados Relacional:** SQLite (Modelagem com chaves estrangeiras unindo `veiculos`, `checklists` e `fotos_veiculo`).
* **Gerenciamento de Arquivos:** Upload via `FormData` e persistência no sistema de arquivos local.

**Frontend & Infraestrutura:**
* **Interface:** HTML5, Bootstrap 5 e Vanilla JavaScript (Fetch API).
* **Acesso Nativo:** Uso da tag `capture="environment"` para abrir a câmera traseira do dispositivo via browser.
* **Deploy Local:** Scripts automatizados (`.bat`) e exposição segura para a internet (rede móvel) utilizando **Ngrok**.

##  Como Executar o Projeto Localmente

1. Clone este repositório:
```bash
git clone [https://github.com/SEU-USUARIO/NOME-DO-SEU-REPO.git](https://github.com/SEU-USUARIO/NOME-DO-SEU-REPO.git)