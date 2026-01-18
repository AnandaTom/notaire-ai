"""
Modal deployment for NotaireAI API
Serverless Python backend for notarial act generation
"""

import modal

# Define the Modal app
app = modal.App("notaire-ai")

# Create image with all dependencies
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "anthropic>=0.40.0",
    "jinja2>=3.1.0",
    "python-docx>=1.1.0",
    "pdfkit>=1.0.0",
    "pydantic>=2.0.0",
    "python-dotenv>=1.0.0",
    "supabase>=2.0.0",
)

# Volume for templates and clauses (synced from GitHub)
templates_volume = modal.Volume.from_name("notaire-templates", create_if_missing=True)


@app.function(
    image=image,
    volumes={"/app/templates": templates_volume},
    secrets=[modal.Secret.from_name("notaire-secrets")],
)
def generate_act(
    act_type: str,
    variables: dict,
    format: str = "pdf",
    clauses_conditionnelles: list[str] | None = None,
    clauses_optionnelles: list[str] | None = None,
) -> dict:
    """
    Generate a notarial act based on type and variables.

    Args:
        act_type: Type of act (e.g., "vente_immobiliere")
        variables: Dictionary of variables for the act
        format: Output format ("pdf" or "docx")
        clauses_conditionnelles: List of conditional clauses to include
        clauses_optionnelles: List of optional clauses to include

    Returns:
        Dictionary with status, file_url, and metadata
    """
    import os
    import json
    from jinja2 import Environment, FileSystemLoader

    # Load templates
    env = Environment(loader=FileSystemLoader("/app/templates"))

    # Assembly logic (simplified - uses execution scripts)
    from execution.assembler_acte import assemble_act
    from execution.valider_acte import validate_act

    # Generate the act
    html_content = assemble_act(
        act_type=act_type,
        variables=variables,
        clauses_conditionnelles=clauses_conditionnelles or [],
        clauses_optionnelles=clauses_optionnelles or [],
    )

    # Validate
    validation = validate_act(html_content, variables)
    if not validation["valid"]:
        return {"status": "error", "errors": validation["errors"]}

    # Export to requested format
    if format == "docx":
        from execution.exporter_docx import export_docx
        file_bytes = export_docx(html_content)
        content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        extension = "docx"
    else:
        from execution.exporter_pdf import export_pdf
        file_bytes = export_pdf(html_content)
        content_type = "application/pdf"
        extension = "pdf"

    # Return file (in production, upload to cloud storage)
    import base64
    return {
        "status": "success",
        "file_base64": base64.b64encode(file_bytes).decode(),
        "content_type": content_type,
        "filename": f"acte_{act_type}.{extension}",
    }


@app.function(
    image=image,
    secrets=[modal.Secret.from_name("notaire-secrets")],
)
def chat_with_notaire(
    messages: list[dict],
    context: dict | None = None,
) -> dict:
    """
    Chat endpoint for the NotaireAI assistant.
    Uses Claude to guide the notary through act creation.

    Args:
        messages: List of chat messages [{role, content}]
        context: Optional context (current act state, variables collected)

    Returns:
        Dictionary with response and updated context
    """
    import os
    from anthropic import Anthropic

    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    system_prompt = """Tu es NotaireAI, un assistant juridique spécialisé dans la rédaction d'actes notariaux pour le cabinet de Maître Charlotte Diaz.

Ton rôle :
1. Guider le notaire dans la collecte d'informations pour l'acte
2. Poser des questions précises et pertinentes
3. Proposer des clauses adaptées à la situation
4. Générer des actes conformes au droit français

Tu connais parfaitement :
- Le Code civil (articles relatifs aux ventes immobilières, donations, etc.)
- Les clauses obligatoires, conditionnelles et optionnelles
- Les bonnes pratiques notariales

Sois professionnel, précis et efficace. Utilise un langage juridique approprié tout en restant accessible."""

    if context:
        system_prompt += f"\n\nContexte actuel de l'acte :\n{json.dumps(context, ensure_ascii=False, indent=2)}"

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=system_prompt,
        messages=messages,
    )

    return {
        "response": response.content[0].text,
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        }
    }


@app.function(
    image=image,
    secrets=[modal.Secret.from_name("notaire-secrets")],
)
def sync_knowledge_base():
    """
    Sync improvements from Supabase to local knowledge base.
    Called periodically or on-demand.
    """
    import os
    from supabase import create_client

    supabase = create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_KEY"],
    )

    # Fetch approved improvements
    improvements = supabase.table("improvements").select("*").eq("status", "approved").execute()

    # Apply improvements to clauses/templates
    for improvement in improvements.data:
        if improvement["type"] == "new_clause":
            # Add new clause to the appropriate category
            pass
        elif improvement["type"] == "correction":
            # Apply correction to existing content
            pass

    return {"synced": len(improvements.data)}


@app.local_entrypoint()
def main():
    """Test the deployment locally."""
    # Test chat
    result = chat_with_notaire.remote(
        messages=[{"role": "user", "content": "Je souhaite créer un acte de vente immobilière."}]
    )
    print(f"Chat response: {result['response'][:200]}...")
    print(f"Tokens used: {result['usage']}")
