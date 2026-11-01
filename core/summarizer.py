from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
import os
from dotenv import load_dotenv
load_dotenv()

# Initialize the ChatGroq instance
def get_llm_qwen():

    return ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model="openai/gpt-oss-120b",
        temperature=0.3,
        # max_tokens=2048,
    )
def get_llm_gpt():

    return ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model="openai/gpt-oss-120b",
        temperature=0.7,
        # max_tokens=2048,
    )

#text splitter
def split_transcript(transcript):
    # Split the transcript into chunks
    splitter = RecursiveCharacterTextSplitter(
    chunk_size=3000,
    chunk_overlap=200
    
    )

    return splitter.split_text(transcript)


def summarize(transcript):
    # Initialize the ChatGroq instance
    llm = get_llm_qwen()

    map_prompt=ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that summarizes text concisely .Remember that text may be of podcast or teaching lecture or may be a meeting transcript. Your task is to summarize the text in a concise manner without losing the key points."),
        ("user", "Summarize the following text: {text}")
    ]

    )
    #build chain
    map_chain= map_prompt | llm | StrOutputParser()


    # Split the transcript into chunks
    chunks = split_transcript(transcript)

    # Process each chunk
    chunk_summaries = [map_chain.invoke({"text":chunk}) for chunk in chunks]

    # Combine the summaries
    combined = "\n\n".join(chunk_summaries)

    

    combined_prompt=ChatPromptTemplate.from_messages([
        ("system", "You are the expert summarizer. Combine these partial summaries into a brilliant summary of a thing. It may be a podcast, teaching lecture, or meeting transcript. You are excellent at your job, so do it. Remember to keep the key points and make it concise."),
        ("user", "{text}")
    ])
    

    combined_chain = (
        RunnablePassthrough() | RunnableLambda(lambda x: {"text": x}) | combined_prompt | llm | StrOutputParser()
    )

    return combined_chain.invoke(combined)


def generate_title(transcript):
    # Initialize the ChatGroq instance
    llm = get_llm_qwen()

    prompt=ChatPromptTemplate.from_messages([
        ("system", "Based on the meeting transcription, the podcast summary, or etc., whatever it is, generate a short professional title for that. Max words would be 8 words only. Write the title, nothing else. "),
        ("user", "{text}")
    ])


    title_chain=(
        RunnablePassthrough() | RunnableLambda(lambda x: {"text": x}) | prompt | llm | StrOutputParser()

    )

    return title_chain.invoke(transcript[:2000])




