SUPPORT_TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_settlement_schedule",
            "description": "Consulta o prazo e valor do próximo depósito das vendas do lojista.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_transaction_status",
            "description": "Consulta as transações recentes do lojista, incluindo status e motivo de recusa.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_device_status",
            "description": "Consulta o status de conectividade da maquininha do lojista (online/offline).",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_account_info",
            "description": "Consulta os dados da conta bancária do lojista, incluindo a chave Pix cadastrada.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_installment_plan",
            "description": "Consulta o plano de parcelamento do crediário do lojista.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]

SUPPORT_TOOL_NAMES = [schema["function"]["name"] for schema in SUPPORT_TOOL_SCHEMAS]


def execute_support_tool(tool_name: str, user_data: dict) -> dict:
    """Look up mocked data for the requesting user only. `tool_name`
    always comes from the LLM's structured tool call; `user_data` is
    resolved server-side from the request's user_id, never from the LLM,
    so a tool can never read another user's data."""
    if tool_name == "get_settlement_schedule":
        return user_data["settlement"]
    if tool_name == "get_transaction_status":
        return {"transactions": user_data["transactions"]}
    if tool_name == "get_device_status":
        return user_data["device"]
    if tool_name == "get_account_info":
        return user_data["account"]
    if tool_name == "get_installment_plan":
        return user_data["installments"]
    raise ValueError(f"Unknown support tool: {tool_name}")
