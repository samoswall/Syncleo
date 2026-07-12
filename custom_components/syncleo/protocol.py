import hashlib
import struct
from dataclasses import dataclass

from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

FRAME_ACK = 0
FRAME_CMD = 1
FRAME_NAK = 0xFF
CMD_HANDSHAKE = 0x00

CMD_NAMES = {
    0x00: "CMD_HANDSHAKE",
    0x01: "CMD_MODE",
    0x02: "CMD_TARGET_TEMPERATURE",
    0x03: "CMD_TARGET_TIME",
    0x04: "CMD_RECIPE_ID",
    0x05: "CMD_RECIPE_STEP",
    0x07: "CMD_ERROR",
    0x08: "CMD_JOYSTICK",
    0x09: "CMD_VOLUME",
    0x0A: "CMD_MAP_DATA",
    0x0B: "CMD_AMOUNT",
    0x0C: "CMD_GYROSCOPE",
    0x0D: "CMD_DELAY_START",
    0x0E: "CMD_MULTI_STEP",
    0x0F: "CMD_SPEED",
    0x10: "CMD_KEEP_WARM",
    0x11: "CMD_PRESSURE",
    0x12: "CMD_TARGET_HUMIDITY",
    0x13: "CMD_CURRENT_HUMIDITY",
    0x14: "CMD_CURRENT_TEMPERATURE",
    0x15: "CMD_MULTI_STEP_CURRENT",
    0x16: "CMD_CURRENT_CO2",
    0x18: "CMD_IONIZATION",
    0x19: "CMD_WARM_STREAM",
    0x1A: "CMD_TOTAL_TIME",
    0x1B: "CMD_BATTERY",
    0x1C: "CMD_BACKLIGHT",
    0x1D: "CMD_BATTERY_STATE",
    0x1E: "CMD_CHILD_LOCK",
    0x1F: "CMD_TANK",
    0x20: "CMD_CURRENT_PM2",
    0x21: "CMD_ULTRAVIOLET",
    0x22: "CMD_EXPENDABLES",
    0x23: "CMD_CLEAN_TIME",
    0x24: "CMD_CLEAN_AREA",
    0x26: "CMD_DAMPER",
    0x28: "CMD_SMART_MODE",
    0x29: "CMD_BSS",
    0x2A: "CMD_SMART_BUTTON",
    0x2B: "CMD_WEIGHT",
    0x31: "CMD_TURBO",
    0x32: "CMD_NIGHT",
    0x34: "CMD_CURRENT_POWER",
    0x40: "CMD_SCHEDULE_SET",
    0x41: "CMD_SCHEDULE_REMOVE",
    0x42: "CMD_PROGRAM_DATA",
    0x43: "CMD_MAP_TARGET",
    0x44: "CMD_CONTOUR",
    0x45: "CMD_FINDME",
    0x46: "CMD_VIRTUAL_WALL",
    0x47: "CMD_MAP_ANGLE",
    0x48: "CMD_MAP_LASER",
    0x49: "CMD_MAP_EDIT_ENABLED",
    0x4A: "CMD_MAP_NO_GO_AREA",
    0x4B: "CMD_MAP_GO_AREA",
    0x4C: "CMD_MAP_ROOMS",
    0x50: "CMD_UPDATE_USER",
    0x51: "CMD_GET_USER_LIST",
    0x80: "CMD_TIME_SYNC",
    0x81: "CMD_WIFI_LIST",
    0x82: "CMD_WIFI_CONFIGURATION",
    0x83: "CMD_CROSS_CONFIG",
    0x85: "CMD_ACCESS_CONTROL",
    0x87: "CMD_OPEN_MQTT",
    0x89: "CMD_DEVICE_TYPE",
    0x8D: "CMD_DIAGNOSTICS",
    0x8F: "CMD_HARDWARE",
    0x90: "CMD_TARGET_ID",
    0x91: "CMD_DEVICE_DIAGNOSTICS",
    0xF0: "CMD_INTERNAL_LOGS",
    0xFD: "CMD_UDP_FIRMWARE",
    0xFE: "CMD_UDP_FIRMWARE_V2",
    0xFF: "CMD_PING",
}

def rev(data: bytes) -> bytes:
    """Реверс байтов (Little-Endian)."""
    return data[::-1]

def pkcs7_pad(data: bytes, block_size: int = 16) -> bytes:
    pad = block_size - (len(data) % block_size)
    return data + bytes([pad]) * pad

def pkcs7_unpad(data: bytes, block_size: int = 16) -> bytes:
    if not data or len(data) % block_size:
        raise ValueError("invalid PKCS7 data length")
    pad = data[-1]
    if pad < 1 or pad > block_size or data[-pad:] != bytes([pad]) * pad:
        raise ValueError("invalid PKCS7 padding")
    return data[:-pad]

def aes_cbc_encrypt(key: bytes, iv: bytes, data: bytes, *, pad: bool) -> bytes:
    if pad:
        data = pkcs7_pad(data)
    elif len(data) % 16:
        raise ValueError("AES/CBC/NoPadding data length must be a multiple of 16")
    enc = Cipher(algorithms.AES(key), modes.CBC(iv)).encryptor()
    return enc.update(data) + enc.finalize()

def aes_cbc_decrypt(key: bytes, iv: bytes, data: bytes, *, unpad: bool) -> bytes:
    dec = Cipher(algorithms.AES(key), modes.CBC(iv)).decryptor()
    out = dec.update(data) + dec.finalize()
    return pkcs7_unpad(out) if unpad else out

def rotate_left(data: bytes, count: int) -> bytes:
    count %= len(data)
    return data[count:] + data[:count]

@dataclass
class SessionKeys:
    tx_iv_base: bytes
    tx_key_base: bytes

    @property
    def rx_key_base(self) -> bytes:
        return self.tx_iv_base  # ВНИМАНИЕ: ключи приема и передачи переставлены местами!

    @property
    def rx_iv_base(self) -> bytes:
        return self.tx_key_base

    def tx_key_iv(self, seq: int) -> tuple[bytes, bytes]:
        return rotate_left(self.tx_key_base, seq & 0x0F), rotate_left(
            self.tx_iv_base, (seq >> 4) & 0x0F
        )

    def rx_key_iv(self, seq: int) -> tuple[bytes, bytes]:
        return rotate_left(self.rx_key_base, seq & 0x0F), rotate_left(
            self.rx_iv_base, (seq >> 4) & 0x0F
        )

def make_x25519_keys(peer_public_reversed_hex: str) -> tuple[bytes, SessionKeys]:
    """Генерация ключей сессии на основе публичного ключа устройства (в hex, реверсном формате)."""
    peer_public = rev(bytes.fromhex(peer_public_reversed_hex))
    private = x25519.X25519PrivateKey.generate()
    public = private.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    shared = private.exchange(x25519.X25519PublicKey.from_public_bytes(peer_public))
    digest = hashlib.sha256(rev(shared)).digest()
    
    # Возвращаем реверсный публичный ключ телефона и ключи сессии
    return rev(public), SessionKeys(tx_iv_base=digest[:16], tx_key_base=digest[16:])

def build_frame(seq: int, frame_type: int, payload: bytes) -> bytes:
    return (
        bytes([seq & 0xFF, frame_type & 0xFF])
        + struct.pack("<H", len(payload))
        + payload
    )

def parse_frame(data: bytes) -> tuple[int, int, bytes] | None:
    if len(data) < 4:
        return None
    seq = data[0]
    frame_type = data[1]
    size = struct.unpack("<H", data[2:4])[0]
    if len(data) != size + 4:
        return None
    return seq, frame_type, data[4:]

def build_encrypted_cmd_frame(seq: int, cmd: int, payload: bytes, keys: SessionKeys) -> bytes:
    plain = bytes([cmd & 0xFF]) + payload
    key, iv = keys.tx_key_iv(seq)
    encrypted = aes_cbc_encrypt(key, iv, bytes([seq & 0xFF]) + plain, pad=True)
    return build_frame(seq, FRAME_CMD, encrypted)

def build_encrypted_ack_frame(seq: int, keys: SessionKeys) -> bytes:
    key, iv = keys.tx_key_iv(seq)
    encrypted = aes_cbc_encrypt(key, iv, bytes([seq & 0xFF]), pad=True)
    return build_frame(seq, FRAME_ACK, encrypted)

def decrypt_frame_payload(seq: int, payload: bytes, keys: SessionKeys) -> bytes:
    key, iv = keys.rx_key_iv(seq)
    plain = aes_cbc_decrypt(key, iv, payload, unpad=True)
    if not plain or plain[0] != (seq & 0xFF):
        raise ValueError("decrypted frame sequence mismatch")
    return plain[1:] # Отрезаем первый байт (seq)



@dataclass
class HandshakeResponseMessage:
    """Стандартное сообщение ответа на Handshake из SDK Syncleo."""
    TYPE = 0
    protocol: int
    fw_major: int
    fw_minor: int
    mode: int
    token: bytes
    seq: Optional[int] = None

    @classmethod
    def from_packed_data(cls, data: bytes, seq: int = 0) -> "HandshakeResponseMessage":
        if len(data) < 5:
            raise ValueError("Too short for HandshakeResponse")
        protocol, fw_major, fw_minor, mode = struct.unpack('<HBBB', data[:5])
        token = data[5:21] if len(data) >= 21 else data[5:]
        return cls(protocol, fw_major, fw_minor, mode, token, seq)






