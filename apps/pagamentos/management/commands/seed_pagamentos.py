from django.core.management.base import BaseCommand
from apps.pagamentos.models import FormaPagamento

class Command(BaseCommand):
    help = 'Cria as formas de pagamento padrão (PIX, Cartão de Crédito, Cartão de Débito, Dinheiro)'

    def handle(self, *args, **kwargs):
        formas_padrao = [
            {'nome': 'PIX', 'tipo': FormaPagamento.TipoPagamento.PIX},
            {'nome': 'Cartão de Crédito', 'tipo': FormaPagamento.TipoPagamento.CARTAO_CREDITO},
            {'nome': 'Cartão de Débito', 'tipo': FormaPagamento.TipoPagamento.CARTAO_DEBITO},
            {'nome': 'Dinheiro', 'tipo': FormaPagamento.TipoPagamento.DINHEIRO},
        ]

        created_count = 0
        for forma in formas_padrao:
            obj, created = FormaPagamento.objects.get_or_create(
                nome=forma['nome'],
                defaults={'tipo': forma['tipo']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Forma de pagamento '{forma['nome']}' criada com sucesso!"))
                created_count += 1
            else:
                self.stdout.write(self.style.WARNING(f"Forma de pagamento '{forma['nome']}' já existe."))
        
        if created_count > 0:
            self.stdout.write(self.style.SUCCESS(f'Foram criadas {created_count} novas formas de pagamento.'))
        else:
            self.stdout.write(self.style.SUCCESS('Todas as formas de pagamento já estavam cadastradas.'))
