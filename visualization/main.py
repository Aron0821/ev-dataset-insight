from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from text_to_sql import nl_to_sql, clean_sql, execute_sql, build_interpretation_prompt, interprate_final_result
import uvicorn
app = FastAPI()

# ------------------ REQUEST SCHEMA ------------------
class QueryRequest(BaseModel):
    question: str
@app.post("/query")
def query_db(payload: QueryRequest):
    try:
        userquery = payload.question
        raw_sql = nl_to_sql(userquery)
        sql = clean_sql(raw_sql)
        result = execute_sql(sql)
        interpretation_prompt = build_interpretation_prompt(userquery, result)

        final_answer = interprate_final_result(interpretation_prompt)

        return {
            "question": payload.question,
            "sql": sql,
            "result": result,
            "answer": final_answer
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__=="__main__":
    uvicorn.run("main:app", host="0.0.0.0" , port=8000,reload=False)