import asyncio
import logging
import time
from django.core.management.base import BaseCommand
from crm_integration.api_clients.token_providers import MicrosoftTokenProvider

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Test token generation by calling the token API directly and printing detailed logs.'

    def handle(self, *args, **options):
        asyncio.run(self._run())

    async def _run(self):
        self.stdout.write(self.style.SUCCESS('=== Token API Test ==='))
        provider = MicrosoftTokenProvider()
        self.stdout.write(f'Token Provider: {type(provider).__name__}')
        self.stdout.write('---')

        start = time.monotonic()
        try:
            token = await provider.get_token()
            elapsed = time.monotonic() - start
            self.stdout.write(self.style.SUCCESS(f'Execution time: {elapsed:.3f}s'))
            self.stdout.write(self.style.SUCCESS(f'Token obtained: {token[:50]}...'))
        except Exception as ex:
            elapsed = time.monotonic() - start
            self.stdout.write(self.style.ERROR(f'Execution time: {elapsed:.3f}s'))
            self.stdout.write(self.style.ERROR(f'Exception: {type(ex).__name__}: {str(ex)}'))
            import traceback
            self.stdout.write(self.style.ERROR(traceback.format_exc()))
