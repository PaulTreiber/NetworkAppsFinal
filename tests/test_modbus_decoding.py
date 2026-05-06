from ref620_modbus_client.modbus import decode_registers
from ref620_modbus_client.points import PointDefinition
from ref620_modbus_client.setting_group import decode_group_from_ssr2


def test_decodes_unsigned_16_bit_scaled_value():
    point = PointDefinition("frequency", 2378, "u16", scale_factor=100)

    assert decode_registers(point, [6000]) == 60.0


def test_decodes_signed_16_bit_scaled_value():
    point = PointDefinition("power_factor", 2388, "s16", scale_factor=100)

    assert decode_registers(point, [0xFF9C]) == -1.0


def test_decodes_signed_32_bit_high_word_first():
    point = PointDefinition("ia_current", 2000, "s32", register_count=2, scale_factor=100)

    assert decode_registers(point, [0x0001, 0x86A0]) == 1000.0


def test_decodes_negative_signed_32_bit_high_word_first():
    point = PointDefinition("active_power", 2393, "s32", register_count=2, scale_factor=100)

    assert decode_registers(point, [0xFFFF, 0xFC18]) == -10.0


def test_decodes_bit_point():
    point = PointDefinition("cb_closed", 320, "bit", bit=12)

    assert decode_registers(point, [0b0001000000000000]) == 1.0


def test_decodes_setting_group_from_ssr2_bits():
    assert decode_group_from_ssr2(0b0000000000011000) == 3


def test_rejects_invalid_setting_group_from_ssr2_bits():
    assert decode_group_from_ssr2(0) is None
