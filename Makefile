export PYTHONPATH:=$(shell pwd)
.PHONY: all fr_pacs fr_hub fr_brain clean

fr_pacs:
	@echo "Starting FrPACS..."
	nohup python3 fr_pacs/main.py > fr_pacs/fr_pacs.log 2>&1 &

fr_hub:
	@echo "Starting FrHUB..."
	nohup python3 fr_hub/main.py > fr_hub/fr_hub.log 2>&1 &

fr_brain:
	@echo "Starting FrBRAIN..."
	nohup python3 fr_brain/main.py > fr_brain/fr_brain.log 2>&1 &

all: fr_pacs fr_hub fr_brain

clean:
	@echo "Stopping all components here..."
	-pkill -f fr_pacs/main.py
	-pkill -f fr_hub/main.py
	-pkill -f fr_brain/main.py
	@echo "All components are stopped."


coverage:
	@echo "Starting unit tests..."
	coverage run -m pytest
	coverage report -m

test:
	@echo "Starting unit tests..."
	pytest -v


