"""Connessione al server MCP ufficiale di Trello (M4·L8), con login OAuth.

Il server è quello del fornitore, in cloud: https://mcp.trello.com/v1
(trasporto Streamable HTTP). Il login lo fa il client, cioè questo file:

1. la prima richiesta riceve 401;
2. il client si registra da solo sul server di autorizzazione
   (registrazione dinamica) e apre il browser sulla pagina di consenso;
3. tu scegli il workspace e accetti;
4. Trello rimanda il browser a http://localhost:3030/callback con un codice;
5. il client scambia il codice con un token e lo salva in .mcp-token/.

Dalla seconda volta il token viene letto da .mcp-token/ e il browser non si apre.
La cartella .mcp-token/ è nel .gitignore: il token vale come una password.
"""

import asyncio
import json
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

from agents.mcp import MCPServerStreamableHttp
from mcp.client.auth import OAuthClientProvider, TokenStorage
from mcp.shared.auth import OAuthClientInformationFull, OAuthClientMetadata, OAuthToken

from config import CONFIG

URL_TRELLO = "https://mcp.trello.com/v1"
PORTA = 3030
REDIRECT_URI = f"http://localhost:{PORTA}/callback"


class TokenSuFile(TokenStorage):
    """Salva token e registrazione del client in due file JSON in .mcp-token/."""

    def __init__(self) -> None:
        self.cartella = CONFIG["mcp_token_dir"]
        self.cartella.mkdir(exist_ok=True)
        self.file_token = self.cartella / "trello-token.json"
        self.file_client = self.cartella / "trello-client.json"

    async def get_tokens(self) -> OAuthToken | None:
        if self.file_token.exists():
            return OAuthToken.model_validate_json(self.file_token.read_text(encoding="utf-8"))
        return None

    async def set_tokens(self, tokens: OAuthToken) -> None:
        self.file_token.write_text(tokens.model_dump_json(), encoding="utf-8")

    async def get_client_info(self) -> OAuthClientInformationFull | None:
        if self.file_client.exists():
            return OAuthClientInformationFull.model_validate_json(
                self.file_client.read_text(encoding="utf-8")
            )
        return None

    async def set_client_info(self, client_info: OAuthClientInformationFull) -> None:
        self.file_client.write_text(client_info.model_dump_json(), encoding="utf-8")


async def apri_browser(url: str) -> None:
    print("\n  [trello] Login: si apre il browser sulla pagina di consenso di Trello.")
    print(f"  [trello] Se non si apre, copia questo indirizzo nel browser:\n  {url}\n")
    webbrowser.open(url)


def _ricevi_callback() -> dict[str, str]:
    """Server HTTP minimo su localhost:3030: aspetta UNA richiesta /callback."""
    ricevuto: dict[str, str] = {}

    class Gestore(BaseHTTPRequestHandler):
        def do_GET(self):
            parametri = parse_qs(urlparse(self.path).query)
            for chiave in ("code", "state", "iss", "error", "error_description"):
                if chiave in parametri:
                    ricevuto[chiave] = parametri[chiave][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            esito = "Login completato" if "code" in ricevuto else "Login non riuscito"
            self.wfile.write(
                f"<h2>OnTheRoad AI: {esito}.</h2><p>Puoi chiudere questa scheda.</p>".encode()
            )

        def log_message(self, *args):  # niente log HTTP nel terminale
            pass

    server = HTTPServer(("localhost", PORTA), Gestore)
    try:
        while "code" not in ricevuto and "error" not in ricevuto:
            server.handle_request()  # ignora richieste estranee (es. favicon)
    finally:
        server.server_close()
    return ricevuto


async def aspetta_codice():
    ricevuto = await asyncio.to_thread(_ricevi_callback)
    if "error" in ricevuto:
        raise RuntimeError(
            f"Login Trello rifiutato: {ricevuto['error']} {ricevuto.get('error_description', '')}"
        )
    print("  [trello] codice ricevuto, scambio con il token…")
    try:  # SDK mcp recente: un oggetto con code, state, iss
        from mcp.shared.auth import AuthorizationCodeResult

        return AuthorizationCodeResult(
            code=ricevuto["code"], state=ricevuto.get("state"), iss=ricevuto.get("iss")
        )
    except ImportError:  # SDK mcp meno recente: una coppia (code, state)
        return ricevuto["code"], ricevuto.get("state")


def server_trello(**opzioni) -> MCPServerStreamableHttp:
    """Il server MCP di Trello, pronto per `async with server_trello() as trello:`."""
    auth = OAuthClientProvider(
        server_url=URL_TRELLO,
        client_metadata=OAuthClientMetadata(
            client_name="OnTheRoad AI",
            redirect_uris=[REDIRECT_URI],
            grant_types=["authorization_code", "refresh_token"],
            response_types=["code"],
            token_endpoint_auth_method="none",
        ),
        storage=TokenSuFile(),
        redirect_handler=apri_browser,
        callback_handler=aspetta_codice,
    )
    return MCPServerStreamableHttp(
        params={"url": URL_TRELLO, "auth": auth, "timeout": 30},
        name="trello",
        client_session_timeout_seconds=30,
        cache_tools_list=True,
        **opzioni,
    )


def testo(risultato) -> str:
    """Il testo di una risposta di call_tool (i server rispondono con blocchi di testo)."""
    return "\n".join(b.text for b in risultato.content if getattr(b, "text", None))


# --- Card delle richieste (M4·L8-L9) ----------------------------------------
# Le chiama il codice, non il modello: dopo l'approvazione la card va creata
# sempre, una volta sola. Il modello non vede i tool di Trello.


async def _chiama(trello, tool: str, argomenti: dict) -> dict:
    risultato = await trello.call_tool(tool, argomenti)
    contenuto = testo(risultato)
    if getattr(risultato, "isError", False):
        raise RuntimeError(f"{tool}: {contenuto}")
    return json.loads(contenuto)


async def trova_lista(trello, nome_board: str, nome_lista: str) -> tuple[str, str]:
    """Gli id (ARI) della board e della lista, cercati per nome: niente id scritti nel codice."""
    trovate = await _chiama(trello, "trelloSearch", {"action": "search_boards", "query": nome_board})
    board = next((b for b in trovate.get("boards", []) if b["name"] == nome_board), None)
    if board is None:
        raise RuntimeError(f"board '{nome_board}' non trovata su Trello")
    dettaglio = await _chiama(trello, "trelloReadBoard", {"action": "get", "boardId": board["id"]})
    lista = next((l for l in dettaglio.get("lists", []) if l["name"] == nome_lista), None)
    if lista is None:
        raise RuntimeError(f"lista '{nome_lista}' non trovata nella board '{nome_board}'")
    return board["id"], lista["id"]


async def card_esistente(trello, board_id: str, prefisso: str) -> dict | None:
    """Idempotenza: cerca tra TUTTE le card della board (anche archiviate) una che
    inizia con il prefisso, es. '#3 '. Se c'è, la richiesta ha già la sua card."""
    argomenti = {"action": "list_by_board", "boardIdOrUrl": board_id, "filter": "all"}
    while True:
        pagina = await _chiama(trello, "trelloReadCard", argomenti)
        for lista in pagina.get("lists", []):
            for card in lista.get("cards", []):
                if card.get("name", "").startswith(prefisso):
                    return card
        if not pagina.get("hasNextPage"):
            return None
        argomenti["cursor"] = pagina["nextCursor"]


async def crea_card_richiesta(
    trello, numero: int, titolo_itinerario: str, pacchetto: str,
    prezzo: int, nome: str, email: str, messaggio: str,
) -> str:
    """Crea la card della richiesta n. `numero` nella lista Nuove, se non c'è già.
    Restituisce una riga di esito per il terminale e per il modello."""
    board_id, lista_id = await trova_lista(
        trello, CONFIG["trello_board"], CONFIG["trello_lista_nuove"]
    )
    prefisso = f"#{numero} "
    gia = await card_esistente(trello, board_id, prefisso)
    if gia is not None:
        return f"card già presente: {gia.get('name')} {gia.get('url', '')}".strip()
    card = await _chiama(trello, "trelloWriteCard", {
        "action": "create",
        "listId": lista_id,
        "name": f"#{numero} · {titolo_itinerario} · {pacchetto} · {nome}",
        "desc": (
            f"**Richiesta n. {numero}** (da OnTheRoad AI, approvata dall'operatore)\n\n"
            f"- Itinerario: {titolo_itinerario}\n"
            f"- Pacchetto: {pacchetto} — €{prezzo}\n"
            f"- Cliente: {nome} <{email}>\n"
            f"- Messaggio: {messaggio or '—'}"
        ),
        "pos": "top",
    })
    return f"card creata: {card.get('name', prefisso)} {card.get('url', '')}".strip()


async def sincronizza() -> None:
    """Crea le card mancanti per tutte le richieste in richieste.db.

    Serve se Trello non era raggiungibile al momento dell'approvazione.
    Grazie all'idempotenza si può lanciare quante volte si vuole:
    le richieste che hanno già la card vengono saltate.
    """
    import sqlite3

    from strumenti import carica_itinerario

    if not CONFIG["richieste_db"].exists():
        print("  [trello] nessuna richiesta salvata")
        return
    con = sqlite3.connect(CONFIG["richieste_db"])
    righe = con.execute(
        "SELECT id, itinerary_id, package, prezzo_eur, name, email, message"
        " FROM richieste ORDER BY id"
    ).fetchall()
    con.close()
    async with server_trello() as trello:
        for numero, it_id, pacchetto, prezzo, nome, email, messaggio in righe:
            it = carica_itinerario(it_id)
            titolo = it.title if it else it_id
            esito = await crea_card_richiesta(
                trello, numero, titolo, pacchetto, prezzo, nome, email, messaggio
            )
            print(f"  [trello] n. {numero}: {esito}")


if __name__ == "__main__":
    import sys

    # Prova della connessione: login (solo la prima volta), tool, chi sono, board e lista.
    async def prova() -> None:
        async with server_trello() as trello:
            tools = await trello.list_tools()
            print(f"  [trello] {len(tools)} tool:", ", ".join(t.name for t in tools))
            io = json.loads(testo(await trello.call_tool("trelloReadMember", {"action": "get_me"})))
            print(f"  [trello] collegato come {io['fullName']} ({io['username']})")
            board_id, lista_id = await trova_lista(
                trello, CONFIG["trello_board"], CONFIG["trello_lista_nuove"]
            )
            print(f"  [trello] board '{CONFIG['trello_board']}', lista '{CONFIG['trello_lista_nuove']}': trovate")

    # python trello_mcp.py               → prova della connessione
    # python trello_mcp.py sincronizza   → card mancanti per le richieste salvate
    asyncio.run(sincronizza() if sys.argv[1:] == ["sincronizza"] else prova())
