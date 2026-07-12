import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

def get_conversational_rag_chain(vector_store, get_session_history_func):
    """
    Builds and returns a conversational RAG chain using the persistent vector store.
    Uses gemini-2.0-flash for high quality response generation.
    """
    # 1. Initialize Gemini LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash",
        temperature=0.2,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )

    # 2. Define the retriever
    retriever = vector_store.as_retriever(search_kwargs={"k": 4})

    # 3. Build the prompt pipeline with system instructions and chat history
    system_prompt = (
        "You are an intelligent enterprise knowledge assistant. Answer the user's question "
        "using ONLY the following pieces of retrieved context. If you do not know the answer, "
        "say that you cannot find it in the documents. Do not hallucinate.\n\n"
        "Context:\n{context}"
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ])

    # 4. Create QA chain and retrieval chain
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    # 5. Add conversational history tracking
    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history_func,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )

    return conversational_rag_chain