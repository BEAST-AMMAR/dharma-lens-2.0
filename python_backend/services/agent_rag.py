import sys
import os
import json
import pydantic
from typing import Dict, TypedDict, Annotated, Sequence

# LangChain Core / LangGraph Pydantic v1 compatibility shim
try:
    import langchain_core
    try:
        import pydantic.v1 as pydantic_v1
    except ImportError:
        pydantic_v1 = pydantic
    sys.modules['langchain_core.pydantic_v1'] = pydantic_v1
except Exception as _lc_err:
    pass

import networkx as nx
from langgraph.graph import StateGraph, END
from pydantic import BaseModel

class AgentState(TypedDict):
    document_text: str
    query: str
    reformulated_query: str
    requires_constitutional: bool
    requires_criminal: bool
    vector_results: list
    graph_results: list
    final_analysis: dict
    config: dict

# ──────────────────────────────────────────────────────────────────
# DYNAMIC LEGAL GRAPH — Expanded IPC<->BNS<->BNSS<->BSA statutory mappings
# ──────────────────────────────────────────────────────────────────
legal_graph = nx.DiGraph()

def init_legal_graph():
    """Build dynamic NetworkX knowledge graph for IPC<->BNS<->BNSS<->BSA statutory relationships."""
    legal_graph.clear()
    
    # ── IPC <-> BNS Mappings (Criminal Law) ──
    ipc_bns_mappings = [
        ("IPC_302", "BNS_103", "Murder", "Punishment for Murder"),
        ("IPC_378", "BNS_303", "Theft", "Theft"),
        ("IPC_420", "BNS_318", "Cheating", "Cheating and dishonestly inducing delivery of property"),
        ("IPC_376", "BNS_64", "Rape", "Punishment for Rape"),
        ("IPC_304A", "BNS_106", "Death by Negligence", "Causing death by negligence"),
        ("IPC_498A", "BNS_85", "Cruelty by Husband", "Cruelty by husband or relatives of husband"),
        ("IPC_354", "BNS_74", "Assault on Woman", "Assault or criminal force to woman with intent to outrage her modesty"),
        ("IPC_506", "BNS_351", "Criminal Intimidation", "Criminal intimidation"),
        ("IPC_34", "BNS_3_5", "Common Intention", "Acts done by several persons in furtherance of common intention"),
        ("IPC_120B", "BNS_61", "Criminal Conspiracy", "Criminal conspiracy"),
    ]
    
    for ipc_id, bns_id, short_title, full_title in ipc_bns_mappings:
        legal_graph.add_node(ipc_id, type="section", title=short_title, full_title=full_title, act="IPC")
        legal_graph.add_node(bns_id, type="section", title=short_title, full_title=full_title, act="BNS")
        legal_graph.add_edge(ipc_id, bns_id, relation="SUPERSEDED_BY")
        legal_graph.add_edge(bns_id, ipc_id, relation="REPLACES")
    
    # ── CrPC <-> BNSS Mappings (Procedural Law) ──
    crpc_bnss_mappings = [
        ("CrPC_154", "BNSS_173", "FIR", "Information in cognizable cases"),
        ("CrPC_161", "BNSS_180", "Examination of Witnesses", "Examination of witnesses by police"),
        ("CrPC_41", "BNSS_35", "Arrest without Warrant", "When police may arrest without warrant"),
        ("CrPC_438", "BNSS_482", "Anticipatory Bail", "Direction for grant of bail to person apprehending arrest"),
        ("CrPC_482", "BNSS_528", "Inherent Powers", "Saving of inherent powers of High Court"),
    ]
    
    for crpc_id, bnss_id, short_title, full_title in crpc_bnss_mappings:
        legal_graph.add_node(crpc_id, type="section", title=short_title, full_title=full_title, act="CrPC")
        legal_graph.add_node(bnss_id, type="section", title=short_title, full_title=full_title, act="BNSS")
        legal_graph.add_edge(crpc_id, bnss_id, relation="SUPERSEDED_BY")
        legal_graph.add_edge(bnss_id, crpc_id, relation="REPLACES")

    # ── Constitutional Articles ──
    constitutional_articles = [
        ("Article_14", "Equality Before Law", "The State shall not deny to any person equality before the law"),
        ("Article_19", "Freedom of Speech", "All citizens shall have the right to freedom of speech and expression"),
        ("Article_20", "Protection against Conviction", "No person shall be convicted except for violation of a law in force"),
        ("Article_21", "Right to Life", "No person shall be deprived of life or personal liberty except according to procedure established by law"),
        ("Article_22", "Protection against Arrest", "No person who is arrested shall be detained without being informed of grounds"),
        ("Article_32", "Right to Constitutional Remedies", "The right to move the Supreme Court for enforcement of fundamental rights"),
        ("Article_226", "Power of High Courts", "Power of High Courts to issue certain writs"),
    ]
    
    for art_id, title, content in constitutional_articles:
        legal_graph.add_node(art_id, type="article", title=title, content=content, act="Constitution")
    
    # ── Constitutional Review Edges ──
    constitutional_review_edges = [
        ("BNS_103", "Article_21"), ("BNS_64", "Article_21"),
        ("BNS_303", "Article_14"), ("BNS_318", "Article_14"),
        ("BNS_85", "Article_21"), ("BNS_74", "Article_21"),
        ("BNSS_35", "Article_22"), ("BNSS_482", "Article_21"),
        ("BNSS_173", "Article_21"),
    ]
    
    for statute, article in constitutional_review_edges:
        if legal_graph.has_node(statute) and legal_graph.has_node(article):
            legal_graph.add_edge(statute, article, relation="SUBJECT_TO_CONSTITUTIONAL_REVIEW")

init_legal_graph()

def router_node(state: AgentState) -> AgentState:
    """
    Router Agent: Determines if document requires Constitutional or Criminal Law analysis,
    and reformulates raw document into a focused legal query.
    """
    print("[Agentic RAG] Router Node analyzing document context...")
    from services.ai_pipeline import call_llm_hybrid
    
    text = state["document_text"][:2500]
    config = state.get("config", {})
    
    system_prompt = (
        "You are a legal document router and query reformulator. "
        "Analyze the input text and return a JSON object with EXACTLY these keys:\n"
        "{\n"
        '  "requires_constitutional": true/false,\n'
        '  "requires_criminal": true/false,\n'
        '  "reformulated_query": "Focused 1-sentence legal question representing key issues"\n'
        "}"
    )
    user_prompt = f"Analyze this text:\n\n{text}"
    
    try:
        res = call_llm_hybrid(system_prompt, user_prompt, is_json=True, config=config)
        state["requires_constitutional"] = res.get("requires_constitutional", True)
        state["requires_criminal"] = res.get("requires_criminal", True)
        state["reformulated_query"] = res.get("reformulated_query", text[:300])
    except Exception as e:
        print(f"[Router Node Error]: {e}")
        state["requires_constitutional"] = True
        state["requires_criminal"] = True
        state["reformulated_query"] = text[:300]
        
    return state

def vector_retrieval_node(state: AgentState) -> AgentState:
    """
    Hybrid Retrieval Agent: Queries Supabase using hybrid search (BM25 + pgvector)
    with sentence-transformer CPU embeddings. Falls back to graph-only if vector store is empty.
    """
    print("[Agentic RAG] Hybrid Retriever searching Supabase pgvector...")
    query = state.get("reformulated_query") or state["document_text"][:500]
    
    vector_results = []
    try:
        from services.ingest_law import model, supabase
        query_embedding = model.encode(query).tolist()
        
        rpc_res = supabase.rpc("hybrid_search_legal_knowledge", {
            "query_text": query,
            "query_embedding": query_embedding,
            "match_count": 5,
            "full_text_weight": 1.0,
            "semantic_weight": 1.0
        }).execute()
        
        if rpc_res.data:
            for row in rpc_res.data:
                vector_results.append({
                    "id": str(row.get("id", "")),
                    "source_type": row.get("source_type"),
                    "section": f"{row.get('source_type')} {row.get('section_number')}",
                    "section_number": row.get("section_number"),
                    "title": row.get("title"),
                    "content": row.get("content"),
                    "similarity": round(float(row.get("similarity", 0.9)), 3),
                    "superseded_by": row.get("superseded_by"),
                    "replaces": row.get("replaces")
                })
            print(f"[Vector Retrieval] Found {len(vector_results)} real results from Supabase pgvector.")
        else:
            print("[Vector Retrieval] Supabase returned 0 results. Legal knowledge table may be empty — run ingest_law.py first.")
    except Exception as e:
        print(f"[Vector Retrieval Warning]: {e}. Proceeding with graph-only analysis.")

    # If vector store is empty, note it clearly — NO synthetic mock data injected
    if not vector_results:
        print("[Vector Retrieval] WARNING: No vector results available. Analysis will rely on graph traversal and LLM reasoning only.")
        
    state["vector_results"] = vector_results
    return state

def graph_retrieval_node(state: AgentState) -> AgentState:
    """
    Graph Retrieval Agent: Traverses NetworkX statutory graph for IPC<->BNS<->BNSS transition mappings
    and constitutional review relationships. Performs intelligent matching against document text.
    """
    print("[Agentic RAG] Graph Retriever traversing NetworkX legal graph...")
    graph_results = []
    
    doc_text = state["document_text"][:5000].upper()
    
    # Collect all relevant graph edges based on document content and routing flags
    for u, v, data in legal_graph.edges(data=True):
        relation = data.get("relation")
        
        # Check if this graph edge is relevant to the document text
        u_label = u.replace("_", " ").replace("IPC ", "IPC Section ").replace("BNS ", "BNS Section ")
        v_label = v.replace("_", " ").replace("IPC ", "IPC Section ").replace("BNS ", "BNS Section ")
        
        # Match if the section/article is mentioned in the document text
        u_mentioned = u.replace("_", " ") in doc_text or u.replace("_", "") in doc_text
        v_mentioned = v.replace("_", " ") in doc_text or v.replace("_", "") in doc_text
        
        is_relevant_criminal = state["requires_criminal"] and relation in ("SUPERSEDED_BY", "REPLACES")
        is_relevant_constitutional = state["requires_constitutional"] and relation == "SUBJECT_TO_CONSTITUTIONAL_REVIEW"
        
        if (u_mentioned or v_mentioned) or is_relevant_criminal or is_relevant_constitutional:
            u_node = legal_graph.nodes.get(u, {})
            v_node = legal_graph.nodes.get(v, {})
            
            if relation == "SUPERSEDED_BY":
                graph_results.append({
                    "relationship": f"{u.replace('_', ' ')} ({u_node.get('title', '')}) is superseded by {v.replace('_', ' ')} ({v_node.get('title', '')})",
                    "old_section": u.replace("_", " "),
                    "new_section": v.replace("_", " "),
                    "old_act": u_node.get("act"),
                    "new_act": v_node.get("act"),
                    "relation_type": "SUPERSEDED_BY"
                })
            elif relation == "SUBJECT_TO_CONSTITUTIONAL_REVIEW":
                graph_results.append({
                    "relationship": f"{u.replace('_', ' ')} is subject to Constitutional Review under {v.replace('_', ' ')} ({v_node.get('title', '')})",
                    "statute": u.replace("_", " "),
                    "constitutional_article": v.replace("_", " "),
                    "article_title": v_node.get("title"),
                    "relation_type": "CONSTITUTIONAL_REVIEW"
                })
    
    # Deduplicate by relationship text
    seen = set()
    unique_results = []
    for r in graph_results:
        key = r["relationship"]
        if key not in seen:
            seen.add(key)
            unique_results.append(r)
    
    state["graph_results"] = unique_results
    print(f"[Graph Retrieval] Found {len(unique_results)} statutory relationships.")
    return state

def synthesizer_node(state: AgentState) -> AgentState:
    """
    Synthesizer Agent: Compiles vector context, graph relationships, and document text
    into a structured JSON legal analysis report with verified citations.
    """
    print("[Agentic RAG] Synthesizer compiling report...")
    from services.ai_pipeline import call_llm_hybrid
    
    text = state["document_text"][:5000]
    config = state.get("config", {})
    
    system_prompt = """You are an expert Indian Legal AI. Synthesize a comprehensive legal analysis based on the document text and the provided retrieval context (Vector Search & Knowledge Graph). 
    Return a JSON object with EXACTLY this schema:
    {
        "constitutional_principles": ["list of constitutional articles/principles relevant to this document"],
        "relevant_articles": [{"section": "...", "content": "..."}],
        "graph_relationships": ["list of statutory relationships like IPC to BNS mappings"],
        "potential_violations": ["list of potential legal violations or issues identified"]
    }"""
    
    context = (
        f"Document Text Snippet:\n{text}\n\n"
        f"Reformulated Query: {state.get('reformulated_query')}\n\n"
        f"Vector Search Results:\n{json.dumps(state['vector_results'], indent=2)}\n\n"
        f"Graph Traversals:\n{json.dumps(state['graph_results'], indent=2)}"
    )
    
    try:
        analysis = call_llm_hybrid(system_prompt, context, is_json=True, config=config)
        state["final_analysis"] = {
            "constitutional_principles": analysis.get("constitutional_principles", []),
            "relevant_articles": analysis.get("relevant_articles", state["vector_results"]),
            "graph_relationships": analysis.get("graph_relationships", [g["relationship"] for g in state["graph_results"] if "relationship" in g]),
            "potential_violations": analysis.get("potential_violations", []),
            "citations": state["vector_results"]
        }
    except Exception as e:
        print(f"[Synthesizer Error]: {e}")
        state["final_analysis"] = {
            "constitutional_principles": [
                "Article 21 - Right to Life and Personal Liberty"
            ] if state["requires_constitutional"] else [],
            "relevant_articles": state["vector_results"],
            "graph_relationships": [g.get("relationship", str(g)) for g in state["graph_results"]],
            "potential_violations": [],
            "citations": state["vector_results"]
        }
    
    return state

# Build the LangGraph
workflow = StateGraph(AgentState)

workflow.add_node("router", router_node)
workflow.add_node("vector_retriever", vector_retrieval_node)
workflow.add_node("graph_retriever", graph_retrieval_node)
workflow.add_node("synthesizer", synthesizer_node)

workflow.set_entry_point("router")
workflow.add_edge("router", "vector_retriever")
workflow.add_edge("vector_retriever", "graph_retriever")
workflow.add_edge("graph_retriever", "synthesizer")
workflow.add_edge("synthesizer", END)

legal_agent_app = workflow.compile()

def run_agentic_rag(document_text: str, config: dict = None):
    """
    Execute the Multi-Agent RAG Pipeline
    """
    initial_state = {
        "document_text": document_text,
        "query": "",
        "reformulated_query": "",
        "requires_constitutional": False,
        "requires_criminal": False,
        "vector_results": [],
        "graph_results": [],
        "final_analysis": {},
        "config": config or {}
    }
    
    final_state = legal_agent_app.invoke(initial_state)
    return final_state["final_analysis"]
