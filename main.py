from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from assistant import Trip
from functions import tools, INSTRUCTION
import uvicorn

app = FastAPI( title="Ask Pak tour API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


ai_travel = Trip()
ai_travel_assistant = ai_travel.create_assistant(
    name="AI Travel Assistant",
    instructions=INSTRUCTION,
    tools=tools,
)


class UserMessage(BaseModel):
    message: str

@app.post("/chat")
async def chat(user_message: UserMessage):

    thread = ai_travel.create_thread()


    ai_travel.add_message_to_thread(
        thread=thread,
        content=user_message.message,
        role="user"
    )


    run = ai_travel.create_run(
        thread=thread,
        instructions=INSTRUCTION
    )


    final_res = ai_travel.get_run_result(
        run=run,
        thread=thread
    )


    assistant_responses = [
        m.content[0].text.value
        for m in reversed(final_res["messages"].data)
        if m.role == "assistant"
    ]

    if assistant_responses:
        response_text = assistant_responses[0]
    else:
        response_text = "I'm sorry, I couldn't process your request."

    return {
        "response": response_text,
        "function_outputs": final_res["function_outputs"]
    }


if __name__ == "__main__":
    # Run the API using uvicorn on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)