from fastapi import FastAPI
from langchain.chat_models import ChatOpenAI
from langchain.chains import GraphSparqlQAChain
from langchain.graphs import RdfGraph

from app.openAI_key import OPENAI_API_KEY

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Welcome to the chat system server v0.1"}


from langchain import OpenAI, ConversationChain
llm = OpenAI(model_name="gpt-4", openai_api_key=OPENAI_API_KEY, temperature=0) 

#--------------read dataset of sparql and steps
import pandas as pd

path =  'app/triples'
import os 
cwd = os.getcwd()
print(cwd)

tab1_df = pd.read_excel(path +  '/RDF_Task.ods')



select_instruction = """Instructions:
Use only the node types and properties provided in the schema.
Do not use any node types and properties that are not explicitly provided.
Include all necessary prefixes.
Schema:
{schema}
Note: Be as concise as possible.
Do not include any explanations or apologies in your responses.
Do not respond to any questions that ask for anything else than for you to construct a SPARQL query.
Only return the SPARQL query generated and no other text before or after it.
"""



template = "You are improving your underestanding of how making SPARQL queries for this dataset. Look carefully for chain of variables used for this question."
template = template + select_instruction

questions = tab1_df["Question"]
queries =  tab1_df["SPARQL"]
logic_steps = tab1_df["STEPS"]


graph = RdfGraph(
    source_file=  "app/triples/bmw_model_x_with_owner_info.nt", 
    standard="rdf",
    local_copy="test2.ttl",
)

import warnings
warnings.filterwarnings("ignore", message="does not look like a valid URI, trying to serialize this will break.")

graph.load_schema()
my_llm_chat = ChatOpenAI(temperature=0)

chain = GraphSparqlQAChain.from_llm(
    my_llm_chat, graph=graph, verbose=True
)

new_prompt = "" 


post_prompt2 = " now tell me: "

for  i in range(0,12): 
    steps_to_make_sparql = "steps to make the SPARQL query for this is: " + logic_steps[i]
    example_sparql_ = " ,therefore, a correct SPARQL query for Q:"+ questions[i] + " is: " + queries[i]
    new_prompt = new_prompt + steps_to_make_sparql + example_sparql_ + "\n"

post_prompt21 = " list all of answers instead of one. If they are more than 50, cut the rest. " first 10.
post_prompt22 = "Note: never include the SPARQL query in the answer." 
post_prompt2 = post_prompt21 + post_prompt22 +"  now tell me: "
 
@app.get("/chat/{user_text}")
async def read_chat(user_text:str):
    print(user_text)
    question2 = " " + user_text + "?"
    new_prompt2 =  new_prompt +post_prompt2  + question2
    print(new_prompt2)
    try:
        a = chain.run(new_prompt2)
        print(a)
    except Exception as inst:
        print(type(inst))    # the exception type
        print(inst.args)     # arguments stored in .args
        print(inst) 
        a = "Sorry, this question is out of scope of my current knowledge."
    return {"response": a }
