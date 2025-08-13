import os
import asyncio
import streamlit as st
from dotenv import load_dotenv
from agents import (
    AsyncOpenAI, OpenAIChatCompletionsModel, Agent, Runner, input_guardrail,
    GuardrailFunctionOutput, output_guardrail,
    InputGuardrailTripwireTriggered, OutputGuardrailTripwireTriggered,
    RunContextWrapper
)
from pydantic import BaseModel
from dataclasses import dataclass


load_dotenv()

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"


class IllegalAndIrrelevant(BaseModel):
    is_request_irrelevant_illegal: bool
    reasoning: str

class ControlBookingCriteria(BaseModel):
    is_response_violates: bool
    reasoning: str

class MessageOutput(BaseModel):
    response: str

@dataclass
class UserInfo:
    name: str
    age: int
    departure_city: str
    budget: float
    travel_history: list[str]


async def run_travel_agent(chat_history):
    
    client = AsyncOpenAI(api_key=GEMINI_KEY, base_url=BASE_URL)

    
    premium_model = OpenAIChatCompletionsModel(
        openai_client=client, model="gemini-2.5-flash"
    )
    
    basic_model = OpenAIChatCompletionsModel(
        openai_client=client, model="gemini-2.0-flash"
    )

    
    illegal_and_irrelevant_input_guardrail = Agent(
        name="input guardrail agent",
        instructions="""
        You are an input guardrail agent. Your job is to decide whether the user's request is:
        - asking to book travel to an illegal/unsafe/restricted destination,
        - OR the message is clearly irrelevant or offensive.
        Return:
          is_request_irrelevant_illegal: bool
          reasoning: short explanation
        """,
        model=basic_model,
        output_type=IllegalAndIrrelevant
    )

    
    control_booking_output_guardrail = Agent(
        name="output guardrail agent",
        instructions="""
        You are an output guardrail agent. Inspect the assistant's reply text and decide:
        - Does it give medical/legal advice? (flag)
        - OR confirm a booking without showing cost? (flag)
        Return:
          is_response_violates: bool
          reasoning: short explanation
        """,
        model=basic_model,
        output_type=ControlBookingCriteria
    )

    
    @input_guardrail
    async def illegal_irrelevant(ctx: RunContextWrapper[UserInfo], agent, user_input):
        result = await Runner.run(
            starting_agent=illegal_and_irrelevant_input_guardrail,
            input=user_input,
            context=ctx.context
        )
        return GuardrailFunctionOutput(
            output_info=result.final_output,
            tripwire_triggered=result.final_output.is_request_irrelevant_illegal
        )

    
    
    @output_guardrail
    async def check_booking(ctx: RunContextWrapper[UserInfo], agent, output: MessageOutput):
        result = await Runner.run(
            starting_agent=control_booking_output_guardrail,
            input=output.response,
            context=ctx.context
        )
        return GuardrailFunctionOutput(
            output_info=result.final_output,
            tripwire_triggered=result.final_output.is_response_violates
        )

    
    
    Travel_Booking_Assistant_Agent = Agent(
        name="travel booking agent",
        instructions="""
        You are a travel booking assistant. Help the user find and summarize flight & hotel options,
        explain costs clearly, and guide them through booking steps.
        Maintain context from the entire conversation history provided.
        """,
        model=premium_model,
        input_guardrails=[illegal_irrelevant],
        output_guardrails=[check_booking],
        output_type=MessageOutput,
    )

    
    user_info = UserInfo(
        name="Mark Willson",
        age=45,
        departure_city="Tokyo",
        budget=180.4,
        travel_history=["China", "UAE", "Iran", "India"]
    )

    
    # Combine full conversation into one prompt
    conversation = ""
    for msg in chat_history:
        role = "User" if msg["role"] == "user" else "Agent"
        conversation += f"{role}: {msg['content']}\n"

    
    
    try:
        result = await Runner.run(
            starting_agent=Travel_Booking_Assistant_Agent,
            input=conversation.strip(),
            context=user_info
        )
        return {"status": "success", "response": result.final_output.response}

    
    except InputGuardrailTripwireTriggered:
        return {"status": "blocked_input", "reason": "Illegal or irrelevant request."}

    
    except OutputGuardrailTripwireTriggered:
        return {"status": "blocked_output", "reason": "Blocked for safety (medical/legal advice or missing cost)."}




# ----- Streamlit Chat UI -----
st.set_page_config(page_title="✈️ Travel Booking Assistant", layout="centered")


st.title("Travel Booking Assistant")
st.markdown("Chat with your **AI Travel Agent**")
st.markdown("Now with continuous conversation & safety guardrails.")


# Sidebar with profile
st.sidebar.header("👤 User Profile")
st.sidebar.write("**Name:** Mark Willson")
st.sidebar.write("**Age:** 45")
st.sidebar.write("**Departure City:** Tokyo")
st.sidebar.write("**Budget:** $180.4")
st.sidebar.write("**Travel History:**")
for country in ["China", "UAE", "Iran", "India"]:
    st.sidebar.write(f"{country}")



# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


# Display chat history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"<div style='text-align:right; background-color:#d1e7dd; padding:10px; border-radius:10px; margin:5px 0;'><b>You:</b> {msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='text-align:left; background-color:#f8f9fa; padding:10px; border-radius:10px; margin:5px 0;'><b>Agent:</b> {msg['content']}</div>", unsafe_allow_html=True)



# Input form at bottom
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Type your message:", "")
    submit = st.form_submit_button("Send")


if submit and user_input.strip():
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.spinner("Agent is thinking..."):
        result = asyncio.run(run_travel_agent(st.session_state.messages))

    if result["status"] == "success":
        st.session_state.messages.append({"role": "agent", "content": result["response"]})
    elif result["status"] == "blocked_input":
        st.session_state.messages.append({"role": "agent", "content": f"Request Blocked: {result['reason']}"} )
    elif result["status"] == "blocked_output":
        st.session_state.messages.append({"role": "agent", "content": f"Response Blocked: {result['reason']}"} )

    st.rerun()
