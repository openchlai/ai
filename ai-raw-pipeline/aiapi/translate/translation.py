from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

def translation(dat=False):
	# https://medium.com/@perezogayo/translating-text-using-meta-ais-nllb-fb189f3a946c
	tokenizer = AutoTokenizer.from_pretrained("facebook/nllb-200-distilled-600M")
	model = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-distilled-600M")

	translator = pipeline(
		'translation',
		model=model,
		tokenizer=tokenizer,
		src_lang='swa_Latn', 
		tgt_lang='eng_Latn',
		max_length = 200)

	# kinyarwanda-english
	text=["Niambie mambo", "Erevuka ujue mambo"]
	translator(text)

	#Get the code of your target langauge. After getting the language code; get the id
	tgt_lang_id = tokenizer.lang_code_to_id["eng_Latn"]

	#tokenize your input
	model_inputs = tokenizer(text, return_tensors="pt", padding='longest')

	#generate output
	gen_tokens = model.generate(**model_inputs , forced_bos_token_id=tgt_lang_id)

	#decode output — convert to text
	translated_text = tokenizer.batch_decode(gen_tokens, skip_special_tokens=True)

	#print
	print(translated_text)
