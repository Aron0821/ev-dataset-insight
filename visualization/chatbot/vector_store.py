import pandas as pd
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings


def build_vector_store(db_connect):

    conn = db_connect()

    query = """
        SELECT
            v.vin,
            v.model_year,
            v.ev_type,
            v.electric_range,
            m.make,
            m.model,
            l.city,
            l.state,
            l.county,
            l.postal_code
        FROM vehicle v
        JOIN model m ON v.model_id = m.model_id
        JOIN location l ON v.location_id = l.location_id;
    """

    df = pd.read_sql(query, conn)
    conn.close()

    docs = []

    for _, row in df.iterrows():

        content = f"""
        VIN: {row.vin}
        Make: {row.make}
        Model: {row.model}
        Year: {row.model_year}
        EV Type: {row.ev_type}
        Range: {row.electric_range}
        City: {row.city}
        State: {row.state}
        County: {row.county}
        Postal Code: {row.postal_code}
        """

        docs.append(Document(page_content=content))

    embedding = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vector_db = FAISS.from_documents(docs, embedding)

    vector_db.save_local("ev_faiss_index")

    return vector_db
