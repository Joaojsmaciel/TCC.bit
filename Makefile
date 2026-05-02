# Makefile para Sistema P2P
# Facilita comandos comuns do Docker Compose

.PHONY: help build up down logs clean test files peer1 peer2 peer3 tracker restart

# Cores para output
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
WHITE  := $(shell tput -Txterm setaf 7)
RESET  := $(shell tput -Txterm sgr0)

help: ## Mostra esta ajuda
	@echo ''
	@echo 'Uso:'
	@echo '  ${YELLOW}make${RESET} ${GREEN}<target>${RESET}'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  ${YELLOW}%-15s${GREEN}%s${RESET}\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Constrói as imagens Docker
	@echo "${GREEN}Construindo imagens...${RESET}"
	docker-compose build

up: ## Inicia o sistema (tracker + 3 peers)
	@echo "${GREEN}Iniciando sistema P2P...${RESET}"
	docker-compose up -d
	@echo "${GREEN}Sistema iniciado!${RESET}"
	@echo "${YELLOW}Acesse os peers com:${RESET}"
	@echo "  make peer1"
	@echo "  make peer2"
	@echo "  make peer3"

start: up ## Alias para 'up'

down: ## Para o sistema
	@echo "${GREEN}Parando sistema...${RESET}"
	docker-compose down

stop: down ## Alias para 'down'

restart: down up ## Reinicia o sistema

logs: ## Mostra logs de todos os containers
	docker-compose logs -f

logs-tracker: ## Mostra logs do tracker
	docker-compose logs -f tracker

logs-peer1: ## Mostra logs do peer1
	docker-compose logs -f peer1

logs-peer2: ## Mostra logs do peer2
	docker-compose logs -f peer2

logs-peer3: ## Mostra logs do peer3
	docker-compose logs -f peer3

peer1: ## Acessa interface do Peer 1
	@echo "${GREEN}Acessando Peer 1...${RESET}"
	docker exec -it p2p_peer1 python peer.py

peer2: ## Acessa interface do Peer 2
	@echo "${GREEN}Acessando Peer 2...${RESET}"
	docker exec -it p2p_peer2 python peer.py

peer3: ## Acessa interface do Peer 3
	@echo "${GREEN}Acessando Peer 3...${RESET}"
	docker exec -it p2p_peer3 python peer.py

tracker: ## Mostra status do tracker
	@echo "${GREEN}Status do Tracker:${RESET}"
	@docker logs p2p_tracker | tail -20

status: ## Mostra status de todos os containers
	@echo "${GREEN}Status dos Containers:${RESET}"
	@docker-compose ps

files: ## Cria arquivos de teste
	@echo "${GREEN}Criando arquivos de teste...${RESET}"
	@mkdir -p shared_files
	@echo "Este é um TCC sobre Sistemas Distribuídos P2P" > shared_files/tcc_sistemas_distribuidos.zip
	@echo "Artigo sobre Redes de Computadores" > shared_files/artigo_redes.zip
	@echo "Trabalho de Conclusão de Curso - Segurança" > shared_files/tcc_seguranca.zip
	@echo "Pesquisa sobre Cloud Computing" > shared_files/artigo_cloud.zip
	@echo "Projeto Final - Banco de Dados" > shared_files/trabalho_bd.zip
	@echo "${GREEN}Arquivos criados em shared_files/${RESET}"
	@ls -lh shared_files/

clean: down ## Remove containers, volumes e arquivos gerados
	@echo "${GREEN}Limpando sistema...${RESET}"
	docker-compose down -v
	rm -rf shared_files/
	rm -rf files_*/
	@echo "${GREEN}Sistema limpo!${RESET}"

clean-all: clean ## Remove tudo, incluindo imagens
	@echo "${GREEN}Removendo imagens Docker...${RESET}"
	docker rmi sistematcc_tracker sistematcc_peer1 sistematcc_peer2 sistematcc_peer3 2>/dev/null || true
	@echo "${GREEN}Limpeza completa!${RESET}"

test: files up ## Inicia sistema com arquivos de teste
	@echo "${GREEN}Sistema iniciado com arquivos de teste!${RESET}"
	@sleep 3
	@echo "${YELLOW}Aguardando inicialização...${RESET}"
	@sleep 2
	@echo "${GREEN}Pronto! Use 'make peer1' para acessar um peer.${RESET}"

ps: status ## Alias para 'status'

shell-peer1: ## Abre shell no container do peer1
	docker exec -it p2p_peer1 sh

shell-peer2: ## Abre shell no container do peer2
	docker exec -it p2p_peer2 sh

shell-peer3: ## Abre shell no container do peer3
	docker exec -it p2p_peer3 sh

shell-tracker: ## Abre shell no container do tracker
	docker exec -it p2p_tracker sh

rebuild: clean build up ## Reconstrói e reinicia tudo

.DEFAULT_GOAL := help
