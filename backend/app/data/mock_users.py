MOCK_USERS: dict[str, dict] = {
    "user-1": {
        "name": "Maria Souza",
        "account": {
            "bank_name": "Banco Getnet",
            "agency": "0001",
            "account_number": "123456-7",
            "pix_key": "maria.souza@example.com",
            "pix_key_type": "email",
        },
        "settlement": {
            "schedule_description": "Vendas no débito caem em 1 dia útil; vendas no crédito à vista em 14 dias corridos.",
            "next_deposit_date": "2026-08-25",
            "next_deposit_amount": 842.50,
        },
        "device": {
            "model": "Get Smart",
            "connectivity_status": "offline",
            "connectivity_detail": "Sem sinal Wi-Fi/4G há 2 horas. Último uso: chip de dados.",
            "last_seen": "2026-08-23T10:15:00-03:00",
        },
        "transactions": [
            {
                "id": "txn-9001",
                "status": "declined",
                "amount": 1200.00,
                "date": "2026-08-22T18:32:00-03:00",
                "decline_reason": "Saldo/limite insuficiente no cartão do cliente.",
            },
            {
                "id": "txn-9002",
                "status": "approved",
                "amount": 89.90,
                "date": "2026-08-23T09:05:00-03:00",
                "decline_reason": None,
            },
        ],
        "installments": {
            "product": "crediário",
            "max_installments": 12,
            "current_plan": "6x de R$ 150,00 sem juros para o cliente; taxa de 4,5% ao mês para o lojista.",
        },
    },
    "user-2": {
        "name": "João Pereira",
        "account": {
            "bank_name": "Banco Getnet",
            "agency": "0001",
            "account_number": "765432-1",
            "pix_key": "+5511999998888",
            "pix_key_type": "telefone",
        },
        "settlement": {
            "schedule_description": "Vendas no débito caem em 1 dia útil; vendas no crédito parcelado em até 30 dias corridos.",
            "next_deposit_date": "2026-08-24",
            "next_deposit_amount": 2310.00,
        },
        "device": {
            "model": "Get Clássica",
            "connectivity_status": "online",
            "connectivity_detail": "Conectada via Wi-Fi, última transação há 10 minutos.",
            "last_seen": "2026-08-23T11:40:00-03:00",
        },
        "transactions": [
            {
                "id": "txn-8001",
                "status": "approved",
                "amount": 350.00,
                "date": "2026-08-23T08:00:00-03:00",
                "decline_reason": None,
            }
        ],
        "installments": {
            "product": "crediário",
            "max_installments": 10,
            "current_plan": "10x de R$ 90,00 sem juros para o cliente; taxa de 5,2% ao mês para o lojista.",
        },
    },
}


def get_user(user_id: str) -> dict | None:
    return MOCK_USERS.get(user_id)
