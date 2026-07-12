import asyncio
import logging
from typing import Optional

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

class SyncleoUdpClient:
    """Асинхронный клиент для отправки/получения UDP пакетов."""

    @staticmethod
    async def async_send_and_receive(
        ip: str, port: int, packet: bytes, timeout: float = 1.0
    ) -> Optional[bytes]:
        loop = asyncio.get_running_loop()
        future = loop.create_future()

        class _Protocol(asyncio.DatagramProtocol):
            def datagram_received(self, data, addr):
                if not future.done():
                    future.set_result(data)

            def error_received(self, exc):
                if not future.done():
                    future.set_exception(exc)

        try:
            transport, _ = await loop.create_datagram_endpoint(
                lambda: _Protocol(), remote_addr=(ip, port)
            )
            transport.sendto(packet)
            
            # Ждем ответа
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            _LOGGER.debug("UDP Error for %s:%d: %s", ip, port, e)
            return None
        finally:
            if 'transport' in locals():
                transport.close()