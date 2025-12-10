import json
import os


def clean_text(text: str) -> str:
    return " ".join(text.strip().split())  # delete spaces and line breaks, cut multiple spaces and line breaks, etc...



def build_jsonl (raw_dir="data/raw", output_file="data/processed/documents.jsonl"):
	"""
	browse all .txt files in data/raw/ and create a JSONL file with a doc per line
	"""
	
	docs = []
	if not os.path.isdir(raw_dir): # check if data/raw exist
		raise ValueError(f"Raw directory not found: {raw_dir}")
	
	with open(output_file, "w", encoding="utf-8") as f_out:  # create/crush documents.jsonl
		for idx, filename in enumerate(os.listdir(raw_dir)):  # os.listdir = list all files/folders in data/raw
			if not filename.endswith(".txt"):
				continue
			
			path = os.path.join(raw_dir, filename)

			with open(path, "r", encoding="utf-8") as f_in:
				text = clean_text(f_in.read())  # clean all the text with function clean_text



			"""
			create JSON object
			"""
			doc = {
				"id": f"doc_{idx+1}",
				"title": filename.replace(".txt","").replace("_"," "),
				"text": text,
				"tags": []
			}

			
			f_out.write(json.dumps(doc) +"\n") # transform document into JSON and write a line per doc


	print(f"JSONL dataset created -> {output_file}")
