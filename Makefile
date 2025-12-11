#######################################
### Semantic Search Engine Makefile ###
#######################################

# Python virtual environment path
VENV=venv
PYTHON=$(VENV)/bin/python
PIP=$(VENV)/bin/pip

###################################
###### Setup & Installation #######
###################################

install:
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt

###################################
####### Dataset Processing ########
###################################

dataset: 
	$(PYTHON) -c "from app.preprocessing import build_jsonl; build_jsonl()"

###################################
###### FAISS Index Building #######
###################################

# default index: L2
index: 
	$(PYTHON) -c "from app.search import build_faiss_index; build_faiss_index('l2')"

# explicit IndexFlatL2 build
index:
	$(PYTHON) -c "from app.search import build_faiss_index; build_faiss_index('l2')"

# Cosine similarity index
index-cosine:
	$(PYTHON) -c "from app.search import build_faiss_index; build_faiss_index('cosine')"

###################################
######### Run API Server ##########
###################################

api: 
	$(VENV)/bin/uvicorn app.main:app --reload

###################################
########### Run Tests #############
###################################

test: 
	$(VENV)/bin/pytest -q

###################################
######### Docker Build ############
###################################

docker: 
	docker build -t semantic-search-engine .

###################################
############ Cleanup ##############
###################################

clean:
	rm -f index/faiss_index.bin
	rm -f index/faiss_l2.bin
	rm -f index/faiss_cosine.bin
	rm -f index/meta.json
	rm -f index/meta_l2.json
	rm -f index/meta_cosine.json
	rm -f data/processed/documents.jsonl
	rm -rf __pycache__
