import urllib.request
import json
from datetime import date, timedelta

amanha = date.today() + timedelta(days=1)
url = f"http://localhost:8000/api/v1/agendamentos/disponibilidade/?data={amanha.isoformat()}&servico_id=1"
print("GET", url)
try:
    req = urllib.request.Request(url)
    # The API might need authentication, wait! IsAuthenticated is on AgendamentoViewSet?
    # Yes, read the views:
    #     @action(detail=False, methods=['get'], url_path='disponibilidade')
    #     def disponibilidade(self, request):
    # This requires a token.
    print("Requires auth, let's login first")
except Exception as e:
    print(e)
