from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from langchain_anthropic import ChatAnthropic


def configure_graph(state_class, chatbot_node, tool_node):
    graph_builder = StateGraph(state_class)
    llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")
    
    # Node configuration
    graph_builder.add_node("chatbot", chatbot_node(llm))
    graph_builder.add_node("tools", tool_node)
    
    graph_builder.set_entry_point("chatbot")
    graph_builder.set_finish_point("chatbot")
    
    def route_tools(state):
        if isinstance(state, list):
            ai_message = state[-1]
        elif messages := state.get("messages", []):
            ai_message = messages[-1]
        else:
            raise ValueError(f"No messages found in input state to tool_edge: {state}")
        
        if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
            return "tools"
        
        return END
    
    # Conditional routing
    graph_builder.add_conditional_edges(
        "chatbot",
        route_tools,
        {"tools": "tools", END: END},
    )
    
    # Edges configuration
    graph_builder.add_edge("tools", "chatbot")
    graph_builder.add_edge(START, "chatbot")
    
    return graph_builder.compile(
        checkpointer=MemorySaver()
        )